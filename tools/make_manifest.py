#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


def build_manifest() -> list[dict]:
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if include_file(path):
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return rows


def main() -> int:
    rows = build_manifest()
    (ROOT / "MANIFEST.json").write_text(json.dumps({"artifact": "haltseal-gateway-proof-pack", "version": "0.3.0-public-eval", "files": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / "MANIFEST.sha256.json").write_text(json.dumps({row["path"]: row["sha256"] for row in rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"manifest: wrote {len(rows)} file entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
