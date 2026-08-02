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
from haltseal_resolve.verifier import verify_receipt

TEXT_EXT = {".md", ".py", ".json", ".txt", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".html"}
SKIP = {"MANIFEST.json", "MANIFEST.sha256.json", "QA_RESULTS.json", "release_gate.py"}

# Public release metadata must remain institutional and evidence-led. These phrases
# are disallowed even when used aspirationally because they weaken diligence posture.
FORBIDDEN_PATTERNS = [
    r"production-ready",
    r"production SDK included",
    r"production use permitted",
    r"free patent license",
    r"patent license grant",
    r"official reference implementation",
    r"v0\.3\.1-proof-receipt",
    r"0\.3\.1-proof-receipt",
    r"IETF standard",
    r"certified compliant",
    r"guaranteed licensing",
    r"must license",
    r"world'?s first",
    r"world'?s only",
    r"Nobel",
    r"\$100m",
    r"\$10m",
    r"10m\+",
    r"99\.9",
    r"world\s*#?\s*1",
    r"world\s+number\s+one",
    r"Fortune 500",
    r"Big Tech",
    r"claim chart included",
    r"infringement map",
    r"target company",
    r"customer architecture",
    r"commercial terms included",
]

REQUIRED_FILES = [
    # Historical v0.3.2 proof lineage.
    "README.md",
    "README_FIRST.md",
    "QUICKSTART.md",
    "LICENSE-EVALUATION.md",
    "PATENT-NOTICE.md",
    "SECURITY_AND_LIMITATIONS.md",
    "docs/PUBLIC_BOUNDARY.md",
    "docs/BOUNDARY_MAPPER.md",
    "docs/LICENSING_HANDOFF.md",
    "docs/PROOF_RECEIPT.md",
    "docs/DILIGENCE_PACKET.md",
    "docs/REVIEWER_GUIDE.md",
    "docs/RELEASE_READINESS_v0_3_0.md",
    "docs/IP_PUBLIC_ALIGNMENT.md",
    "attestations/synthetic_evaluation_attestation.json",
    "attestations/privacy_preserving_transparency_report.json",
    "receipts/haltseal-gateway-proof-receipt.json",
    "receipts/haltseal-gateway-proof-receipt.md",
    "receipts/haltseal-gateway-proof-receipt.txt",
    "schemas/haltseal_gateway_proof_receipt.schema.json",
    "tools/export_proof_receipt.py",
    "tools/verify_proof_receipt.py",
    "tools/run_public_eval.py",
    "tools/validate_public_packet.py",
    "tools/generate_transparency_report.py",
    "tools/generate_attestation.py",
    "tools/zip_audit.py",
    "tools/verify_release_artifact.py",
    "tools/generate_transparency_bundle.py",
    "tools/verify_transparency_bundle.py",
    "tools/generate_ed25519_profile.py",
    "tools/verify_ed25519_profile.py",
    "tools/independent_recompute.py",
    "haltseal_eval/transparency.py",
    "haltseal_eval/ed25519_eval.py",
    "receipts/haltseal-transparency-bundle.json",
    "receipts/haltseal-ed25519-proof-profile.json",
    "vectors/haltseal_gateway_vectors.json",
    # v0.4.0 public resolve surface.
    "RELEASE_NOTES_v0.4.0.md",
    "requirements.lock",
    ".github/workflows/public-eval.yml",
    "openapi/haltseal-public-resolve-v1.yaml",
    "profiles/payment.one-time-purchase.v1.json",
    "profiles/payment.outcome-unknown.v1.json",
    "profiles/payment.revoked-authority.v1.json",
    "reason-codes/haltseal-public-resolve-reason-codes-v1.json",
    "keys/sample-evaluation-jwks.json",
    "haltseal_resolve/mock_engine.py",
    "haltseal_resolve/mock_server.py",
    "haltseal_resolve/verifier.py",
    "haltseal_resolve/receipt_profile.py",
    "haltseal_resolve/jws.py",
    "haltseal_resolve/strict_json.py",
    "verifier/python/haltseal_verify.py",
    "verifier/typescript/haltseal_verify.mjs",
    "verifier/typescript/haltseal_verify.ts",
    "vectors/public-resolve/public-resolve-conformance-v1.json",
    "vectors/public-resolve/verifier-parity-v1.json",
    "tools/public_resolve/generate_samples.py",
    "tools/public_resolve/run_verifier_parity.py",
    "tools/public_resolve/run_http_contract.py",
    "tools/public_resolve/run_conformance.py",
    "tools/public_resolve/generate_release_records.py",
    "tools/public_resolve/verify_public_release.py",
    "tools/public_resolve/http_smoke.py",
    "release/v0.4.0/PUBLIC_RESOLVE_QA_RESULTS.json",
    "release/v0.4.0/VERIFIER_PARITY_QA_RESULTS.json",
    "release/v0.4.0/HTTP_CONTRACT_QA_RESULTS.json",
    "release/v0.4.0/HALTSEAL_PUBLIC_RESOLVE_RELEASE_MANIFEST.json",
    "release/v0.4.0/SBOM.spdx.json",
    "release/v0.4.0/provenance.json",
    "release/v0.4.0/PUBLIC_GITHUB_ASSET_INDEX.json",
    "release/v0.4.0/GITHUB_RELEASE_METADATA.json",
    "release/v0.4.0/REPOSITORY_METADATA.json",
    "release/v0.4.0/HOSTED_LAUNCH_GATE_TEMPLATE.json",
    "docs/public-resolve/PUBLIC_API_BOUNDARY.md",
    "docs/public-resolve/RECEIPT_PROFILE.md",
    "docs/public-resolve/IDEMPOTENCY_AND_REPLAY.md",
    "docs/public-resolve/NO_PROVIDER_EGRESS.md",
    "docs/public-resolve/SECURITY_AND_LIMITATIONS.md",
    "docs/public-resolve/PRIVATE_IMPLEMENTATION_BOUNDARY.md",
    "docs/public-resolve/API_EVALUATION_TERMS.md",
    "docs/public-resolve/LAUNCH_GATES.md",
    "docs/public-resolve/THREAT_MODEL.md",
    "docs/public-resolve/IMPLEMENTATION_PLAN.md",
    "docs/GITHUB_RELEASE_BODY.md",
    "docs/GITHUB_UPLOAD_CHECKLIST.md",
    "docs/WEBSITE_CTA_COPY.md",
    "website/HALTSEAL_PUBLIC_RESOLVE_PATCH.md",
    "website/HALTSEAL_PUBLIC_RESOLVE_SECTION.html",
    "website/HALTSEAL_CURRENT_AUTHORITY_MICROPATCH.html",
]

