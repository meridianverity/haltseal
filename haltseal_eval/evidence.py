from __future__ import annotations

from typing import Any

from .canonicalization import contextual_sha256
from .constants import IAL_CONTEXT, PUBLIC_BOUNDARY_NOTICE
from .synthetic_crypto import signature_block


def _object_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def build_evidence_record(*, packet: dict[str, Any] | Any, disposition: str, result_code: str, stage: str, action_digest: str | None) -> dict[str, Any]:
    safe_packet = _object_or_empty(packet)
    action = _object_or_empty(safe_packet.get("action"))
    permit = _object_or_empty(safe_packet.get("permit"))
    head = _object_or_empty(safe_packet.get("signed_head"))
    att = _object_or_empty(permit.get("elv_attestation_ref"))
    record = {
        "context_label": IAL_CONTEXT,
        "event_type": disposition,
        "ts": safe_packet.get("now"),
        "result_code": result_code,
        "stage": stage,
        "disposition": disposition,
        "action_id": action.get("action_id"),
        "action_digest": action_digest,
        "policy_epoch": action.get("policy_epoch"),
        "permit_id": permit.get("permit_id"),
        "icc_head_id": permit.get("icc_head_id"),
        "signed_head_id": head.get("signed_head_id") or permit.get("signed_head_id"),
        "license_tier_id": permit.get("license_tier_id"),
        "jurisdictional_fingerprint": permit.get("jurisdictional_fingerprint"),
        "elv_measurement_hash": att.get("measurement_hash"),
        "implementation_hook": action.get("implementation_hook"),
        "audience": {
            "agent_id": action.get("agent_id"),
            "tenant_id": action.get("tenant_id"),
            "mission_id": action.get("mission_id"),
        },
        "public_boundary": PUBLIC_BOUNDARY_NOTICE,
    }
    signable = dict(record)
    signable["evidence_hash"] = contextual_sha256(IAL_CONTEXT, record)
    record["evidence_hash"] = signable["evidence_hash"]
    record["evidence_sig"] = signature_block(IAL_CONTEXT, signable)
    return record
