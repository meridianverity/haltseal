from __future__ import annotations

import re
from typing import Any

from .constants import SIGNED_HEAD_CONTEXT
from .synthetic_crypto import signature_block, verify_signature_block
from .timeutils import seconds_between

_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_HEAD_FIELDS = ["signed_head_id", "log_id", "tree_size", "root_hash", "timestamp", "witness_cosigs", "signature"]
_STRING_FIELDS = {"signed_head_id", "log_id", "root_hash", "timestamp"}


def _is_int_not_bool(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def signed_head_signable_view(head: dict[str, Any]) -> dict[str, Any]:
    view = dict(head)
    view.pop("signature", None)
    return view


def sign_signed_head(head: dict[str, Any]) -> dict[str, Any]:
    out = dict(head)
    out["signature"] = signature_block(SIGNED_HEAD_CONTEXT, signed_head_signable_view(out))
    return out


def validate_signed_head_shape(head: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for field in _REQUIRED_HEAD_FIELDS:
        if field not in head:
            findings.append(f"missing signed head field: {field}")

    for field in sorted(_STRING_FIELDS & set(head)):
        if not _non_empty_string(head[field]):
            findings.append(f"{field} must be a non-empty string")

    if "root_hash" in head and isinstance(head.get("root_hash"), str) and not _HEX_64.fullmatch(head["root_hash"]):
        findings.append("root_hash must be 64 lowercase hexadecimal characters")

    if "tree_size" in head:
        if not _is_int_not_bool(head["tree_size"]):
            findings.append("tree_size must be an integer")
        elif head["tree_size"] < 0:
            findings.append("tree_size must be non-negative")

    witnesses = head.get("witness_cosigs")
    if not isinstance(witnesses, list):
        findings.append("witness_cosigs must be an array")
    else:
        for i, witness in enumerate(witnesses):
            if not isinstance(witness, dict):
                findings.append(f"witness_cosigs[{i}] must be an object")
                continue
            if not _non_empty_string(witness.get("witness_id")):
                findings.append(f"witness_cosigs[{i}].witness_id must be a non-empty string")
            if not _non_empty_string(witness.get("sig")):
                findings.append(f"witness_cosigs[{i}].sig must be a non-empty string")

    if "status" in head and head.get("status") not in {"ok", "conflict"}:
        findings.append("status must be ok or conflict when present")

    signature = head.get("signature")
    if not isinstance(signature, dict):
        findings.append("signature must be an object")
    else:
        for field in ("alg", "kid", "sig"):
            if not _non_empty_string(signature.get(field)):
                findings.append(f"signature.{field} must be a non-empty string")

    return findings


def validate_signed_head(head: dict[str, Any], *, now: str, mmd_seconds: int, required_witness_cosigs: int) -> tuple[bool, str, str]:
    if not isinstance(head, dict):
        return False, "SIGNED_HEAD_MISSING", "FRESHNESS_CONTINUITY"
    if validate_signed_head_shape(head):
        return False, "SIGNED_HEAD_SHAPE_INVALID", "FRESHNESS_CONTINUITY"
    if not verify_signature_block(SIGNED_HEAD_CONTEXT, signed_head_signable_view(head), head.get("signature")):
        return False, "SIGNED_HEAD_SIGNATURE_INVALID", "FRESHNESS_CONTINUITY"
    witnesses = head.get("witness_cosigs") or []
    if len(witnesses) < required_witness_cosigs:
        return False, "WITNESS_COSIGNATURE_MISSING", "FRESHNESS_CONTINUITY"
    if head.get("status") == "conflict":
        return False, "HEAD_CONFLICT", "FRESHNESS_CONTINUITY"
    try:
        age = seconds_between(now, head["timestamp"])
    except (KeyError, TypeError, ValueError):
        return False, "SIGNED_HEAD_TIMESTAMP_INVALID", "FRESHNESS_CONTINUITY"
    if age < 0:
        return False, "SIGNED_HEAD_FROM_FUTURE", "FRESHNESS_CONTINUITY"
    if age > mmd_seconds:
        return False, "FRESHNESS_STALE", "FRESHNESS_CONTINUITY"
    return True, "SIGNED_HEAD_OK", "FRESHNESS_CONTINUITY"
