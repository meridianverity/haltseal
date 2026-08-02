from __future__ import annotations

import re
from typing import Any

from .constants import BOUNDARY, ISSUER, PROFILE_VERSION, RECEIPT_AUDIENCE
from .models import ValidationError, validate_action, validate_authority

RECEIPT_FIELDS = {
    "iss", "aud", "jti", "iat", "profile_version", "challenge_id",
    "authority", "authority_digest", "action", "action_digest", "decision",
    "reason_codes", "emission", "consumption", "boundary",
}
EMISSION_FIELDS = {
    "disposition", "synthetic_request_record_id", "existing_request_record_id",
    "new_request_count", "total_request_count_for_use", "outcome",
}
CONSUMPTION_FIELDS = {"state_before", "state_after"}

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_RECEIPT_ID = re.compile(r"^hsr_[a-z0-9_]{8,80}$")
_CHALLENGE_ID = re.compile(r"^hsc_[a-z0-9_]{8,80}$")
_REQUEST_ID = re.compile(r"^hsreq_[a-z0-9_]{8,80}$")
_REASON = re.compile(r"^[A-Z0-9_]{3,64}$")


class ReceiptProfileError(ValueError):
    pass


def _exact_object(value: Any, fields: set[str], label: str) -> dict:
    if not isinstance(value, dict):
        raise ReceiptProfileError(f"{label} must be an object")
    actual = set(value)
    if actual != fields:
        missing = sorted(fields - actual)
        extra = sorted(actual - fields)
        raise ReceiptProfileError(f"{label} field set mismatch; missing={missing} extra={extra}")
    return value


def _exact_string(value: Any, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ReceiptProfileError(f"{label} is invalid")
    return value


def _nullable_request_id(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _exact_string(value, _REQUEST_ID, label)


def _exact_int(value: Any, minimum: int, maximum: int, label: str) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ReceiptProfileError(f"{label} must be an integer from {minimum} through {maximum}")
    return value


def validate_receipt_payload(payload: Any) -> tuple[dict, dict, dict, dict]:
    """Validate the complete closed receipt profile before semantic replay.

    Returns normalized copies of authority, action, emission, and consumption.
    """
    p = _exact_object(payload, RECEIPT_FIELDS, "receipt payload")

    if p["iss"] != ISSUER:
        raise ReceiptProfileError("receipt issuer mismatch")
    if p["aud"] != RECEIPT_AUDIENCE:
        raise ReceiptProfileError("receipt audience mismatch")
    if p["profile_version"] != PROFILE_VERSION:
        raise ReceiptProfileError("receipt profile version mismatch")

    _exact_string(p["jti"], _RECEIPT_ID, "receipt jti")
    _exact_int(p["iat"], 0, 2**63 - 1, "receipt iat")
    _exact_string(p["challenge_id"], _CHALLENGE_ID, "challenge_id")
    _exact_string(p["authority_digest"], _DIGEST, "authority_digest")
    _exact_string(p["action_digest"], _DIGEST, "action_digest")

    if p["decision"] not in {"ACCEPT", "HOLD", "REFUSE"}:
        raise ReceiptProfileError("decision is invalid")
    reasons = p["reason_codes"]
    if not isinstance(reasons, list) or not reasons:
        raise ReceiptProfileError("reason_codes must be a non-empty array")
    if any(not isinstance(v, str) or not _REASON.fullmatch(v) for v in reasons):
        raise ReceiptProfileError("reason_codes contains an invalid value")
    if len(reasons) != len(set(reasons)):
        raise ReceiptProfileError("reason_codes must be unique")

    if p["boundary"] != BOUNDARY:
        raise ReceiptProfileError("boundary mismatch")

    try:
        authority = validate_authority(p["authority"])
        action = validate_action(p["action"])
    except ValidationError as exc:
        raise ReceiptProfileError(str(exc)) from exc

    e = _exact_object(p["emission"], EMISSION_FIELDS, "emission")
    c = _exact_object(p["consumption"], CONSUMPTION_FIELDS, "consumption")

    if e["disposition"] not in {"ONE_SYNTHETIC_REQUEST", "NO_REQUEST", "NO_NEW_REQUEST"}:
        raise ReceiptProfileError("emission disposition is invalid")
    if e["outcome"] not in {"RECORDED", "NONE", "UNKNOWN"}:
        raise ReceiptProfileError("emission outcome is invalid")
    synthetic_id = _nullable_request_id(e["synthetic_request_record_id"], "synthetic_request_record_id")
    existing_id = _nullable_request_id(e["existing_request_record_id"], "existing_request_record_id")
    new_count = _exact_int(e["new_request_count"], 0, 1, "new_request_count")
    total_count = _exact_int(e["total_request_count_for_use"], 0, 1, "total_request_count_for_use")

    if c["state_before"] not in {"AVAILABLE", "CONSUMED"} or c["state_after"] not in {"AVAILABLE", "CONSUMED"}:
        raise ReceiptProfileError("consumption state is invalid")

    decision = p["decision"]
    if decision == "ACCEPT":
        expected_emission = {
            "disposition": "ONE_SYNTHETIC_REQUEST",
            "synthetic_request_record_id": synthetic_id,
            "existing_request_record_id": None,
            "new_request_count": 1,
            "total_request_count_for_use": 1,
            "outcome": "RECORDED",
        }
        if synthetic_id is None or dict(e) != expected_emission:
            raise ReceiptProfileError("ACCEPT emission invariant failed")
        if dict(c) != {"state_before": "AVAILABLE", "state_after": "CONSUMED"}:
            raise ReceiptProfileError("ACCEPT consumption invariant failed")
    elif decision == "HOLD":
        expected_emission = {
            "disposition": "NO_NEW_REQUEST",
            "synthetic_request_record_id": None,
            "existing_request_record_id": existing_id,
            "new_request_count": 0,
            "total_request_count_for_use": 1,
            "outcome": "UNKNOWN",
        }
        if existing_id is None or dict(e) != expected_emission:
            raise ReceiptProfileError("HOLD emission invariant failed")
        if dict(c) != {"state_before": "CONSUMED", "state_after": "CONSUMED"}:
            raise ReceiptProfileError("HOLD consumption invariant failed")
    else:
        if c["state_before"] != c["state_after"]:
            raise ReceiptProfileError("REFUSE consumption must not change state")
        expected_total = 1 if c["state_before"] == "CONSUMED" else 0
        expected_emission = {
            "disposition": "NO_REQUEST",
            "synthetic_request_record_id": None,
            "existing_request_record_id": None,
            "new_request_count": 0,
            "total_request_count_for_use": expected_total,
            "outcome": "NONE",
        }
        if dict(e) != expected_emission:
            raise ReceiptProfileError("REFUSE emission invariant failed")

    return authority, action, dict(e), dict(c)
