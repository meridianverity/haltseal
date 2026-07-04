#!/usr/bin/env python3
"""
HALTSEAL v0.3.1 hidden-files restore helper.

This file is intentionally NOT hidden. It reconstructs the four hidden repository
files that can be lost when manual upload tools ignore dotfiles or .github/.

Default behavior: create missing hidden files and refuse to overwrite different
existing files unless --force is supplied.
Recommended command from the repository root:

    python HALTSEAL_HIDDEN_FILES_RESTORE.py --force --cleanup

After success, run:

    python verify_manifest.py
    python -m pytest -q
    python tools/release_gate.py
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import os
from pathlib import Path
import sys

FILES = [
  {
    "target_path": ".gitignore",
    "size": 76,
    "sha256": "2200de0e4fef993523606dbe5aa38248c61bffdd3cb57692b8c72959d8f2886d",
    "base64": "X19weWNhY2hlX18vCioucHljCi5weXRlc3RfY2FjaGUvCi52ZW52LwpkaXN0LwpidWlsZC8KKi5lZ2ctaW5mby8KLkRTX1N0b3JlCg=="
  },
  {
    "target_path": ".github/workflows/public-eval.yml",
    "size": 1171,
    "sha256": "bedd3fc966be51462ead548c4e523cf84f1fe65111b7f93214aef3464c9c3e70",
    "base64": "bmFtZTogSEFMVFNFQUwgcHVibGljIGV2YWx1YXRpb24KCm9uOgogIHB1c2g6CiAgcHVsbF9yZXF1ZXN0OgoKam9iczoKICBwdWJsaWMtZXZhbDoKICAgIHJ1bnMtb246IHVidW50dS1sYXRlc3QKICAgIGVudjoKICAgICAgUFlUSE9ORE9OVFdSSVRFQllURUNPREU6ICIxIgogICAgc3RlcHM6CiAgICAgIC0gdXNlczogYWN0aW9ucy9jaGVja291dEB2NAogICAgICAtIHVzZXM6IGFjdGlvbnMvc2V0dXAtcHl0aG9uQHY1CiAgICAgICAgd2l0aDoKICAgICAgICAgIHB5dGhvbi12ZXJzaW9uOiAnMy4xMScKICAgICAgLSBuYW1lOiBJbnN0YWxsIHRlc3QgZGVwZW5kZW5jeQogICAgICAgIHJ1bjogcHl0aG9uIC1tIHBpcCBpbnN0YWxsIC1yIHJlcXVpcmVtZW50cy50eHQKICAgICAgLSBuYW1lOiBSZWdlbmVyYXRlIGRldGVybWluaXN0aWMgdmVjdG9ycwogICAgICAgIHJ1bjogcHl0aG9uIHRvb2xzL3JlZ2VuZXJhdGVfdmVjdG9ycy5weQogICAgICAtIG5hbWU6IFJ1biBwdWJsaWMgZXZhbHVhdGlvbgogICAgICAgIHJ1bjogcHl0aG9uIHRvb2xzL3J1bl9wdWJsaWNfZXZhbC5weQogICAgICAtIG5hbWU6IFZhbGlkYXRlIHBhY2tldCBib3VuZGFyeQogICAgICAgIHJ1bjogcHl0aG9uIHRvb2xzL3ZhbGlkYXRlX3B1YmxpY19wYWNrZXQucHkKICAgICAgLSBuYW1lOiBHZW5lcmF0ZSB0cmFuc3BhcmVuY3kgcmVwb3J0CiAgICAgICAgcnVuOiBweXRob24gdG9vbHMvZ2VuZXJhdGVfdHJhbnNwYXJlbmN5X3JlcG9ydC5weQogICAgICAtIG5hbWU6IEdlbmVyYXRlIHN5bnRoZXRpYyBldmFsdWF0aW9uIGF0dGVzdGF0aW9uCiAgICAgICAgcnVuOiBweXRob24gdG9vbHMvZ2VuZXJhdGVfYXR0ZXN0YXRpb24ucHkKICAgICAgLSBuYW1lOiBDaGVjayBtYW5pZmVzdAogICAgICAgIHJ1bjogcHl0aG9uIHRvb2xzL21ha2VfbWFuaWZlc3QucHkgJiYgcHl0aG9uIHZlcmlmeV9tYW5pZmVzdC5weQogICAgICAtIG5hbWU6IFJ1biB0ZXN0cwogICAgICAgIHJ1bjogcHl0aG9uIC1tIHB5dGVzdCAtcQogICAgICAtIG5hbWU6IFJlbGVhc2UgZ2F0ZQogICAgICAgIHJ1bjogcHl0aG9uIHRvb2xzL3JlbGVhc2VfZ2F0ZS5weQogICAgICAtIG5hbWU6IFppcCBoeWdpZW5lIGF1ZGl0CiAgICAgICAgcnVuOiBtYWtlIGNsZWFuLWNhY2hlcyAmJiBweXRob24gdG9vbHMvemlwX2F1ZGl0LnB5Cg=="
  },
  {
    "target_path": ".github/pull_request_template.md",
    "size": 430,
    "sha256": "e2c1ee3860e523004ffd52eb91debed7a00851c2a27c2416990bbf5d820bd6e4",
    "base64": "IyBQdWJsaWMtZXZhbCBwdWxsIHJlcXVlc3QKCiMjIFNjb3BlCgotIFsgXSBTeW50aGV0aWMgZXZhbHVhdGlvbiBvbmx5Ci0gWyBdIE5vIGltcGxlbWVudGF0aW9uLWRlcHRoIG1hdGVyaWFsCi0gWyBdIE5vIHByaXZhdGUgbGVnYWwgbWFwcGluZwotIFsgXSBObyB0YXJnZXQtc3BlY2lmaWMgYW5hbHlzaXMKLSBbIF0gTm8gY29tbWVyY2lhbCB0ZXJtcwotIFsgXSBObyBwYXRlbnQtbGljZW5zZSB0ZXJtcwoKIyMgQ2hlY2tzCgpgYGBiYXNoCnB5dGhvbiB0b29scy9ydW5fcHVibGljX2V2YWwucHkKcHl0aG9uIHRvb2xzL3ZhbGlkYXRlX3B1YmxpY19wYWNrZXQucHkKcHl0aG9uIHRvb2xzL21ha2VfbWFuaWZlc3QucHkKcHl0aG9uIHZlcmlmeV9tYW5pZmVzdC5weQpweXRob24gLW0gcHl0ZXN0IC1xCnB5dGhvbiB0b29scy9yZWxlYXNlX2dhdGUucHkKYGBgCg=="
  },
  {
    "target_path": ".github/ISSUE_TEMPLATE/boundary_question.md",
    "size": 323,
    "sha256": "a8d3dd9cb9382867112796b474afb4ec701f3bfc00f9849d8464eaaa380bc6aa",
    "base64": "LS0tCm5hbWU6IEJvdW5kYXJ5IHF1ZXN0aW9uCmFib3V0OiBBc2sgYWJvdXQgdGhlIHN5bnRoZXRpYyBwdWJsaWMgZXZhbHVhdGlvbiBib3VuZGFyeQpsYWJlbHM6IGJvdW5kYXJ5LCBwdWJsaWMtZXZhbAotLS0KCiMjIFF1ZXN0aW9uCgojIyBGaWxlIG9yIHZlY3RvcgoKIyMgV2h5IGl0IG1hdHRlcnMgZm9yIHB1YmxpYyByZXZpZXcKClBsZWFzZSBkbyBub3QgaW5jbHVkZSBzZWNyZXRzLCBjb25maWRlbnRpYWwgZGVwbG95bWVudCBkZXRhaWxzLCBwcml2YXRlIGxlZ2FsIG1hcHBpbmcsIHRhcmdldC1zcGVjaWZpYyBhbmFseXNpcywgb3IgbGljZW5zaW5nIHRlcm1zLgo="
  }
]

OVERLAY_HELPER_FILES = [
    "HALTSEAL_HIDDEN_FILES_RESTORE.py",
    "HALTSEAL_HIDDEN_FILES_MANUAL.md",
    "HALTSEAL_HIDDEN_FILES_RESTORE_MANIFEST.json",
    "HALTSEAL_HIDDEN_FILES_SHA256SUMS.txt",
]

SOURCE_ZIP_SHA256 = "3f2cb8fdea32fa2d7516494b2cd7e0467d8a5fa92baa92d28fca7f92af970412"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def decode_record(record: dict[str, str]) -> bytes:
    data = base64.b64decode(record["base64"].encode("ascii"))
    actual = sha256_bytes(data)
    if actual != record["sha256"]:
        raise SystemExit(f"embedded content hash mismatch for {record['target_path']}: {actual}")
    if len(data) != int(record["size"]):
        raise SystemExit(f"embedded content size mismatch for {record['target_path']}")
    return data


def cleanup_overlay_files(repo_root: Path, script_path: Path | None) -> list[str]:
    removed: list[str] = []
    candidates = [repo_root / name for name in OVERLAY_HELPER_FILES]
    if script_path is not None:
        candidates.append(script_path)
    seen: set[Path] = set()
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved in seen:
            continue
        seen.add(resolved)
        try:
            if path.exists() and path.is_file():
                path.unlink()
                removed.append(str(path))
        except OSError as exc:
            print(f"cleanup warning: could not remove {path}: {exc}", file=sys.stderr)
    return removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Restore HALTSEAL hidden files from an unhidden upload helper.")
    parser.add_argument("--repo-root", default=".", help="repository root to modify; default: current directory")
    parser.add_argument("--force", action="store_true", help="overwrite existing hidden files if their content differs")
    parser.add_argument("--check", action="store_true", help="verify hidden files only; do not write")
    parser.add_argument("--dry-run", action="store_true", help="show actions without writing")
    parser.add_argument("--cleanup", action="store_true", help="delete visible overlay helper files after successful restore")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        print(f"repo root does not exist: {repo_root}", file=sys.stderr)
        return 2

    failures: list[str] = []
    writes: list[str] = []
    already_ok: list[str] = []

    for record in FILES:
        rel = record["target_path"]
        target = repo_root / rel
        expected_hash = record["sha256"]
        data = decode_record(record)

        if target.exists():
            actual_hash = sha256_file(target)
            if actual_hash == expected_hash:
                already_ok.append(rel)
                continue
            if args.check:
                failures.append(f"{rel} hash mismatch: expected {expected_hash}, got {actual_hash}")
                continue
            if not args.force:
                failures.append(f"{rel} exists but differs; rerun with --force to overwrite")
                continue
        elif args.check:
            failures.append(f"{rel} is missing")
            continue

        if not args.check:
            writes.append(rel)
            if not args.dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                tmp = target.with_name(target.name + ".tmp-haltseal-hidden-restore")
                tmp.write_bytes(data)
                os.replace(tmp, target)
                actual_hash = sha256_file(target)
                if actual_hash != expected_hash:
                    failures.append(f"{rel} restore hash mismatch after write: {actual_hash}")

    if failures:
        print("HALTSEAL hidden-files restore: FAIL")
        for item in failures:
            print(f"- {item}")
        return 1

    if args.check:
        print(f"HALTSEAL hidden-files check: PASS ({len(already_ok)} / {len(FILES)} present and exact)")
        return 0

    if args.dry_run:
        print("HALTSEAL hidden-files restore dry-run: PASS")
        for rel in writes:
            print(f"would write: {rel}")
        for rel in already_ok:
            print(f"already exact: {rel}")
        return 0

    print(f"HALTSEAL hidden-files restore: PASS (wrote {len(writes)}, already exact {len(already_ok)})")
    for rel in writes:
        print(f"wrote: {rel}")
    for rel in already_ok:
        print(f"already exact: {rel}")

    if args.cleanup:
        script_path: Path | None = None
        try:
            script_path = Path(__file__).resolve()
        except NameError:
            script_path = None
        removed = cleanup_overlay_files(repo_root, script_path)
        if removed:
            print("cleanup: removed visible overlay helper files")
            for path in removed:
                print(f"removed: {path}")
        else:
            print("cleanup: no visible overlay helper files found")

    print("next verification commands:")
    print("  python verify_manifest.py")
    print("  python -m pytest -q")
    print("  python tools/release_gate.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
