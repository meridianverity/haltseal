#!/usr/bin/env python3
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_NAME_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}
FORBIDDEN_FILENAMES = {".DS_Store", ".env"}


def audit_names(names: list[str]) -> list[str]:
    findings: list[str] = []
    seen: set[str] = set()
    for raw in names:
        name = raw.rstrip("/")
        if not name:
            continue
        if name in seen:
            findings.append(f"duplicate archive member: {name}")
        seen.add(name)
        parts = set(Path(name).parts)
        suffix = Path(name).suffix.lower()
        if parts & FORBIDDEN_NAME_PARTS:
            findings.append(f"forbidden path member: {name}")
        if suffix in FORBIDDEN_SUFFIXES:
            findings.append(f"forbidden compiled artifact: {name}")
        if Path(name).name in FORBIDDEN_FILENAMES:
            findings.append(f"forbidden local file: {name}")
        if suffix == ".zip":
            findings.append(f"nested zip artifact is not allowed: {name}")
        if name.startswith("/") or ".." in Path(name).parts:
            findings.append(f"unsafe archive path: {name}")
    return findings


def names_from_tree(root: Path) -> list[str]:
    return [str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*") if p.is_file()]


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print("usage: python tools/zip_audit.py [release.zip]")
        return 2
    if len(argv) == 2:
        zpath = Path(argv[1])
        if not zpath.exists():
            print(f"zip audit: FAIL - missing file: {zpath}")
            return 1
        try:
            with zipfile.ZipFile(zpath, "r") as zf:
                findings = audit_names(zf.namelist())
                bad_test = zf.testzip()
                if bad_test:
                    findings.append(f"zip CRC failure: {bad_test}")
        except zipfile.BadZipFile as exc:
            print(f"zip audit: FAIL - bad zip: {exc}")
            return 1
    else:
        findings = audit_names(names_from_tree(ROOT))

    if findings:
        print("zip audit: FAIL")
        for f in findings:
            print(f"- {f}")
        return 1
    print("zip audit: PASS")
    print("findings: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
