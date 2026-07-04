#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
RELEASE_VERSION_TOKEN = (VERSION if VERSION.startswith("v") else f"v{VERSION}").replace(".", "_").replace("-", "_").upper()
RELEASE_BASENAME = f"HALTSEAL_GATEWAY_PROOF_PACK_{RELEASE_VERSION_TOKEN}"
EXCLUDE_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}
FIXED_ZIP_TS = (2026, 7, 4, 12, 0, 0)


def run(cmd: list[str]) -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    print(proc.stdout, end="")
    if proc.returncode:
        raise SystemExit(proc.returncode)


def clean_generated_caches() -> None:
    # Keep release hygiene deterministic even when a prior package run left dist/.
    if (ROOT / "dist").exists():
        shutil.rmtree(ROOT / "dist")
    for p in ROOT.rglob("*"):
        if p.is_dir() and p.name in {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}:
            shutil.rmtree(p)
    for p in ROOT.rglob("*.pyc"):
        p.unlink()


def include_file(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if set(rel.parts) & EXCLUDE_PARTS:
        return False
    if path.suffix.lower() in EXCLUDE_SUFFIXES:
        return False
    if path.name in {".DS_Store", ".env"}:
        return False
    if path.suffix.lower() == ".zip":
        return False
    return True



def refresh_source_tree() -> None:
    skip_parts = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build"}
    files = []
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and not (set(p.relative_to(ROOT).parts) & skip_parts):
            files.append(p.relative_to(ROOT).as_posix())
    (ROOT / "SOURCE_TREE.txt").write_text("\n".join(files) + "\n", encoding="utf-8")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_zip(out_zip: Path) -> None:
    root_name = ROOT.name
    files = [p for p in sorted(ROOT.rglob("*")) if p.is_file() and include_file(p)]
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in files:
            arcname = f"{root_name}/{p.relative_to(ROOT).as_posix()}"
            info = zipfile.ZipInfo(arcname, date_time=FIXED_ZIP_TS)
            info.external_attr = (0o644 & 0xFFFF) << 16
            zf.writestr(info, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> int:
    clean_generated_caches()
    run([sys.executable, "tools/regenerate_vectors.py"])
    run([sys.executable, "tools/run_public_eval.py"])
    run([sys.executable, "tools/validate_public_packet.py"])
    run([sys.executable, "tools/generate_transparency_report.py"])
    run([sys.executable, "tools/generate_attestation.py"])
    run([sys.executable, "tools/export_proof_receipt.py"])
    run([sys.executable, "tools/verify_proof_receipt.py"])
    refresh_source_tree()
    run([sys.executable, "tools/make_manifest.py"])
    run([sys.executable, "verify_manifest.py"])
    run([sys.executable, "-m", "pytest", "-q"])
    clean_generated_caches()
    refresh_source_tree()
    run([sys.executable, "tools/make_manifest.py"])
    run([sys.executable, "verify_manifest.py"])
    run([sys.executable, "tools/release_gate.py"])
    run([sys.executable, "tools/zip_audit.py"])

    out_zip = ROOT / "dist" / f"{RELEASE_BASENAME}.zip"
    build_zip(out_zip)
    run([sys.executable, "tools/zip_audit.py", str(out_zip)])
    digest = sha256_file(out_zip)
    sha_path = out_zip.with_suffix(out_zip.suffix + ".sha256.txt")
    sha_path.write_text(f"{digest}  {out_zip.name}\n", encoding="utf-8")
    print(f"release zip: {out_zip}")
    print(f"sha256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
