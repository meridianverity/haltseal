from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .canonicalization import contextual_sha256, load_json, write_json
from .constants import (
    DEFAULT_NOW,
    PROOF_RECEIPT_CONTEXT,
    PROOF_RECEIPT_VERSION,
    PUBLIC_BOUNDARY_NOTICE,
    PUBLIC_EVAL_IMPLEMENTATION_HOOK,
    PUBLIC_EVAL_RELEASE_SHA256,
    PUBLIC_EVAL_RELEASE_URL,
    PUBLIC_EVAL_RELEASE_VERSION,
    PUBLIC_EVAL_REPOSITORY,
    VERSION,
)
from .synthetic_crypto import signature_block, verify_signature_block

RIGHTS_POSTURE = [
    "no production SDK",
    "no patent license",
    "no certification",
    "no conformance program",
    "written-scope diligence required for implementation depth",
]

RECEIPT_TYPE = "HALTSEAL_GATEWAY_PROOF_RECEIPT"


def _receipt_payload_for_hash(receipt: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in receipt.items() if k not in {"evidence_hash", "evidence_sig"}}


def build_proof_receipt(root: Path, generated_at: str = DEFAULT_NOW) -> dict[str, Any]:
    qa_path = root / "QA_RESULTS.json"
    qa = load_json(qa_path)
    vectors = load_json(root / "vectors" / "haltseal_gateway_vectors.json")

    if qa.get("total") != len(vectors):
        raise ValueError(f"QA_RESULTS total {qa.get('total')!r} does not match vector count {len(vectors)}")
    if qa.get("failed") != 0 or qa.get("passed") != len(vectors):
        raise ValueError("public evaluation is not in a clean PASS state")

    receipt: dict[str, Any] = {
        "artifact": "HALTSEAL Gateway Proof Pack",
        "receipt_type": RECEIPT_TYPE,
        "receipt_version": PROOF_RECEIPT_VERSION,
        "receipt_tool_release": f"v{VERSION}",
        "generated_at": generated_at,
        "public_eval_version": PUBLIC_EVAL_RELEASE_VERSION,
        "repository": PUBLIC_EVAL_REPOSITORY,
        "release": PUBLIC_EVAL_RELEASE_URL,
        "release_sha256": PUBLIC_EVAL_RELEASE_SHA256,
        "vector_result": {
            "passed": qa.get("passed"),
            "total": qa.get("total"),
            "failed": qa.get("failed"),
        },
        "expected_tests": {
            "pytest_passed": _count_test_functions(root),
        },
        "enabled_public_eval_hook": PUBLIC_EVAL_IMPLEMENTATION_HOOK,
        "public_boundary": PUBLIC_BOUNDARY_NOTICE,
        "rights_posture": RIGHTS_POSTURE,
        "receipt_purpose": "public review, reproducible evaluation, and written-scope diligence handoff",
        "notices": [
            "not a certificate",
            "not a production attestation",
            "not a patent-license grant",
            "not a security certification",
        ],
        "diligence_next_step": "Review one protected action boundary and identify the first missing-proof HOLD condition.",
    }
    receipt["evidence_hash"] = contextual_sha256(PROOF_RECEIPT_CONTEXT, _receipt_payload_for_hash(receipt))
    receipt["evidence_sig"] = signature_block(PROOF_RECEIPT_CONTEXT, _receipt_payload_for_hash(receipt))
    return receipt


