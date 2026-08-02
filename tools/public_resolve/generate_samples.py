from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from haltseal_resolve.constants import BOUNDARY, SAMPLE_KID, SAMPLE_SEED_LABEL
from haltseal_resolve.jws import deterministic_private_key, public_jwk
from haltseal_resolve.profiles import profile_state
from haltseal_resolve.receipt import build_receipt_payload, sign_receipt
from haltseal_resolve.semantics import evaluate_action

OUT = ROOT / "examples" / "receipts"
OUT.mkdir(parents=True, exist_ok=True)
key = deterministic_private_key(SAMPLE_SEED_LABEL)
jwks = {"keys": [public_jwk(key, SAMPLE_KID)]}
(ROOT / "keys" / "sample-evaluation-jwks.json").write_text(json.dumps(jwks, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def make(name, *, profile, action, outcome_unknown=False, consumed=False, existing=None, receipt_id, request_id=None):
    state = profile_state(profile)
    authority = state["authority"]
    sem = evaluate_action(authority, action, outcome_unknown=outcome_unknown, already_consumed=consumed)
    if sem.decision == "ACCEPT":
        emission = {"disposition":"ONE_SYNTHETIC_REQUEST","synthetic_request_record_id":request_id,"existing_request_record_id":None,"new_request_count":1,"total_request_count_for_use":1,"outcome":"RECORDED"}
        consumption = {"state_before":"AVAILABLE","state_after":"CONSUMED"}
    elif sem.decision == "HOLD":
        emission = {"disposition":"NO_NEW_REQUEST","synthetic_request_record_id":None,"existing_request_record_id":existing,"new_request_count":0,"total_request_count_for_use":1,"outcome":"UNKNOWN"}
        consumption = {"state_before":"CONSUMED","state_after":"CONSUMED"}
    else:
        before = "CONSUMED" if consumed or authority["remaining_uses"] == 0 else "AVAILABLE"
        emission = {"disposition":"NO_REQUEST","synthetic_request_record_id":None,"existing_request_record_id":None,"new_request_count":0,"total_request_count_for_use":1 if before=="CONSUMED" else 0,"outcome":"NONE"}
        consumption = {"state_before":before,"state_after":before}
    payload = build_receipt_payload(receipt_id=receipt_id,issued_at=1785600000,challenge_id="hsc_sample_fixed_000000000001",authority=authority,action=action,decision=sem.decision,reason_codes=list(sem.reason_codes),emission=emission,consumption=consumption)
    token = sign_receipt(payload,key,kid=SAMPLE_KID)
    response={"decision":sem.decision,"reason_codes":list(sem.reason_codes),"action_digest":payload["action_digest"],"authority_digest":payload["authority_digest"],"emission":emission,"receipt":{"receipt_id":receipt_id,"jws":token,"sha256":"sha256:"+hashlib.sha256(token.encode('ascii')).hexdigest()},"boundary":BOUNDARY}
    (OUT/f"{name}.receipt.jws").write_text(token+"\n",encoding="utf-8")
    (OUT/f"{name}.receipt-payload.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (OUT/f"{name}.resolve-response.json").write_text(json.dumps(response,indent=2,sort_keys=True)+"\n",encoding="utf-8")

exact={"amount_minor":25000,"currency":"USD","merchant_id":"merchant_synthetic_alpha","terms":"ONE_TIME","destination_id":"account_synthetic_a"}
changed_terms=dict(exact); changed_terms["terms"]="RECURRING_MONTHLY"
make("accept-exact",profile="payment.one-time-purchase.v1",action=exact,receipt_id="hsr_sample_accept_000000000001",request_id="hsreq_sample_accept_0000000001")
make("refuse-changed-terms",profile="payment.one-time-purchase.v1",action=changed_terms,receipt_id="hsr_sample_refuse_00000000001")
make("hold-outcome-unknown",profile="payment.outcome-unknown.v1",action=exact,outcome_unknown=True,consumed=True,existing="hsreq_sample_existing_unknown",receipt_id="hsr_sample_hold_0000000000001")
make("refuse-consumed-use",profile="payment.one-time-purchase.v1",action=exact,consumed=True,receipt_id="hsr_sample_consumed_000000001")
print("generated sample JWKS and receipts")
