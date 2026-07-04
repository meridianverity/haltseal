from __future__ import annotations

import re
from typing import Any

from .canonicalization import contextual_sha256
from .constants import (
    ACTION_CONTEXT,
    PUBLIC_EVAL_ACTION_TYPE,
    PUBLIC_EVAL_DESTINATION,
    PUBLIC_EVAL_IMPLEMENTATION_HOOK,
    PUBLIC_EVAL_METHOD,
)

REQUIRED_ACTION_FIELDS = [
    "action_id",
    "action_type",
    "method",
    "destination",
    "tenant_id",
    "agent_id",
    "mission_id",
    "payload_sha256",
    "policy_epoch",
    "implementation_hook",
    "signed_head_id",
    "nonce",
    "monotonic_counter",
]

_ALLOWED_ACTION_FIELDS = set(REQUIRED_ACTION_FIELDS)
_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
_STRING_FIELDS = {
    "action_id",
    "action_type",
    "method",
    "destination",
    "tenant_id",
    "agent_id",
    "mission_id",
    "payload_sha256",
    "policy_epoch",
    "implementation_hook",
    "signed_head_id",
}


def _is_int_not_bool(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def validate_action_shape(action: dict[str, Any], *, required_policy_epoch: str | None = None) -> list[str]:
    """Return public-eval findings for action-shape and boundary checks.

    The verifier intentionally reviews one protected action boundary. A permit
    cannot broaden that boundary by signing an otherwise well-formed but
    out-of-scope action, hook, destination, or policy epoch.
    """
    findings: list[str] = []
    for field in REQUIRED_ACTION_FIELDS:
        if field not in action:
            findings.append(f"missing action field: {field}")

    for field in sorted(set(action) - _ALLOWED_ACTION_FIELDS):
        findings.append(f"unknown action field: {field}")

    for field in sorted(_STRING_FIELDS & set(action)):
        if not _non_empty_string(action[field]):
            findings.append(f"{field} must be a non-empty string")

    if "payload_sha256" in action and isinstance(action.get("payload_sha256"), str) and not _HEX_64.fullmatch(action["payload_sha256"]):
        findings.append("payload_sha256 must be 64 lowercase hexadecimal characters")

    for int_field in ("nonce", "monotonic_counter"):
        if int_field in action:
            if not _is_int_not_bool(action[int_field]):
                findings.append(f"{int_field} must be an integer")
            elif action[int_field] < 0:
                findings.append(f"{int_field} must be non-negative")

    if action.get("implementation_hook") != PUBLIC_EVAL_IMPLEMENTATION_HOOK:
        findings.append(f"unsupported implementation hook: {action.get('implementation_hook')}")

    if (
        action.get("action_type") != PUBLIC_EVAL_ACTION_TYPE
        or action.get("method") != PUBLIC_EVAL_METHOD
        or action.get("destination") != PUBLIC_EVAL_DESTINATION
    ):
        findings.append("unsupported protected action boundary")

    if required_policy_epoch is not None and action.get("policy_epoch") != required_policy_epoch:
        findings.append("policy_epoch outside configured public boundary")

    return findings


def action_digest(action: dict[str, Any]) -> str:
    return contextual_sha256(ACTION_CONTEXT, action)


def audience_from_action(action: dict[str, Any]) -> dict[str, str]:
    return {
        "agent_id": str(action["agent_id"]),
        "tenant_id": str(action["tenant_id"]),
        "mission_id": str(action["mission_id"]),
    }


def audience_key(audience: dict[str, str]) -> str:
    return f"{audience.get('tenant_id')}::{audience.get('agent_id')}::{audience.get('mission_id')}"
