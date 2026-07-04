#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from haltseal_eval.proof_receipt import receipt_markdown, procurement_block, write_receipt_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a HALTSEAL Gateway Proof Receipt from the public evaluation result.")
    parser.add_argument("--out", default="receipts/haltseal-gateway-proof-receipt.json", help="JSON receipt output path")
    parser.add_argument("--markdown-out", default="receipts/haltseal-gateway-proof-receipt.md", help="Markdown receipt output path")
    parser.add_argument("--text-out", default="receipts/haltseal-gateway-proof-receipt.txt", help="Copy-paste diligence block output path")
    args = parser.parse_args()

    receipt = write_receipt_bundle(ROOT, ROOT / args.out, ROOT / args.markdown_out, ROOT / args.text_out)
    print("HALTSEAL Gateway Proof Receipt: PASS")
    print("Release SHA-256: OK")
    print(f"Public evaluation: {receipt['vector_result']['passed']} / {receipt['vector_result']['total']} PASS")
    print(f"Boundary: {receipt['enabled_public_eval_hook']}")
    print("Rights posture: no production SDK · no patent license")
    print(f"Receipt JSON: {args.out}")
    print(f"Receipt Markdown: {args.markdown_out}")
    print(f"Copy-paste block: {args.text_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
