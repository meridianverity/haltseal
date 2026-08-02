from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from haltseal_resolve.canonical import action_digest
from haltseal_resolve.mock_engine import MockEngine
from haltseal_resolve.strict_json import StrictJSONError, loads
from haltseal_resolve.verifier import ReceiptVerificationError, verify_receipt

ROOT = Path(__file__).resolve().parents[1]
EXACT = {"amount_minor":25000,"currency":"USD","merchant_id":"merchant_synthetic_alpha","terms":"ONE_TIME","destination_id":"account_synthetic_a"}

def test_strict_json_rejects_duplicate_and_nonfinite():
    with pytest.raises(StrictJSONError): loads('{"amount_minor":999999,"amount_minor":25000}', require_object=True)
    for raw in ('{"x":NaN}','{"x":Infinity}','{"x":1e400}'):
        with pytest.raises(StrictJSONError): loads(raw, require_object=True)

def test_exact_accept_and_offline_verify():
    engine=MockEngine(now=lambda:1785600000); ch=engine.create_challenge("payment.one-time-purchase.v1")
    response,replayed=engine.resolve(challenge_token=ch["challenge_token"],action=EXACT,idempotency_key="idem-public-test-0001")
    assert not replayed and response["decision"]=="ACCEPT"
    assert response["emission"]["new_request_count"]==1
    result=verify_receipt(response["receipt"]["jws"],engine.jwks)
    assert result["semantic_replay"]=="PASS"

def test_changed_terms_refuses_without_consuming():
    engine=MockEngine(now=lambda:1785600000); ch=engine.create_challenge("payment.one-time-purchase.v1")
    changed=dict(EXACT,terms="RECURRING_MONTHLY")
    r,_=engine.resolve(challenge_token=ch["challenge_token"],action=changed,idempotency_key="idem-public-test-0002")
    assert r["decision"]=="REFUSE" and r["emission"]["new_request_count"]==0
    accepted,_=engine.resolve(challenge_token=ch["challenge_token"],action=EXACT,idempotency_key="idem-public-test-0003")
    assert accepted["decision"]=="ACCEPT"

def test_outcome_unknown_holds_no_new_request():
    engine=MockEngine(now=lambda:1785600000); ch=engine.create_challenge("payment.outcome-unknown.v1")
    r,_=engine.resolve(challenge_token=ch["challenge_token"],action=EXACT,idempotency_key="idem-public-test-0004")
    assert r["decision"]=="HOLD" and r["emission"]["disposition"]=="NO_NEW_REQUEST"
    assert r["emission"]["new_request_count"]==0

def test_same_transport_retry_returns_same_receipt():
    engine=MockEngine(now=lambda:1785600000); ch=engine.create_challenge("payment.one-time-purchase.v1")
    a,replay1=engine.resolve(challenge_token=ch["challenge_token"],action=EXACT,idempotency_key="idem-public-test-0005")
    b,replay2=engine.resolve(challenge_token=ch["challenge_token"],action=EXACT,idempotency_key="idem-public-test-0005")
    assert not replay1 and replay2 and a==b

def test_new_economic_use_after_consumption_refuses():
    engine=MockEngine(now=lambda:1785600000); ch=engine.create_challenge("payment.one-time-purchase.v1")
    a,_=engine.resolve(challenge_token=ch["challenge_token"],action=EXACT,idempotency_key="idem-public-test-0006")
    b,_=engine.resolve(challenge_token=ch["challenge_token"],action=EXACT,idempotency_key="idem-public-test-0007")
    assert a["decision"]=="ACCEPT" and b["decision"]=="REFUSE"
    assert b["reason_codes"]==["AUTHORIZED_USE_ALREADY_CONSUMED"] and b["emission"]["new_request_count"]==0

def test_64_concurrent_calls_create_one_accept():
    engine=MockEngine(now=lambda:1785600000); ch=engine.create_challenge("payment.one-time-purchase.v1")
    def call(i): return engine.resolve(challenge_token=ch["challenge_token"],action=EXACT,idempotency_key=f"idem-concurrency-{i:04d}")[0]
    with ThreadPoolExecutor(max_workers=32) as pool: results=list(pool.map(call,range(64)))
    assert sum(r["decision"]=="ACCEPT" for r in results)==1
    assert sum(r["emission"]["new_request_count"] for r in results)==1

def test_idempotency_key_conflict_fails():
    engine=MockEngine(now=lambda:1785600000); ch=engine.create_challenge("payment.one-time-purchase.v1")
    engine.resolve(challenge_token=ch["challenge_token"],action=dict(EXACT,terms="RECURRING_MONTHLY"),idempotency_key="idem-public-test-0008")
    with pytest.raises(ValueError): engine.resolve(challenge_token=ch["challenge_token"],action=EXACT,idempotency_key="idem-public-test-0008")