PUBLIC_SCHEMA_FILES = {
    "action-v1.json", "authority-v1.json", "boundary-v1.json",
    "challenge-request-v1.json", "challenge-response-v1.json",
    "emission-v1.json", "problem-v1.json", "receipt-payload-v1.json",
    "resolve-request-v1.json", "resolve-response-v1.json",
    "verify-request-v1.json", "verify-response-v1.json",
}
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
        if set(path.relative_to(ROOT).parts) & EXCLUDE_TREE_PARTS:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                findings.append(f"{path.relative_to(ROOT)} contains high-risk phrase /{pattern}/")
    return findings


def check_required_files() -> list[str]:
    findings = [f"missing required file: {rel}" for rel in REQUIRED_FILES if not (ROOT / rel).exists()]
    actual_schemas = {p.name for p in (ROOT / "schemas/public-resolve").glob("*.json")}
    if actual_schemas != PUBLIC_SCHEMA_FILES:
        findings.append(f"public schema set mismatch: expected {sorted(PUBLIC_SCHEMA_FILES)} got {sorted(actual_schemas)}")
    return findings


def count_test_functions(directory: str) -> int:
    total = 0
    for path in sorted((ROOT / directory).glob("test_*.py")):
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
        # Historical attestation covers the historical tests directory only.
        "test_count": count_test_functions("tests"),
    }
    for key, value in expected.items():
        if att.get(key) != value:
            findings.append(f"attestation mismatch: {key} expected {value!r} got {att.get(key)!r}")
    if qa.get("total") != len(vectors):
        findings.append(f"QA total mismatch: expected {len(vectors)} got {qa.get('total')!r}")
    if qa.get("failed") != 0:
        findings.append(f"QA failed count is nonzero: {qa.get('failed')!r}")
    return findings


def check_proof_receipt_consistency() -> list[str]:
    findings: list[str] = []
    try:
        from haltseal_eval.proof_receipt import build_proof_receipt, verify_proof_receipt
        receipt = load_json("receipts/haltseal-gateway-proof-receipt.json")
        expected = build_proof_receipt(ROOT)
    except Exception as exc:
        return [f"proof receipt consistency check could not load required data: {exc}"]
    if receipt != expected:
        findings.append("receipts/haltseal-gateway-proof-receipt.json is not synchronized with QA_RESULTS.json")
    findings += [f"proof receipt invalid: {f}" for f in verify_proof_receipt(receipt, ROOT)]
    md = ROOT / "receipts" / "haltseal-gateway-proof-receipt.md"
    txt = ROOT / "receipts" / "haltseal-gateway-proof-receipt.txt"
    if md.exists() and "HALTSEAL Gateway Proof Receipt" not in md.read_text(encoding="utf-8"):
        findings.append("proof receipt Markdown missing title")
    if txt.exists() and "Result: 32 / 32 public vectors PASS" not in txt.read_text(encoding="utf-8"):
        findings.append("proof receipt text block missing vector result")
    return findings