def _count_test_functions(root: Path) -> int:
    import ast

    total = 0
    for path in sorted((root / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        total += sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
            for node in ast.walk(tree)
        )
    return total


def verify_proof_receipt(receipt: dict[str, Any], root: Path | None = None) -> list[str]:
    findings: list[str] = []
    if receipt.get("receipt_type") != RECEIPT_TYPE:
        findings.append("receipt_type mismatch")
    if receipt.get("receipt_version") != PROOF_RECEIPT_VERSION:
        findings.append("receipt_version mismatch")
    if receipt.get("public_eval_version") != PUBLIC_EVAL_RELEASE_VERSION:
        findings.append("public_eval_version mismatch")
    if receipt.get("repository") != PUBLIC_EVAL_REPOSITORY:
        findings.append("repository mismatch")
    if receipt.get("release") != PUBLIC_EVAL_RELEASE_URL:
        findings.append("release URL mismatch")
    if receipt.get("release_sha256") != PUBLIC_EVAL_RELEASE_SHA256:
        findings.append("release SHA-256 mismatch")
    if receipt.get("enabled_public_eval_hook") != PUBLIC_EVAL_IMPLEMENTATION_HOOK:
        findings.append("enabled_public_eval_hook mismatch")
    if receipt.get("public_boundary") != PUBLIC_BOUNDARY_NOTICE:
        findings.append("public_boundary mismatch")
    if receipt.get("rights_posture") != RIGHTS_POSTURE:
        findings.append("rights_posture mismatch")

    vector_result = receipt.get("vector_result")
    if not isinstance(vector_result, dict):
        findings.append("vector_result missing or invalid")
    else:
        if vector_result.get("passed") != 32 or vector_result.get("total") != 32 or vector_result.get("failed") != 0:
            findings.append("vector_result must be 32 / 32 PASS")

    if root is not None:
        qa = load_json(root / "QA_RESULTS.json")
        if isinstance(vector_result, dict) and (
            vector_result.get("passed") != qa.get("passed")
            or vector_result.get("total") != qa.get("total")
            or vector_result.get("failed") != qa.get("failed")
        ):
            findings.append("vector_result does not match QA_RESULTS.json")

    payload = _receipt_payload_for_hash(receipt)
    expected_hash = contextual_sha256(PROOF_RECEIPT_CONTEXT, payload)
    if receipt.get("evidence_hash") != expected_hash:
        findings.append("evidence_hash mismatch")
    if not verify_signature_block(PROOF_RECEIPT_CONTEXT, payload, receipt.get("evidence_sig")):
        findings.append("evidence_sig mismatch")
    return findings


def procurement_block(receipt: dict[str, Any]) -> str:
    repo_display = str(receipt["repository"]).replace("https://", "")
    result = receipt["vector_result"]
    return "\n".join([
        "HALTSEAL Gateway Proof Receipt",
        "",
        f"Artifact: HALTSEAL Gateway Proof Pack {receipt['public_eval_version']}",
        f"Repo: {repo_display}",
        f"Result: {result['passed']} / {result['total']} public vectors PASS",
        f"Enabled hook: {receipt['enabled_public_eval_hook']}",
        f"SHA-256: {receipt['release_sha256']}",
        "Boundary: synthetic evaluation only",
        "Rights posture: no production SDK · no patent license · written-scope diligence required",
        "",
        "Requested next step:",
        str(receipt["diligence_next_step"]),
        "",
    ])


def receipt_markdown(receipt: dict[str, Any]) -> str:
    block = procurement_block(receipt).rstrip()
    return f"""# HALTSEAL Gateway Proof Receipt

Turn a public eval run into a review-ready proof receipt.

This receipt is portable review evidence for public evaluation and written-scope diligence handoff. It is not a certificate, not a production attestation, not a security certification, and not a patent-license grant.

## Receipt summary

```text
Artifact: {receipt['artifact']} {receipt['public_eval_version']}
Result: {receipt['vector_result']['passed']} / {receipt['vector_result']['total']} public vectors PASS
Enabled hook: {receipt['enabled_public_eval_hook']}
SHA-256: {receipt['release_sha256']}
Boundary: {receipt['public_boundary']}
Evidence hash: {receipt['evidence_hash']}
```

## Copy-paste diligence block

```text
{block}
```
"""


def write_receipt_bundle(root: Path, out_json: Path, markdown_out: Path | None = None, text_out: Path | None = None) -> dict[str, Any]:
    receipt = build_proof_receipt(root)
    write_json(out_json, receipt)
    if markdown_out:
        markdown_out.parent.mkdir(parents=True, exist_ok=True)
        markdown_out.write_text(receipt_markdown(receipt), encoding="utf-8")
    if text_out:
        text_out.parent.mkdir(parents=True, exist_ok=True)
        text_out.write_text(procurement_block(receipt), encoding="utf-8")
    return receipt
