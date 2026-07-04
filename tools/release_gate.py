#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from haltseal_eval.constants import PUBLIC_EVAL_IMPLEMENTATION_HOOK, VERSION

TEXT_EXT = {".md", ".py", ".json", ".txt", ".yaml", ".yml", ".toml", ".cfg", ".ini"}
SKIP = {"MANIFEST.json", "MANIFEST.sha256.json", "QA_RESULTS.json", "release_gate.py"}

# Exact high-risk phrases for a public evaluation artifact. The gate intentionally
# allows boundary disclaimers such as "no patent license" and "not production software".
FORBIDDEN_PATTERNS = [
    r"production-ready",
    r"production SDK included",
    r"production use permitted",
    r"free patent license",
    r"patent license grant",
    r"official reference implementation",
    r"IETF standard",
    r"certified compliant",
    r"guaranteed licensing",
    r"must license",
    r"world'?s first",
    r"world'?s only",
    r"Nobel",
    r"\$100m",
    r"Fortune 500",
    r"Big Tech",
    r"claim chart included",
    r"infringement map",
    r"target company",
    r"customer architecture",
    r"commercial terms included",
]

REQUIRED_FILES = [
    "README.md",
    "README_FIRST.md",
    "QUICKSTART.md",
    "LICENSE-EVALUATION.md",
    "PATENT-NOTICE.md",
    "SECURITY_AND_LIMITATIONS.md",
    "docs/PUBLIC_BOUNDARY.md",
    "docs/BOUNDARY_MAPPER.md",
    "docs/LICENSING_HANDOFF.md",
    "docs/REVIEWER_GUIDE.md",
    "docs/RELEASE_READINESS_v0_3_0.md",
    "docs/IP_PUBLIC_ALIGNMENT.md",
    "attestations/synthetic_evaluation_attestation.json",
    "attestations/privacy_preserving_transparency_report.json",
    "tools/run_public_eval.py",
    "tools/validate_public_packet.py",
    "tools/generate_transparency_report.py",
    "tools/generate_attestation.py",
    "tools/zip_audit.py",
    "vectors/haltseal_gateway_vectors.json",
]

FUTURE_HOOK_NAMES = {"device_io_gateway", "dispatch_gateway", "actuation_gateway"}
EXCLUDE_TREE_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build"}
EXCLUDE_TREE_SUFFIXES = {".pyc", ".pyo"}


def load_json(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def scan_text() -> list[str]:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name in SKIP or path.suffix.lower() not in TEXT_EXT:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                findings.append(f"{path.relative_to(ROOT)} contains high-risk phrase /{pattern}/")
    return findings


def check_required_files() -> list[str]:
    return [f"missing required file: {rel}" for rel in REQUIRED_FILES if not (ROOT / rel).exists()]


def count_test_functions() -> int:
    total = 0
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        total += sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
            for node in ast.walk(tree)
        )
    return total


def check_attestation_consistency() -> list[str]:
    findings: list[str] = []
    try:
        vectors = load_json("vectors/haltseal_gateway_vectors.json")
        qa = load_json("QA_RESULTS.json")
        att = load_json("attestations/synthetic_evaluation_attestation.json")
    except Exception as exc:
        return [f"attestation consistency check could not load required JSON: {exc}"]

    expected = {
        "version": VERSION,
        "vector_count": len(vectors),
        "expected_pass_count": len(vectors),
        "actual_pass_count": qa.get("passed"),
        "failed_count": qa.get("failed"),
        "test_count": count_test_functions(),
    }
    for key, value in expected.items():
        if att.get(key) != value:
            findings.append(f"attestation mismatch: {key} expected {value!r} got {att.get(key)!r}")
    if qa.get("total") != len(vectors):
        findings.append(f"QA total mismatch: expected {len(vectors)} got {qa.get('total')!r}")
    if qa.get("failed") != 0:
        findings.append(f"QA failed count is nonzero: {qa.get('failed')!r}")
    return findings


def check_transparency_report_consistency() -> list[str]:
    findings: list[str] = []
    try:
        qa = load_json("QA_RESULTS.json")
        report = load_json("attestations/privacy_preserving_transparency_report.json")
    except Exception as exc:
        return [f"transparency report consistency check could not load required JSON: {exc}"]
    checks = {
        "total_vectors": qa.get("total"),
        "passed_vectors": qa.get("passed"),
        "failed_vectors": qa.get("failed"),
    }
    for key, value in checks.items():
        if report.get(key) != value:
            findings.append(f"transparency report mismatch: {key} expected {value!r} got {report.get(key)!r}")
    return findings


def check_boundary_mapper_consistency() -> list[str]:
    findings: list[str] = []
    path = ROOT / "docs" / "BOUNDARY_MAPPER.md"
    text = path.read_text(encoding="utf-8")
    if PUBLIC_EVAL_IMPLEMENTATION_HOOK not in text:
        findings.append("BOUNDARY_MAPPER.md does not name the enabled public-eval hook")
    for hook in sorted(FUTURE_HOOK_NAMES):
        if hook in text:
            findings.append(f"BOUNDARY_MAPPER.md previews non-enabled hook name: {hook}")
    if "only implementation hook enabled" not in text:
        findings.append("BOUNDARY_MAPPER.md must state that only one implementation hook is enabled")
    return findings


def expected_source_tree() -> list[str]:
    files: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if set(rel.parts) & EXCLUDE_TREE_PARTS:
            continue
        if path.suffix.lower() in EXCLUDE_TREE_SUFFIXES:
            continue
        files.append(rel.as_posix())
    return files


def check_release_hygiene() -> list[str]:
    """Optional strict checks for maintainers running HALTSEAL_STRICT_TREE=1."""
    path = ROOT / "SOURCE_TREE.txt"
    if not path.exists():
        return ["SOURCE_TREE.txt is missing"]
    expected = expected_source_tree()
    actual = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if actual != expected:
        missing = sorted(set(expected) - set(actual))[:10]
        extra = sorted(set(actual) - set(expected))[:10]
        finding = "SOURCE_TREE.txt is not synchronized with the current tree"
        if missing:
            finding += f"; missing examples: {missing}"
        if extra:
            finding += f"; extra examples: {extra}"
        return [finding]
    return []


def main() -> int:
    findings = (
        check_required_files()
        + scan_text()
        + check_attestation_consistency()
        + check_transparency_report_consistency()
        + check_boundary_mapper_consistency()
    )
    if os.environ.get("HALTSEAL_STRICT_TREE") == "1":
        findings += check_release_hygiene()
    if findings:
        print("release gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("release gate: PASS")
    print("findings: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
