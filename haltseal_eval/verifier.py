from __future__ import annotations

from typing import Any

from .action_digest import action_digest, audience_from_action, audience_key, validate_action_shape
from .canonicalization import CanonicalizationError
from .constants import (
    DEFAULT_MMD_SECONDS,
    PERMIT_CONTEXT,
    PUBLIC_EVAL_ELV_MEASUREMENT_HASH,
    PUBLIC_EVAL_ICC_HEAD_ID,
    PUBLIC_EVAL_JURISDICTIONAL_FINGERPRINT,
    PUBLIC_EVAL_LICENSE_TIER_ID,
    PUBLIC_EVAL_POLICY_EPOCH,
)
from .evidence import build_evidence_record
from .permit import validate_permit_status
from .replay import ReplayCache
from .signed_head import validate_signed_head
from .timeutils import parse_ts


_HOLD_HEAD_CODES = {"FRESHNESS_STALE", "HEAD_CONFLICT", "WITNESS_COSIGNATURE_MISSING"}


def _decision(packet: dict[str, Any] | Any, disposition: str, result_code: str, stage: str, digest: str | None) -> dict[str, Any]:
    vector_id = packet.get("vector_id") if isinstance(packet, dict) else None
    return {
        "vector_id": vector_id,
        "disposition": disposition,
        "result_code": result_code,
        "stage": stage,
        "evidence": build_evidence_record(packet=packet, disposition=disposition, result_code=result_code, stage=stage, action_digest=digest),
    }


def _policy_int(policy: dict[str, Any], field: str, default: int) -> int | None:
    value = policy.get(field, default)
    if isinstance(value, bool):
        return None
    try:
        out = int(value)
    except (TypeError, ValueError):
        return None
    if out < 0:
        return None
    return out


def _policy_bool(policy: dict[str, Any], field: str, default: bool) -> bool | None:
    value = policy.get(field, default)
    return value if isinstance(value, bool) else None


def _policy_str(policy: dict[str, Any], field: str, default: str) -> str | None:
    value = policy.get(field, default)
    return value if isinstance(value, str) and value else None


def _policy_str_list(policy: dict[str, Any], field: str) -> list[str] | None:
    value = policy.get(field, [])
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        return None
    return value