def test_tampered_receipt_fails():
    token=(ROOT/'examples/receipts/accept-exact.receipt.jws').read_text().strip(); jwks=json.loads((ROOT/'keys/sample-evaluation-jwks.json').read_text())
    parts=token.split('.'); parts[1]=parts[1][:-1]+('A' if parts[1][-1]!='A' else 'B')
    with pytest.raises(ReceiptVerificationError): verify_receipt('.'.join(parts),jwks)

def test_public_schemas_are_closed_and_valid():
    for path in sorted((ROOT/'schemas/public-resolve').glob('*.json')):
        schema=json.loads(path.read_text()); Draft202012Validator.check_schema(schema)
        assert schema.get('additionalProperties') is False or path.name in {'receipt-payload-v1.json'}

def test_public_source_has_no_provider_egress_libraries():
    text='\n'.join(p.read_text(errors='ignore') for p in (ROOT/'haltseal_resolve').glob('*.py'))
    for forbidden in ('requests.', 'httpx.', 'aiohttp.', 'boto3.', 'stripe.', 'checkout_sdk'):
        assert forbidden not in text

# v0.4.0 verifier-parity and HTTP-contract closure
import copy
import contextlib
import http.client
import subprocess
import tempfile
import threading
from http.server import ThreadingHTTPServer

from haltseal_resolve.constants import SAMPLE_KID, SAMPLE_SEED_LABEL
from haltseal_resolve.jws import deterministic_private_key, sign, unb64u
from haltseal_resolve.receipt import sign_receipt
from haltseal_resolve.strict_json import loads as strict_loads


def _canonical_accept_fixture():
    engine=MockEngine(now=lambda:1785600000)
    challenge=engine.create_challenge("payment.one-time-purchase.v1")
    response,_=engine.resolve(challenge_token=challenge["challenge_token"],action=EXACT,idempotency_key="idem-parity-fixture-0001")
    payload=strict_loads(unb64u(response["receipt"]["jws"].split(".")[1]),require_object=True)
    return engine,payload,response["receipt"]["jws"]


def _node_accepts(token,jwks):
    with tempfile.TemporaryDirectory() as td:
        token_path=Path(td)/"receipt.jws"; jwks_path=Path(td)/"jwks.json"
        token_path.write_text(token,encoding="utf-8")
        jwks_path.write_text(json.dumps(jwks),encoding="utf-8")
        proc=subprocess.run(
            ["node",str(ROOT/"verifier/typescript/haltseal_verify.mjs"),str(token_path),str(jwks_path)],
            cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,
        )
        return proc.returncode==0, proc.stdout+proc.stderr


def _python_accepts(token,jwks):
    try:
        verify_receipt(token,jwks)
        return True
    except ReceiptVerificationError:
        return False


@pytest.mark.parametrize("label,mutator",[
    ("wrong-issuer",lambda p:p.__setitem__("iss","https://evil.invalid")),
    ("wrong-audience",lambda p:p.__setitem__("aud","wrong-audience")),
    ("wrong-profile-version",lambda p:p.__setitem__("profile_version","attacker-profile")),
    ("live-provider-boundary",lambda p:p["boundary"].__setitem__("live_provider_call",True)),
    ("credentials-accepted-boundary",lambda p:p["boundary"].__setitem__("payment_credentials_accepted",True)),
    ("accept-unknown-outcome",lambda p:p["emission"].__setitem__("outcome","UNKNOWN")),
    ("accept-existing-request",lambda p:p["emission"].__setitem__("existing_request_record_id","hsreq_sample_12345678")),
    ("accept-new-count-999",lambda p:p["emission"].__setitem__("new_request_count",999)),
    ("accept-total-count-999",lambda p:p["emission"].__setitem__("total_request_count_for_use",999)),
    ("empty-jti",lambda p:p.__setitem__("jti","")),
    ("string-iat",lambda p:p.__setitem__("iat","1785600000")),
    ("integer-challenge-id",lambda p:p.__setitem__("challenge_id",123)),
    ("duplicate-reason",lambda p:p.__setitem__("reason_codes",p["reason_codes"]+[p["reason_codes"][0]])),
    ("unknown-emission-field",lambda p:p["emission"].__setitem__("provider_request_id","pay_attacker")),
    ("unknown-action-field",lambda p:p["action"].__setitem__("callback_url","https://evil.invalid")),
    ("string-amount",lambda p:p["action"].__setitem__("amount_minor","25000")),
    ("boundary-extra-field",lambda p:p["boundary"].__setitem__("certified",True)),
])
def test_python_and_typescript_reject_same_malformed_signed_receipts(label,mutator):
    engine,payload,_=_canonical_accept_fixture(); key=deterministic_private_key(SAMPLE_SEED_LABEL)
    malformed=copy.deepcopy(payload); mutator(malformed)
    token=sign_receipt(malformed,key,kid=SAMPLE_KID)
    py=_python_accepts(token,engine.jwks); ts,detail=_node_accepts(token,engine.jwks)
    assert py is False, label
    assert ts is False, f"{label}: {detail}"


