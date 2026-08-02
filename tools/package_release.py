#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RELEASE_TAG = "v0.4.0-public-resolve-challenge"
RELEASE_BASENAME = "haltseal-public-resolve-challenge-v0.4.0"
FIXED_ZIP_TS = (2026, 8, 1, 16, 0, 0)
EXCLUDE_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


def run(cmd: list[str], *, env_extra: dict[str, str] | None = None) -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    print(proc.stdout, end="")
    if proc.returncode:
        raise SystemExit(proc.returncode)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_generated_caches() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    for p in list(ROOT.rglob("*")):
        if p.is_dir() and p.name in {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}:
            shutil.rmtree(p)
    for p in ROOT.rglob("*.pyc"):
        p.unlink()
    for p in ROOT.glob("*.egg-info"):
        if p.is_dir():
            shutil.rmtree(p)


def include_public_file(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if set(rel.parts) & EXCLUDE_PARTS:
        return False
    if path.suffix.lower() in EXCLUDE_SUFFIXES or path.name in {".DS_Store", ".env"}:
        return False
    if path.suffix.lower() == ".zip":
        return False
    return True


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TS)
    info.external_attr = (0o644 & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def write_zip(out: Path, files: list[tuple[Path, str]]) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for src, arcname in sorted(files, key=lambda x: x[1]):
            zf.writestr(zip_info(arcname), src.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build_main_zip(out: Path) -> None:
    files = []
    for p in ROOT.rglob("*"):
        if p.is_file() and include_public_file(p):
            files.append((p, f"{RELEASE_BASENAME}/{p.relative_to(ROOT).as_posix()}"))
    write_zip(out, files)


def build_component_zip(out: Path, root_name: str, sources: list[Path]) -> None:
    files: list[tuple[Path, str]] = []
    for source in sources:
        if source.is_file():
            files.append((source, f"{root_name}/{source.name}"))
        else:
            for p in source.rglob("*"):
                if p.is_file() and include_public_file(p):
                    files.append((p, f"{root_name}/{source.name}/{p.relative_to(source).as_posix()}"))
    write_zip(out, files)


def refresh_source_tree_and_manifest() -> None:
    run([sys.executable, "tools/make_manifest.py"])
    run([sys.executable, "verify_manifest.py"])


def prepare_tree() -> None:
    run([sys.executable, "tools/regenerate_vectors.py"])
    run([sys.executable, "tools/run_public_eval.py"])
    run([sys.executable, "tools/validate_public_packet.py"])
    run([sys.executable, "tools/generate_transparency_report.py"])
    run([sys.executable, "tools/generate_transparency_bundle.py"])
    run([sys.executable, "tools/verify_transparency_bundle.py"])
    run([sys.executable, "tools/generate_attestation.py"])
    run([sys.executable, "tools/export_proof_receipt.py"])
    run([sys.executable, "tools/verify_proof_receipt.py"])
    run([sys.executable, "tools/generate_ed25519_profile.py"])
    run([sys.executable, "tools/verify_ed25519_profile.py"])
    run([sys.executable, "tools/independent_recompute.py"])
    run([sys.executable, "tools/public_resolve/generate_samples.py"])
    run([sys.executable, "tools/public_resolve/run_conformance.py"])
    run([sys.executable, "tools/public_resolve/run_verifier_parity.py"])
    run([sys.executable, "tools/public_resolve/run_http_contract.py"])
    run([sys.executable, "tools/public_resolve/generate_release_records.py"])
    refresh_source_tree_and_manifest()
    run([sys.executable, "tools/public_resolve/http_smoke.py"])
    run([sys.executable, "-m", "pytest", "-q"])
    run([sys.executable, "tools/public_resolve/verify_public_release.py"])
    run(["node", "verifier/typescript/haltseal_verify.mjs", "examples/receipts/accept-exact.receipt.jws", "keys/sample-evaluation-jwks.json"])
    clean_tree_only()
    # Release records contain generated digests and must be stable before the root manifest.
    run([sys.executable, "tools/public_resolve/generate_release_records.py"])
    refresh_source_tree_and_manifest()
    run([sys.executable, "tools/release_gate.py"])
    run([sys.executable, "tools/release_gate.py"], env_extra={"HALTSEAL_STRICT_TREE": "1"})
    run([sys.executable, "tools/verify_release_artifact.py", "--tree", "."])
    run([sys.executable, "tools/zip_audit.py"])


def clean_tree_only() -> None:
    for p in list(ROOT.rglob("*")):
        if p.is_dir() and p.name in {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}:
            shutil.rmtree(p)
    for p in ROOT.rglob("*.pyc"):
        p.unlink()
    for p in ROOT.glob("*.egg-info"):
        if p.is_dir():
            shutil.rmtree(p)


def copy_asset(source: Path, target_name: str) -> Path:
    target = DIST / target_name
    shutil.copy2(source, target)
    return target


def main() -> int:
    clean_generated_caches()
    prepare_tree()
    DIST.mkdir(parents=True, exist_ok=True)

    main_zip = DIST / f"{RELEASE_BASENAME}.zip"
    build_main_zip(main_zip)
    main_sha = sha256_file(main_zip)
    main_sidecar = DIST / f"{main_zip.name}.sha256.txt"
    main_sidecar.write_text(f"{main_sha}  {main_zip.name}\n", encoding="utf-8")

    openapi_asset = copy_asset(ROOT / "openapi/haltseal-public-resolve-v1.yaml", "openapi-haltseal-public-resolve-v1.yaml")
    schema_zip = DIST / "haltseal-public-resolve-schemas-v1.zip"
    build_component_zip(schema_zip, "haltseal-public-resolve-schemas-v1", [ROOT / "schemas/public-resolve", ROOT / "profiles", ROOT / "reason-codes"])
    receipt_zip = DIST / "haltseal-public-resolve-sample-receipts-v1.zip"
    build_component_zip(receipt_zip, "haltseal-public-resolve-sample-receipts-v1", [ROOT / "examples/receipts", ROOT / "keys/sample-evaluation-jwks.json"])
    verifier_zip = DIST / "haltseal-public-resolve-verifiers-v1.zip"
    build_component_zip(verifier_zip, "haltseal-public-resolve-verifiers-v1", [ROOT / "verifier", ROOT / "haltseal_resolve/verifier.py", ROOT / "haltseal_resolve/receipt_profile.py", ROOT / "haltseal_resolve/jws.py", ROOT / "haltseal_resolve/canonical.py", ROOT / "haltseal_resolve/models.py", ROOT / "haltseal_resolve/semantics.py", ROOT / "haltseal_resolve/constants.py"])

    copied = [
        copy_asset(ROOT / "release/v0.4.0/HALTSEAL_PUBLIC_RESOLVE_RELEASE_MANIFEST.json", "HALTSEAL_PUBLIC_RESOLVE_RELEASE_MANIFEST.json"),
        copy_asset(ROOT / "release/v0.4.0/SBOM.spdx.json", "SBOM.spdx.json"),
        copy_asset(ROOT / "release/v0.4.0/provenance.json", "provenance.json"),
    ]
    all_assets = [main_zip, main_sidecar, openapi_asset, schema_zip, receipt_zip, verifier_zip, *copied]
    sha_lines = []
    asset_rows = []
    for p in sorted(all_assets, key=lambda x: x.name):
        digest = sha256_file(p)
        sha_lines.append(f"{digest}  {p.name}")
        asset_rows.append({"filename": p.name, "bytes": p.stat().st_size, "sha256": digest})
        if p != main_sidecar:
            (DIST / f"{p.name}.sha256.txt").write_text(f"{digest}  {p.name}\n", encoding="utf-8")
    (DIST / "HALTSEAL_PUBLIC_RESOLVE_GITHUB_ASSETS.sha256.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")
    index = {
        "release": RELEASE_TAG,
        "repository": "https://github.com/meridianverity/haltseal",
        "assets": asset_rows,
        "private_runtime_included": False,
        "publication_condition": "Hosted launch gate PASS and exact tagged-commit provenance recorded.",
    }
    (DIST / "HALTSEAL_PUBLIC_RESOLVE_GITHUB_ASSET_INDEX.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    run([sys.executable, "tools/zip_audit.py", str(main_zip)])
    run([sys.executable, "tools/verify_release_artifact.py", str(main_zip), "--sha256-file", str(main_sidecar)])
    for component in (schema_zip, receipt_zip, verifier_zip):
        run([sys.executable, "tools/zip_audit.py", str(component)])

    print(f"public release zip: {main_zip}")
    print(f"public release sha256: {main_sha}")
    print(f"public GitHub assets: {len(asset_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
