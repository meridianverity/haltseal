#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from haltseal_eval.canonicalization import load_json
from haltseal_eval.proof_receipt import verify_proof_receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a HALTSEAL Gateway Proof Receipt.")
    parser.add_argument("receipt", nargs="?", default="receipts/haltseal-gateway-proof-receipt.json")
    args = parser.parse_args()

    receipt_path = ROOT / args.receipt if not Path(args.receipt).is_absolute() else Path(args.receipt)
    receipt = load_json(receipt_path)
    schema = load_json(ROOT / "schemas" / "haltseal_gateway_proof_receipt.schema.json")
    schema_errors = sorted(Draft202012Validator(schema).iter_errors(receipt), key=lambda e: list(e.absolute_path))
    findings = ["/".join(str(p) for p in e.absolute_path) + f": {e.message}" for e in schema_errors]
    findings += verify_proof_receipt(receipt, ROOT)

    if findings:
        print("HALTSEAL Gateway Proof Receipt: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("HALTSEAL Gateway Proof Receipt: PASS")
    print("Release SHA-256: OK")
    print(f"Public evaluation: {receipt['vector_result']['passed']} / {receipt['vector_result']['total']} PASS")
    print(f"Boundary: {receipt['enabled_public_eval_hook']}")
    print("Rights posture: no production SDK · no patent license")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
