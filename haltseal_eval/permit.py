from __future__ import annotations

import re
from typing import Any

from .constants import PERMIT_CONTEXT
from .synthetic_crypto import signature_block, verify_signature_block
from .timeutils import parse_ts

_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_PERMIT_FIELDS = [
    "context_label",
    "permit_id",
    "audience",
    "issued_ts",
    "expiration_ts",
    "icc_head_id",
    "signed_head_id",
    "license_tier_id",
    "jurisdictional_fingerprint",
    "nonce",
    "monotonic_counter",
    "action_digest",
    "revoked",
    "elv_attestation_ref",
    "signature",
]
_STRING_FIELDS = {
    "context_label",
    "permit_id",
    "issued_ts",
    "expiration_ts",
    "icc_head_id",
    "signed_head_id",
    "license_tier_id",
    "jurisdictional_fingerprint",
    "action_digest",
}
_AUDIENCE_FIELDS = {"agent_id", "tenant_id", "mission_id"}


def _is_int_not_bool(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def permit_signable_view(permit: dict[str, Any]) -> dict[str, Any]:
    view = dict(permit)
    view.pop("signature", None)
    return view


def sign_permit(permit: dict[str, Any]) -> dict[str, Any]:
    out = dict(permit)
    out["signature"] = signature_block(PERMIT_CONTEXT, permit_signable_view(out))
    return out


def validate_permit_signature(permit: dict[str, Any]) -> bool:
    return verify_signature_block(PERMIT_CONTEXT, permit_signable_view(permit), permit.get("signature"))


def validate_permit_shape(permit: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for field in _REQUIRED_PERMIT_FIELDS:
        if field not in permit:
            findings.append(f"missing permit field: {field}")

    for field in sorted(_STRING_FIELDS & set(permit)):
        if not _non_empty_string(permit[field]):
            findings.append(f"{field} must be a non-empty string")

    if "action_digest" in permit and isinstance(permit.get("action_digest"), str) and not _HEX_64.fullmatch(permit["action_digest"]):
        findings.append("action_digest must be 64 lowercase hexadecimal characters")

    audience = permit.get("audience")
    if not isinstance(audience, dict):
        findings.append("audience must be an object")
    else:
        missing = sorted(_AUDIENCE_FIELDS - set(audience))
        extra = sorted(set(audience) - _AUDIENCE_FIELDS)
        for field in missing:
            findings.append(f"missing audience field: {field}")
        for field in extra:
            findings.append(f"unknown audience field: {field}")
        for field in sorted(_AUDIENCE_FIELDS & set(audience)):
            if not _non_empty_string(audience[field]):
                findings.append(f"audience.{field} must be a non-empty string")

    for int_field in ("nonce", "monotonic_counter"):
        if int_field in permit:
            if not _is_int_not_bool(permit[int_field]):
                findings.append(f"{int_field} must be an integer")
            elif permit[int_field] < 0:
                findings.append(f"{int_field} must be non-negative")

    if not isinstance(permit.get("revoked"), bool):
        findings.append("revoked must be a boolean")

    signature = permit.get("signature")
    if not isinstance(signature, dict):
        findings.append("signature must be an object")
    else:
        for field in ("alg", "kid", "sig"):
            if not _non_empty_string(signature.get(field)):
                findings.append(f"signature.{field} must be a non-empty string")

    att = permit.get("elv_attestation_ref")
    if not isinstance(att, dict):
        findings.append("elv_attestation_ref must be an object")
    else:
        measurement = att.get("measurement_hash")
        if not isinstance(measurement, str) or not _HEX_64.fullmatch(measurement):
            findings.append("elv_attestation_ref.measurement_hash must be 64 lowercase hexadecimal characters")
        if not _non_empty_string(att.get("quote")):
            findings.append("elv_attestation_ref.quote must be a non-empty string")
        cert_chain = att.get("cert_chain")
        if not isinstance(cert_chain, list) or not cert_chain or not all(_non_empty_string(x) for x in cert_chain):
            findings.append("elv_attestation_ref.cert_chain must be a non-empty string array")

    return findings


def validate_permit_status(permit: dict[str, Any], *, now: str, required_context_label: str, revoked_ids: set[str]) -> tuple[bool, str, str]:
    if not isinstance(permit, dict):
        return False, "PERMIT_MISSING", "PERMIT_STATUS"
    if permit.get("context_label") != required_context_label:
        return False, "CONTEXT_LABEL_MISMATCH", "CANONICALIZATION"
    if validate_permit_shape(permit):
        return False, "PERMIT_SHAPE_INVALID", "PERMIT_STATUS"
    if not validate_permit_signature(permit):
        return False, "PERMIT_SIGNATURE_INVALID", "PERMIT_STATUS"
    permit_id = str(permit.get("permit_id", ""))
    if permit.get("revoked") is True or permit_id in revoked_ids:
        return False, "PERMIT_REVOKED", "PERMIT_STATUS"
    try:
        n = parse_ts(now)
        issued = parse_ts(permit["issued_ts"])
        expires = parse_ts(permit["expiration_ts"])
    except (KeyError, TypeError, ValueError):
        return False, "PERMIT_TIMESTAMP_INVALID", "PERMIT_STATUS"
    if issued >= expires:
        return False, "PERMIT_TIME_RANGE_INVALID", "PERMIT_STATUS"
    if issued > n:
        return False, "PERMIT_NOT_YET_VALID", "PERMIT_STATUS"
    if expires <= n:
        return False, "PERMIT_EXPIRED", "PERMIT_STATUS"
    return True, "PERMIT_OK", "PERMIT_STATUS"