def _verify_packet_inner(packet: dict[str, Any], replay_cache: ReplayCache) -> dict[str, Any]:
    preload_ok, _ = replay_cache.preload(packet.get("preexisting_replay_state", []))
    if not preload_ok:
        return _decision(packet, "DENY", "REPLAY_STATE_INVALID", "ANTI_REPLAY", None)

    action = packet.get("action")
    if not isinstance(action, dict):
        return _decision(packet, "DENY", "ACTION_MISSING", "ACTION_BINDING", None)

    policy = packet.get("validation_policy")
    if not isinstance(policy, dict):
        return _decision(packet, "DENY", "VALIDATION_POLICY_INVALID", "PACKET_VALIDATION", None)

    packet_now = packet.get("now")
    policy_now = policy.get("now")
    if not isinstance(packet_now, str) or not isinstance(policy_now, str):
        return _decision(packet, "DENY", "VALIDATION_POLICY_INVALID", "PACKET_VALIDATION", None)
    if packet_now != policy_now:
        return _decision(packet, "DENY", "POLICY_NOW_MISMATCH", "PACKET_VALIDATION", None)
    try:
        parse_ts(packet_now)
    except (TypeError, ValueError):
        return _decision(packet, "DENY", "TIMESTAMP_INVALID", "PACKET_VALIDATION", None)

    required_context = _policy_str(policy, "required_context_label", PERMIT_CONTEXT)
    required_policy_epoch = _policy_str(policy, "required_policy_epoch", PUBLIC_EVAL_POLICY_EPOCH)
    required_icc_head_id = _policy_str(policy, "required_icc_head_id", PUBLIC_EVAL_ICC_HEAD_ID)
    required_license_tier_id = _policy_str(policy, "required_license_tier_id", PUBLIC_EVAL_LICENSE_TIER_ID)
    required_jurisdictional_fingerprint = _policy_str(policy, "required_jurisdictional_fingerprint", PUBLIC_EVAL_JURISDICTIONAL_FINGERPRINT)
    required_elv_measurement_hash = _policy_str(policy, "required_elv_measurement_hash", PUBLIC_EVAL_ELV_MEASUREMENT_HASH)
    revoked_raw = _policy_str_list(policy, "revoked_permit_ids")
    mmd = _policy_int(policy, "mmd_seconds", DEFAULT_MMD_SECONDS)
    required_witnesses = _policy_int(policy, "required_witness_cosigs", 1)
    require_continuity = _policy_bool(policy, "require_continuity_proof", True)
    require_elv_attestation_ref = _policy_bool(policy, "require_elv_attestation_ref", True)

    if None in (
        required_context,
        required_policy_epoch,
        required_icc_head_id,
        required_license_tier_id,
        required_jurisdictional_fingerprint,
        required_elv_measurement_hash,
        revoked_raw,
        mmd,
        required_witnesses,
        require_continuity,
        require_elv_attestation_ref,
    ):
        return _decision(packet, "DENY", "VALIDATION_POLICY_INVALID", "PACKET_VALIDATION", None)

    shape_findings = validate_action_shape(action, required_policy_epoch=required_policy_epoch)
    if shape_findings:
        if any(f.startswith("unsupported implementation hook") for f in shape_findings):
            code = "UNSUPPORTED_IMPLEMENTATION_HOOK"
        elif any(f == "unsupported protected action boundary" for f in shape_findings):
            code = "UNSUPPORTED_PROTECTED_ACTION"
        elif any(f == "policy_epoch outside configured public boundary" for f in shape_findings):
            code = "POLICY_EPOCH_MISMATCH"
        else:
            code = "ACTION_SHAPE_INVALID"
        return _decision(packet, "DENY", code, "BOUNDARY_MAPPER", None)

    digest = action_digest(action)
    permit = packet.get("permit")
    if not isinstance(permit, dict):
        return _decision(packet, "DENY", "PERMIT_MISSING", "PERMIT_STATUS", digest)

    revoked_ids = set(revoked_raw or [])
    ok, code, stage = validate_permit_status(permit, now=packet_now, required_context_label=required_context or PERMIT_CONTEXT, revoked_ids=revoked_ids)
    if not ok:
        return _decision(packet, "DENY", code, stage, digest)

    if permit.get("icc_head_id") != required_icc_head_id:
        return _decision(packet, "DENY", "ICC_HEAD_ID_MISMATCH", "ICC_BOUNDARY", digest)

    if permit.get("license_tier_id") != required_license_tier_id:
        return _decision(packet, "DENY", "LICENSE_TIER_MISMATCH", "GLG_GATE", digest)

    if permit.get("jurisdictional_fingerprint") != required_jurisdictional_fingerprint:
        return _decision(packet, "DENY", "JURISDICTIONAL_FINGERPRINT_MISMATCH", "GLG_GATE", digest)

    att = permit.get("elv_attestation_ref")
    if require_elv_attestation_ref and (not isinstance(att, dict) or att.get("measurement_hash") != required_elv_measurement_hash):
        return _decision(packet, "DENY", "ELV_ATTESTATION_MISMATCH", "ELV_ATTESTATION", digest)

    if permit.get("action_digest") != digest:
        return _decision(packet, "DENY", "ACTION_DIGEST_MISMATCH", "ACTION_BINDING", digest)

    expected_audience = audience_from_action(action)
    if permit.get("audience") != expected_audience:
        return _decision(packet, "DENY", "AUDIENCE_MISMATCH", "AUDIENCE_BINDING", digest)

    if permit.get("nonce") != action.get("nonce") or permit.get("monotonic_counter") != action.get("monotonic_counter"):
        return _decision(packet, "DENY", "PERMIT_REPLAY_TUPLE_MISMATCH", "ANTI_REPLAY", digest)

    if permit.get("signed_head_id") != action.get("signed_head_id"):
        return _decision(packet, "DENY", "SIGNED_HEAD_ID_MISMATCH", "FRESHNESS_CONTINUITY", digest)

    head = packet.get("signed_head")
    if isinstance(head, dict) and head.get("signed_head_id") != permit.get("signed_head_id"):
        return _decision(packet, "DENY", "SIGNED_HEAD_ID_MISMATCH", "FRESHNESS_CONTINUITY", digest)

    head_ok, head_code, head_stage = validate_signed_head(head, now=packet_now, mmd_seconds=mmd, required_witness_cosigs=required_witnesses)
    if not head_ok:
        disposition = "HOLD" if head_code in _HOLD_HEAD_CODES else "DENY"
        return _decision(packet, disposition, head_code, head_stage, digest)

    if require_continuity:
        proof = packet.get("continuity_proof") or {}
        if not isinstance(proof, dict):
            return _decision(packet, "HOLD", "PROOF_CONTINUITY_MISSING", "PROOF_CONTINUITY", digest)
        if proof.get("verified") is not True:
            return _decision(packet, "HOLD", "PROOF_CONTINUITY_MISSING", "PROOF_CONTINUITY", digest)
        if proof.get("current_signed_head_id") != permit.get("signed_head_id"):
            return _decision(packet, "HOLD", "PROOF_CONTINUITY_MISMATCH", "PROOF_CONTINUITY", digest)

    aud_key = audience_key(expected_audience)
    replay_ok, _ = replay_cache.record(aud_key, action["nonce"], action["monotonic_counter"])
    if not replay_ok:
        return _decision(packet, "DENY", "REPLAY_NONCE_MONOTONIC", "ANTI_REPLAY", digest)

    return _decision(packet, "ALLOW", "GATEWAY_PERMIT_CURRENT", "GATEWAY_COMMIT", digest)


def verify_packet(packet: dict[str, Any], replay_cache: ReplayCache | None = None) -> dict[str, Any]:
    """Verify a synthetic HALTSEAL gateway packet and return a fail-closed decision.

    This function is intentionally narrow: one protected action boundary, one permit,
    one signed-head posture, one evidence record. It is a public review artifact, not a
    production enforcement layer. Malformed public-eval input returns DENY rather than
    propagating parser exceptions.
    """
    if replay_cache is None:
        replay_cache = ReplayCache()
    if not isinstance(packet, dict):
        return _decision(packet, "DENY", "PACKET_SHAPE_INVALID", "PACKET_VALIDATION", None)
    try:
        return _verify_packet_inner(packet, replay_cache)
    except (CanonicalizationError, KeyError, TypeError, ValueError):
        return _decision(packet, "DENY", "MALFORMED_PACKET", "PACKET_VALIDATION", None)
