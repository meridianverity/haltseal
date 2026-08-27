#!/usr/bin/env python3
"""Verify HALTSEAL CPB identifier vectors from public receipt bytes.

Standard-library only. This runner intentionally tests only the CPB
`haltseal-public-resolve-receipt` identifier context:
SHA-256(RFC 7515 §5.1 JWS Signing Input) -> bare lowercase hex.
It does not exercise HALTSEAL's inner action/authority digest construction.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VECTOR_PATH = ROOT / "examples/cpb/haltseal-public-resolve-receipt-v1.json"
BARE_HEX_RE = re.compile(r"^[0-9a-f]{64}$")
B64URL_SEGMENT_RE = re.compile(rb"^[A-Za-z0-9_-]+$")

EXPECTED_TOP_LEVEL = {
    "artifact_type": "haltseal-public-resolve-receipt",
    "profile_version": "haltseal-public-resolve-1",
    "vector_set_version": "1.0",
    "algorithm": "as-transmitted",
    "hash": "SHA-256",
    "representation": "bare 64-character lowercase hex",
    "byte_boundary_selector": "RFC 7515 §5.1, JWS Signing Input",
    "source_commit": "6e1e4c1fabf97cf057cc3299dafb09c2ffe182c3",
    "source_profile": "docs/public-resolve/RECEIPT_PROFILE.md",
}


class VectorError(ValueError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_receipt(path: Path, expected_file_sha256: str) -> tuple[bytes, bytes]:
    raw = path.read_bytes()
    if _sha256(raw) != expected_file_sha256:
        raise VectorError(f"{path}: file SHA-256 does not match the pinned vector")

    if raw.endswith(b"\r\n"):
        raise VectorError(f"{path}: CRLF fixture framing is not permitted")
    token = raw[:-1] if raw.endswith(b"\n") else raw
    if not token or any(byte in b" \t\r\n" for byte in token):
        raise VectorError(f"{path}: compact JWS contains whitespace")

    parts = token.split(b".")
    if len(parts) != 3 or any(not B64URL_SEGMENT_RE.fullmatch(part) for part in parts):
        raise VectorError(f"{path}: expected three canonical base64url compact-JWS segments")

    signing_input = parts[0] + b"." + parts[1]
    return token, signing_input


def _positive_map(data: dict) -> dict[str, dict]:
    positives = data.get("positive")
    if not isinstance(positives, list) or not positives:
        raise VectorError("vector set requires at least one positive case")
    result: dict[str, dict] = {}
    for case in positives:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in result:
            raise VectorError("positive vector ids must be unique non-empty strings")
        result[case_id] = case
    return result


def verify_positive(case: dict) -> tuple[bytes, bytes]:
    receipt_path = ROOT / case["receipt_file"]
    token, signing_input = _load_receipt(receipt_path, case["receipt_file_sha256"])

    if case.get("preimage_selector") != "RFC 7515 §5.1, JWS Signing Input":
        raise VectorError(f"{case['id']}: selector drift")
    if len(signing_input) != case["preimage_length_bytes"]:
        raise VectorError(f"{case['id']}: pre-image length mismatch")

    digest = _sha256(signing_input)
    expected = case["expected_digest_bare_hex"]
    if not BARE_HEX_RE.fullmatch(expected):
        raise VectorError(f"{case['id']}: expected digest is not bare lowercase SHA-256 hex")
    if digest != expected:
        raise VectorError(f"{case['id']}: digest mismatch: expected {expected}, got {digest}")

    print(f"PASS {case['id']} {digest}")
    return token, signing_input


def verify_negative(case: dict, positives: dict[str, dict], runtime: dict[str, tuple[bytes, bytes]]) -> None:
    case_id = case["id"]
    source_id = case["source_positive"]
    if source_id not in positives or source_id not in runtime:
        raise VectorError(f"{case_id}: unknown source_positive {source_id!r}")

    source = positives[source_id]
    token, signing_input = runtime[source_id]
    expected = source["expected_digest_bare_hex"]

    if case_id == "hs-cpb-id-fail-01-full-jws-boundary":
        wrong = _sha256(token)
        if len(token) != case["wrong_preimage_length_bytes"]:
            raise VectorError(f"{case_id}: full-JWS length mismatch")
        if wrong != case["wrong_digest_bare_hex"] or wrong == expected:
            raise VectorError(f"{case_id}: full-JWS discriminator did not diverge")

    elif case_id == "hs-cpb-id-fail-02-signing-input-trailing-lf":
        mutated = signing_input + b"\n"
        wrong = _sha256(mutated)
        if len(mutated) != case["wrong_preimage_length_bytes"]:
            raise VectorError(f"{case_id}: mutated pre-image length mismatch")
        if wrong != case["wrong_digest_bare_hex"] or wrong == expected:
            raise VectorError(f"{case_id}: trailing-LF mutation did not diverge")

    elif case_id == "hs-cpb-id-fail-03-representation-prefix":
        bare = case["bare_form"]
        prefixed = case["invalid_prefixed_form"]
        if bare != expected or not BARE_HEX_RE.fullmatch(bare):
            raise VectorError(f"{case_id}: bare control value is invalid")
        if prefixed != "sha256:" + bare or BARE_HEX_RE.fullmatch(prefixed):
            raise VectorError(f"{case_id}: prefixed representation was silently accepted")

    elif case_id == "hs-cpb-id-fail-04-uppercase-hex":
        uppercase = case["invalid_uppercase_form"]
        if uppercase != expected.upper() or BARE_HEX_RE.fullmatch(uppercase):
            raise VectorError(f"{case_id}: uppercase representation was silently accepted")

    else:
        raise VectorError(f"{case_id}: runner has no assertion for this negative case")

    print(f"PASS {case_id}")


def main() -> int:
    try:
        data = json.loads(VECTOR_PATH.read_text(encoding="utf-8"))
        for key, expected in EXPECTED_TOP_LEVEL.items():
            if data.get(key) != expected:
                raise VectorError(f"top-level {key!r} drift: expected {expected!r}")

        positives = _positive_map(data)
        negatives = data.get("negative")
        if not isinstance(negatives, list) or not negatives:
            raise VectorError("vector set requires at least one MUST-FAIL/negative case")

        all_ids = set(positives)
        for case in negatives:
            case_id = case.get("id")
            if not isinstance(case_id, str) or not case_id or case_id in all_ids:
                raise VectorError("all vector ids must be unique non-empty strings")
            all_ids.add(case_id)

        runtime: dict[str, tuple[bytes, bytes]] = {}
        for case in data["positive"]:
            runtime[case["id"]] = verify_positive(case)
        for case in negatives:
            verify_negative(case, positives, runtime)

        if not any(case["id"] == "hs-cpb-id-fail-01-full-jws-boundary" for case in negatives):
            raise VectorError("primary byte-boundary discriminating vector is missing")

        print(
            f"CPB identifier vectors: PASS "
            f"({len(data['positive'])} positive, {len(negatives)} negative)"
        )
        print(f"vector_file_sha256: {_sha256(VECTOR_PATH.read_bytes())}")
        return 0
    except (KeyError, OSError, TypeError, json.JSONDecodeError, VectorError) as exc:
        print(f"CPB identifier vectors: FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
