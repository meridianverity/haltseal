#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from haltseal_resolve.constants import SAMPLE_KID, SAMPLE_SEED_LABEL
from haltseal_resolve.jws import deterministic_private_key, unb64u
from haltseal_resolve.mock_engine import MockEngine
from haltseal_resolve.receipt import sign_receipt
from haltseal_resolve.strict_json import loads
from haltseal_resolve.verifier import ReceiptVerificationError, verify_receipt

REGISTRY = ROOT / "vectors/public-resolve/verifier-parity-v1.json"
OUT = ROOT / "release/v0.4.0/VERIFIER_PARITY_QA_RESULTS.json"
EXACT = {
    "amount_minor": 25000,
    "currency": "USD",
    "merchant_id": "merchant_synthetic_alpha",
    "terms": "ONE_TIME",
    "destination_id": "account_synthetic_a",
}


def fixture():
    engine = MockEngine(now=lambda: 1785600000)
    challenge = engine.create_challenge("payment.one-time-purchase.v1")
    response, _ = engine.resolve(
        challenge_token=challenge["challenge_token"],
        action=EXACT,
        idempotency_key="verifier-parity-fixture-0001",
    )
    token = response["receipt"]["jws"]
    payload = loads(unb64u(token.split(".")[1]), require_object=True)
    return engine, payload, token


def mutate(name: str, payload: dict, canonical_token: str) -> str:
    key = deterministic_private_key(SAMPLE_SEED_LABEL)
    p = copy.deepcopy(payload)
    if name == "none":
        return canonical_token
    if name == "wrong_issuer": p["iss"] = "https://evil.invalid"
    elif name == "wrong_audience": p["aud"] = "wrong-audience"
    elif name == "wrong_profile": p["profile_version"] = "attacker-profile"
    elif name == "live_provider": p["boundary"]["live_provider_call"] = True
    elif name == "credentials_accepted": p["boundary"]["payment_credentials_accepted"] = True
    elif name == "accept_unknown": p["emission"]["outcome"] = "UNKNOWN"
    elif name == "accept_existing": p["emission"]["existing_request_record_id"] = "hsreq_sample_12345678"
    elif name == "new_count_999": p["emission"]["new_request_count"] = 999
    elif name == "total_count_999": p["emission"]["total_request_count_for_use"] = 999
    elif name == "empty_jti": p["jti"] = ""
    elif name == "string_iat": p["iat"] = "1785600000"
    elif name == "integer_challenge": p["challenge_id"] = 123
    elif name == "duplicate_reason": p["reason_codes"] = p["reason_codes"] + [p["reason_codes"][0]]
    elif name == "unknown_emission": p["emission"]["provider_request_id"] = "pay_attacker"
    elif name == "unknown_action": p["action"]["callback_url"] = "https://evil.invalid"
    elif name == "string_amount": p["action"]["amount_minor"] = "25000"
    elif name == "boundary_extra": p["boundary"]["certified"] = True
    elif name in {"signature_padding", "standard_base64_signature"}:
        token = canonical_token
        h, body, sig = token.split(".")
        if name == "signature_padding":
            return f"{h}.{body}.{sig}="
        if "-" not in sig and "_" not in sig:
            for i in range(256):
                candidate_payload = copy.deepcopy(payload)
                candidate_payload["jti"] = f"hsr_sample_{i:024x}"
                candidate = sign_receipt(candidate_payload, key, kid=SAMPLE_KID)
                h, body, sig = candidate.split(".")
                if "-" in sig or "_" in sig:
                    break
            else:
                raise RuntimeError("could not generate signature with base64url-only character")
        return f"{h}.{body}.{sig.replace('-', '+').replace('_', '/')}"
    else:
        raise ValueError(f"unknown mutation {name}")
    return sign_receipt(p, key, kid=SAMPLE_KID)


def python_result(token: str, jwks: dict) -> str:
    try:
        verify_receipt(token, jwks)
        return "PASS"
    except ReceiptVerificationError:
        return "FAIL"


def typescript_result(token: str, jwks: dict) -> tuple[str, str]:
    with tempfile.TemporaryDirectory() as td:
        receipt = Path(td) / "receipt.jws"
        keys = Path(td) / "jwks.json"
        receipt.write_text(token, encoding="utf-8")
        keys.write_text(json.dumps(jwks), encoding="utf-8")
        proc = subprocess.run(
            ["node", str(ROOT / "verifier/typescript/haltseal_verify.mjs"), str(receipt), str(keys)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return ("PASS" if proc.returncode == 0 else "FAIL"), proc.stdout.strip()


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    engine, payload, canonical_token = fixture()
    rows = []
    for case in registry["cases"]:
        token = mutate(case["mutation"], payload, canonical_token)
        py = python_result(token, engine.jwks)
        ts, detail = typescript_result(token, engine.jwks)
        ok = py == case["expected"] and ts == case["expected"] and py == ts
        rows.append({
            "id": case["id"],
            "mutation": case["mutation"],
            "expected": case["expected"],
            "python": py,
            "typescript": ts,
            "pass": ok,
            "typescript_detail": detail if not ok else None,
        })
    summary = {
        "release": "v0.4.0-public-resolve-challenge",
        "registry": registry["registry"],
        "cases": len(rows),
        "passed": sum(row["pass"] for row in rows),
        "failed": sum(not row["pass"] for row in rows),
        "python_typescript_parity": all(row["python"] == row["typescript"] for row in rows),
        "results": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"receipt verifier parity: {summary['passed']} / {summary['cases']} PASS")
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