def check_transparency_report_consistency() -> list[str]:
    findings: list[str] = []
    try:
        qa = load_json("QA_RESULTS.json")
        report = load_json("attestations/privacy_preserving_transparency_report.json")
    except Exception as exc:
        return [f"transparency report consistency check could not load required JSON: {exc}"]
    checks = {"total_vectors": qa.get("total"), "passed_vectors": qa.get("passed"), "failed_vectors": qa.get("failed")}
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


def check_public_resolve_consistency() -> list[str]:
    findings: list[str] = []
    try:
        qa = load_json("release/v0.4.0/PUBLIC_RESOLVE_QA_RESULTS.json")
        jwks = load_json("keys/sample-evaluation-jwks.json")
        metadata = load_json("release/v0.4.0/GITHUB_RELEASE_METADATA.json")
        reason_codes = load_json("reason-codes/haltseal-public-resolve-reason-codes-v1.json")
    except Exception as exc:
        return [f"public resolve consistency could not load required data: {exc}"]
    if (qa.get("vectors"), qa.get("passed"), qa.get("failed")) != (32, 32, 0):
        findings.append("public resolve conformance result is not 32/32 PASS")
    try:
        parity = load_json("release/v0.4.0/VERIFIER_PARITY_QA_RESULTS.json")
        http_contract = load_json("release/v0.4.0/HTTP_CONTRACT_QA_RESULTS.json")
    except Exception as exc:
        findings.append(f"public verifier/HTTP QA records could not be loaded: {exc}")
    else:
        if (parity.get("cases"), parity.get("passed"), parity.get("failed"), parity.get("python_typescript_parity")) != (20, 20, 0, True):
            findings.append("receipt verifier parity is not 20/20 PASS")
        if (http_contract.get("cases"), http_contract.get("passed"), http_contract.get("failed")) != (5, 5, 0):
            findings.append("HTTP contract regression is not 5/5 PASS")
    if count_test_functions("tests_public_resolve") != 16:
        findings.append("public resolve contract test source count is not 16")
    for path in sorted((ROOT / "examples/receipts").glob("*.receipt.jws")):
        try:
            result = verify_receipt(path.read_text(encoding="utf-8").strip(), jwks)
            if result.get("semantic_replay") != "PASS":
                findings.append(f"sample receipt semantic replay did not pass: {path.name}")
        except Exception as exc:
            findings.append(f"sample receipt invalid: {path.name}: {exc}")
    if len(list((ROOT / "examples/receipts").glob("*.receipt.jws"))) != 4:
        findings.append("expected four signed public sample receipts")
    if metadata.get("tag_name") != "v0.4.0-public-resolve-challenge":
        findings.append("GitHub release tag mismatch")
    if set(reason_codes.get("decisions", [])) != {"ACCEPT", "HOLD", "REFUSE"}:
        findings.append("decision registry mismatch")
    openapi = (ROOT / "openapi/haltseal-public-resolve-v1.yaml").read_text(encoding="utf-8")
    for required in ("/challenges:", "/resolve:", "/verify:", "/jwks.json:"):
        if required not in openapi:
            findings.append(f"OpenAPI missing {required}")
    emission_schema = (ROOT / "schemas/public-resolve/emission-v1.json").read_text(encoding="utf-8")
    if "synthetic_request_record_id" not in emission_schema:
        findings.append("emission schema missing synthetic_request_record_id")
    if "provider_request_id" in openapi:
        findings.append("OpenAPI incorrectly uses provider_request_id for synthetic evaluation")
    public_source = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in (ROOT / "haltseal_resolve").glob("*.py"))
    for forbidden in ("requests.", "httpx.", "aiohttp.", "stripe.", "checkout_sdk", "boto3."):
        if forbidden in public_source:
            findings.append(f"public source includes outbound/provider marker: {forbidden}")
    for forbidden_path in (ROOT / "haltseal_hosted", ROOT / "private_runtime"):
        if forbidden_path.exists():
            findings.append(f"private hosted runtime leaked into public tree: {forbidden_path.name}")
    return findings


def expected_source_tree() -> list[str]:
    files: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if set(rel.parts) & EXCLUDE_TREE_PARTS or path.suffix.lower() in EXCLUDE_TREE_SUFFIXES:
            continue
        files.append(rel.as_posix())
    return files


def check_release_hygiene() -> list[str]:
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
        + check_proof_receipt_consistency()
        + check_boundary_mapper_consistency()
        + check_public_resolve_consistency()
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
    print("historical gateway vectors: 32 / 32 PASS")
    print("public resolve vectors: 32 / 32 PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
