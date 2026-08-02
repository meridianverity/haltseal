#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
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



def build_source_tree() -> list[str]:
    rows: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if set(rel.parts) & EXCLUDE_PARTS:
            continue
        if path.suffix.lower() in EXCLUDE_SUFFIXES:
            continue
        rows.append(str(rel).replace("\\", "/"))
    for name in ("MANIFEST.json", "MANIFEST.sha256.json"):
        if name not in rows:
            rows.append(name)
    return sorted(rows)

def main() -> int:
    source_tree = build_source_tree()
    (ROOT / "SOURCE_TREE.txt").write_text("\n".join(source_tree) + "\n", encoding="utf-8")
    rows = build_manifest()
    (ROOT / "MANIFEST.json").write_text(json.dumps({"artifact": "haltseal-public-resolve-challenge", "version": VERSION, "files": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / "MANIFEST.sha256.json").write_text(json.dumps({row["path"]: row["sha256"] for row in rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"manifest: wrote {len(rows)} file entries")
    print(f"source tree: wrote {len(source_tree)} file entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
