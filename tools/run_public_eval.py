#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from haltseal_eval.canonicalization import load_json, write_json
from haltseal_eval.verifier import verify_packet
from haltseal_eval.replay import ReplayCache


def run_vectors(vector_path: Path) -> dict:
    vectors = load_json(vector_path)
    rows = []
    passed = 0
    for packet in vectors:
        result = verify_packet(packet, ReplayCache())
        expected = packet["expected"]
        ok = all(result.get(k) == expected.get(k) for k in ("disposition", "result_code", "stage"))
        rows.append({
            "vector_id": packet["vector_id"],
            "title": packet.get("title", ""),
            "expected": expected,
            "actual": {"disposition": result["disposition"], "result_code": result["result_code"], "stage": result["stage"]},
            "pass": ok,
            "evidence_hash": result["evidence"]["evidence_hash"],
        })
        passed += 1 if ok else 0
    return {"total": len(rows), "passed": passed, "failed": len(rows) - passed, "rows": rows}


def main() -> int:
    vector_path = ROOT / "vectors" / "haltseal_gateway_vectors.json"
    report = run_vectors(vector_path)
    print("HALTSEAL Gateway Proof Pack — synthetic public evaluation")
    print()
    for row in report["rows"]:
        status = "PASS" if row["pass"] else "FAIL"
        actual = row["actual"]
        print(f"{row['vector_id']:<50} {actual['disposition']:<5} stage={actual['stage']:<22} code={actual['result_code']:<34} {status}")
    print()
    print(f"Result: {report['passed']} / {report['total']} PASS")
    print("Public boundary: synthetic evaluation only; no production SDK; no patent license.")
    write_json(ROOT / "QA_RESULTS.json", report)
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
