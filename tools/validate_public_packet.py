#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from haltseal_eval.canonicalization import load_json
from haltseal_eval.replay import ReplayCache
from haltseal_eval.verifier import verify_packet


def schema(name: str) -> dict[str, Any]:
    return load_json(ROOT / "schemas" / name)


SCHEMAS = {
    "packet": schema("gateway_review_packet.schema.json"),
    "action": schema("protected_action.schema.json"),
    "permit": schema("permit_token.schema.json"),
    "signed_head": schema("signed_head.schema.json"),
    "result": schema("verifier_result.schema.json"),
    "evidence": schema("ial_record.schema.json"),
}


def format_validation_error(exc: ValidationError) -> str:
    loc = "/".join(str(p) for p in exc.absolute_path) or "$"
    return f"{loc}: {exc.message}"


def validate_with(name: str, value: Any) -> list[str]:
    validator = Draft202012Validator(SCHEMAS[name])
    return [format_validation_error(e) for e in sorted(validator.iter_errors(value), key=lambda e: list(e.absolute_path))]


def check_json_files() -> list[str]:
    findings: list[str] = []
    for path in ROOT.rglob("*.json"):
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        try:
            load_json(path)
        except Exception as exc:
            findings.append(f"invalid json: {path.relative_to(ROOT)}: {exc}")
    return findings


SHAPE_INVALID_RESULT_CODES = {"ACTION_SHAPE_INVALID", "SIGNED_HEAD_SHAPE_INVALID", "PERMIT_SHAPE_INVALID"}


def check_vectors_against_schemas() -> list[str]:
    findings: list[str] = []
    vectors = load_json(ROOT / "vectors" / "haltseal_gateway_vectors.json")
    seen: set[str] = set()
    for index, packet in enumerate(vectors):
        prefix = f"vectors[{index}]/{packet.get('vector_id', '<missing>')}"
        vector_id = packet.get("vector_id")
        if vector_id in seen:
            findings.append(f"duplicate vector_id: {vector_id}")
        if isinstance(vector_id, str):
            seen.add(vector_id)

        for err in validate_with("packet", packet):
            findings.append(f"{prefix} packet schema: {err}")
        expected_code = packet.get("expected", {}).get("result_code")
        # A small number of vectors intentionally carry malformed sub-objects to
        # prove fail-closed behavior. They are still required to produce schema-valid
        # verifier results and evidence.
        skip_component_schema = expected_code in SHAPE_INVALID_RESULT_CODES
        if not skip_component_schema and isinstance(packet.get("action"), dict):
            for err in validate_with("action", packet["action"]):
                findings.append(f"{prefix} action schema: {err}")
        if not skip_component_schema and isinstance(packet.get("permit"), dict):
            for err in validate_with("permit", packet["permit"]):
                findings.append(f"{prefix} permit schema: {err}")
        if not skip_component_schema and isinstance(packet.get("signed_head"), dict):
            for err in validate_with("signed_head", packet["signed_head"]):
                findings.append(f"{prefix} signed_head schema: {err}")

        result = verify_packet(packet, ReplayCache())
        for err in validate_with("result", result):
            findings.append(f"{prefix} result schema: {err}")
        for err in validate_with("evidence", result.get("evidence")):
            findings.append(f"{prefix} evidence schema: {err}")
        expected = packet.get("expected", {})
        actual = {"disposition": result.get("disposition"), "result_code": result.get("result_code"), "stage": result.get("stage")}
        if expected != actual:
            findings.append(f"{prefix} expected mismatch: expected={expected} actual={actual}")
    return findings


def check_examples_match_vectors() -> list[str]:
    findings: list[str] = []
    vectors = load_json(ROOT / "vectors" / "haltseal_gateway_vectors.json")
    vector_by_id = {v["vector_id"]: v for v in vectors}
    for vector_id, packet in vector_by_id.items():
        expected = ROOT / "examples" / f"{vector_id.lower()}.json"
        if not expected.exists():
            findings.append(f"missing example for vector: {vector_id}")
            continue
        try:
            example_packet = load_json(expected)
        except Exception as exc:
            findings.append(f"invalid example json: {expected.relative_to(ROOT)}: {exc}")
            continue
        if example_packet != packet:
            findings.append(f"example does not exactly match vector: {expected.relative_to(ROOT)}")

    example_ids = {p.stem.upper() for p in (ROOT / "examples").glob("h*.json") if re.match(r"^h\d{2}_", p.stem)}
    vector_ids_upper = {v.upper() for v in vector_by_id}
    for extra in sorted(example_ids - vector_ids_upper):
        findings.append(f"orphan example without vector: {extra.lower()}.json")
    return findings


def check_expected_results_file() -> list[str]:
    expected_path = ROOT / "vectors" / "expected_results.json"
    if not expected_path.exists():
        return ["missing vectors/expected_results.json"]
    expected_results = load_json(expected_path)
    vectors = load_json(ROOT / "vectors" / "haltseal_gateway_vectors.json")
    expected_from_vectors = {v["vector_id"]: v["expected"] for v in vectors}
    if expected_results != expected_from_vectors:
        return ["vectors/expected_results.json does not match vector expected blocks"]
    return []


def run(cmd: list[str]) -> int:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(proc.stdout, end="")
    return proc.returncode


def main() -> int:
    findings = check_json_files() + check_vectors_against_schemas() + check_examples_match_vectors() + check_expected_results_file()
    if findings:
        print("packet validation: FAIL")
        for f in findings:
            print(f"- {f}")
        return 1
    if run([sys.executable, "tools/run_public_eval.py"]) != 0:
        return 1
    print("packet validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
