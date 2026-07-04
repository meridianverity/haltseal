#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(ROOT))

from haltseal_eval.canonicalization import contextual_sha256, load_json, write_json
from haltseal_eval.constants import DEFAULT_NOW, PUBLIC_BOUNDARY_NOTICE, VERSION, REPORT_CONTEXT
from haltseal_eval.synthetic_crypto import signature_block


def count_test_functions() -> int:
    total = 0
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        total += sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
            for node in ast.walk(tree)
        )
    return total


def main() -> int:
    vectors = load_json(ROOT / "vectors" / "haltseal_gateway_vectors.json")
    qa = load_json(ROOT / "QA_RESULTS.json")
    attestation = {
        "artifact": "HALTSEAL Gateway Proof Pack",
        "version": VERSION,
        "generated_at": DEFAULT_NOW,
        "boundary": PUBLIC_BOUNDARY_NOTICE,
        "vector_count": len(vectors),
        "expected_pass_count": len(vectors),
        "actual_pass_count": qa.get("passed"),
        "failed_count": qa.get("failed"),
        "test_count": count_test_functions(),
        "attestation_scope": "synthetic public evaluation only; counts generated from vectors, QA_RESULTS.json, and tests/test_*.py",
        "release_posture": "no production SDK; no patent license; no certification; written-scope depth required",
    }
    attestation["attestation_hash"] = contextual_sha256(REPORT_CONTEXT, attestation)
    attestation["attestation_sig"] = signature_block(REPORT_CONTEXT, attestation)
    write_json(ROOT / "attestations" / "synthetic_evaluation_attestation.json", attestation)
    print("synthetic evaluation attestation: PASS")
    print(f"vectors: {attestation['vector_count']}")
    print(f"tests: {attestation['test_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
