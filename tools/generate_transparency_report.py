#!/usr/bin/env python3
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from haltseal_eval.canonicalization import contextual_sha256, load_json, write_json
from haltseal_eval.constants import REPORT_CONTEXT, VERSION
from haltseal_eval.synthetic_crypto import signature_block


def main() -> int:
    qa_path = ROOT / "QA_RESULTS.json"
    if not qa_path.exists():
        print("transparency report: FAIL - QA_RESULTS.json missing; run tools/run_public_eval.py first")
        return 1
    qa = load_json(qa_path)
    rows = qa.get("rows", [])
    dispositions = Counter(row.get("actual", {}).get("disposition") for row in rows)
    stages = Counter(row.get("actual", {}).get("stage") for row in rows)
    result_codes = Counter(row.get("actual", {}).get("result_code") for row in rows)
    report = {
        "context_label": REPORT_CONTEXT,
        "artifact": "HALTSEAL Gateway Proof Pack",
        "version": VERSION,
        "reporting_period": "synthetic-public-eval-2026-07-04",
        "privacy_posture": "aggregated counts only; no per-subject data; synthetic vectors only",
        "total_vectors": qa.get("total"),
        "passed_vectors": qa.get("passed"),
        "failed_vectors": qa.get("failed"),
        "disposition_counts": dict(sorted((k, v) for k, v in dispositions.items() if k)),
        "stage_counts": dict(sorted((k, v) for k, v in stages.items() if k)),
        "result_code_counts": dict(sorted((k, v) for k, v in result_codes.items() if k)),
        "public_boundary": "synthetic evaluation only; no production SDK; no patent license",
    }
    report["report_hash"] = contextual_sha256(REPORT_CONTEXT, report)
    report["report_sig"] = signature_block(REPORT_CONTEXT, report)
    write_json(ROOT / "attestations" / "privacy_preserving_transparency_report.json", report)
    print("transparency report: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
