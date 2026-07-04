from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from haltseal_eval.proof_receipt import build_proof_receipt, verify_proof_receipt, procurement_block, receipt_markdown, write_receipt_bundle
from haltseal_eval.canonicalization import load_json

ROOT = Path(__file__).resolve().parents[1]


def test_build_proof_receipt_is_valid_and_public_safe() -> None:
    receipt = build_proof_receipt(ROOT)
    assert receipt["receipt_type"] == "HALTSEAL_GATEWAY_PROOF_RECEIPT"
    assert receipt["public_eval_version"] == "v0.3.0-public-eval"
    assert receipt["vector_result"] == {"passed": 32, "total": 32, "failed": 0}
    assert receipt["enabled_public_eval_hook"] == "network_egress_gateway"
    assert "no production SDK" in receipt["rights_posture"]
    assert "no patent license" in receipt["rights_posture"]
    assert verify_proof_receipt(receipt, ROOT) == []


def test_proof_receipt_schema_accepts_generated_receipt() -> None:
    receipt = build_proof_receipt(ROOT)
    schema = load_json(ROOT / "schemas" / "haltseal_gateway_proof_receipt.schema.json")
    errors = list(Draft202012Validator(schema).iter_errors(receipt))
    assert errors == []


def test_proof_receipt_evidence_hash_rejects_tampering() -> None:
    receipt = build_proof_receipt(ROOT)
    receipt["vector_result"]["passed"] = 31
    findings = verify_proof_receipt(receipt, ROOT)
    assert any("vector_result" in finding or "evidence_hash" in finding for finding in findings)


def test_proof_receipt_examples_match_generator() -> None:
    expected = build_proof_receipt(ROOT)
    example = load_json(ROOT / "examples" / "haltseal_gateway_proof_receipt.example.json")
    assert example == expected


def test_proof_receipt_copy_blocks_are_review_ready() -> None:
    receipt = build_proof_receipt(ROOT)
    text = procurement_block(receipt)
    md = receipt_markdown(receipt)
    assert "HALTSEAL Gateway Proof Receipt" in text
    assert "Result: 32 / 32 public vectors PASS" in text
    assert "written-scope diligence required" in text
    assert "Evidence hash" in md


def test_write_receipt_bundle_outputs_json_markdown_and_text(tmp_path: Path) -> None:
    out_json = tmp_path / "receipt.json"
    out_md = tmp_path / "receipt.md"
    out_txt = tmp_path / "receipt.txt"
    receipt = write_receipt_bundle(ROOT, out_json, out_md, out_txt)
    assert json.loads(out_json.read_text(encoding="utf-8")) == receipt
    assert "Copy-paste diligence block" in out_md.read_text(encoding="utf-8")
    assert "Enabled hook: network_egress_gateway" in out_txt.read_text(encoding="utf-8")
