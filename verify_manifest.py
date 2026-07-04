#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDE_NAMES = {"MANIFEST.json", "MANIFEST.sha256.json"}
EXCLUDE_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def include_file(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return (
        path.is_file()
        and path.name not in EXCLUDE_NAMES
        and not (set(rel.parts) & EXCLUDE_PARTS)
        and path.suffix.lower() not in EXCLUDE_SUFFIXES
    )


def main() -> int:
    manifest_path = ROOT / "MANIFEST.json"
    if not manifest_path.exists():
        print("manifest verification: FAIL - MANIFEST.json missing")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = manifest.get("files", [])
    findings: list[str] = []
    manifest_paths = {row["path"] for row in rows}
    actual_paths = {str(p.relative_to(ROOT)).replace("\\", "/") for p in ROOT.rglob("*") if include_file(p)}

    for row in rows:
        p = ROOT / row["path"]
        if not p.exists():
            findings.append(f"missing file: {row['path']}")
            continue
        actual = sha256_file(p)
        if actual != row["sha256"]:
            findings.append(f"sha256 mismatch: {row['path']}")
        if p.stat().st_size != row.get("bytes"):
            findings.append(f"size mismatch: {row['path']}")

    for extra in sorted(actual_paths - manifest_paths):
        findings.append(f"extra file not in manifest: {extra}")

    for missing in sorted(manifest_paths - actual_paths):
        findings.append(f"manifested file excluded or missing from tree: {missing}")

    if findings:
        print("manifest verification: FAIL")
        for f in findings:
            print(f"- {f}")
        return 1
    print(f"manifest verification: PASS ({len(rows)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