def test_python_and_typescript_accept_same_canonical_receipt():
    engine,_,token=_canonical_accept_fixture()
    assert _python_accepts(token,engine.jwks)
    accepted,detail=_node_accepts(token,engine.jwks)
    assert accepted,detail


@pytest.mark.parametrize("variant",["signature-padding","standard-base64-signature"])
def test_python_and_typescript_reject_noncanonical_compact_jws(variant):
    engine,_,token=_canonical_accept_fixture(); h,p,s=token.split(".")
    if variant=="signature-padding":
        mutated=f"{h}.{p}.{s}="
    else:
        if "-" not in s and "_" not in s:
            key=deterministic_private_key(SAMPLE_SEED_LABEL)
            _,payload,_=_canonical_accept_fixture()
            for i in range(256):
                payload["jti"]=f"hsr_sample_{i:024x}"
                candidate=sign_receipt(payload,key,kid=SAMPLE_KID)
                h,p,s=candidate.split(".")
                if "-" in s or "_" in s:
                    break
            else:
                raise AssertionError("could not produce base64url signature containing - or _")
        mutated=f"{h}.{p}.{s.replace('-', '+').replace('_', '/')}"
    assert not _python_accepts(mutated,engine.jwks)
    accepted,detail=_node_accepts(mutated,engine.jwks)
    assert not accepted,detail


@contextlib.contextmanager
def _http_server(engine):
    import haltseal_resolve.mock_server as mock_server
    prior=mock_server._ENGINE; mock_server._ENGINE=engine
    server=ThreadingHTTPServer(("127.0.0.1",0),mock_server.Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    try: yield server.server_address[1]
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=3); mock_server._ENGINE=prior


def _http_post(port,path,payload,headers=None):
    body=json.dumps(payload,separators=(",",":")).encode("utf-8")
    conn=http.client.HTTPConnection("127.0.0.1",port,timeout=5)
    conn.request("POST",path,body=body,headers={"Content-Type":"application/json",**(headers or {})})
    response=conn.getresponse(); raw=response.read(); result=(response.status,response.getheader("Content-Type"),json.loads(raw)); conn.close(); return result


def test_local_http_mock_matches_openapi_idempotency_conflict_contract():
    engine=MockEngine(now=lambda:1785600000)
    with _http_server(engine) as port:
        _,_,challenge=_http_post(port,"/haltseal/evaluation/v1/challenges",{"profile":"payment.one-time-purchase.v1"})
        key="idem-http-contract-0001"
        changed=dict(EXACT,terms="RECURRING_MONTHLY")
        status,ctype,_=_http_post(port,"/haltseal/evaluation/v1/resolve",{"challenge_token":challenge["challenge_token"],"action":changed},{"Idempotency-Key":key})
        assert status==200 and ctype=="application/json"
        status,ctype,problem=_http_post(port,"/haltseal/evaluation/v1/resolve",{"challenge_token":challenge["challenge_token"],"action":EXACT},{"Idempotency-Key":key})
        assert status==409
        assert ctype=="application/problem+json"
        assert problem["title"]=="IDEMPOTENCY_KEY_CONFLICT" and problem["status"]==409


def test_local_http_mock_uses_problem_json_for_validation_and_fail_closed():
    engine=MockEngine(now=lambda:1785600000)
    with _http_server(engine) as port:
        status,ctype,problem=_http_post(port,"/haltseal/evaluation/v1/challenges",{"unexpected":True})
        assert status==400 and ctype=="application/problem+json" and problem["title"]=="INVALID_REQUEST"
    class BrokenEngine:
        @property
        def jwks(self): return {"keys":[]}
        def create_challenge(self,profile): raise RuntimeError("simulated failure")
    with _http_server(BrokenEngine()) as port:
        status,ctype,problem=_http_post(port,"/haltseal/evaluation/v1/challenges",{"profile":"payment.one-time-purchase.v1"})
        assert status==503 and ctype=="application/problem+json" and problem["title"]=="FAIL_CLOSED"
