from __future__ import annotations

from copy import deepcopy
from typing import Any

from .action_digest import action_digest, audience_from_action, audience_key
from .constants import (
    DEFAULT_MMD_SECONDS,
    DEFAULT_NOW,
    PERMIT_CONTEXT,
    PUBLIC_BOUNDARY_NOTICE,
    PUBLIC_EVAL_ACTION_TYPE,
    PUBLIC_EVAL_DESTINATION,
    PUBLIC_EVAL_ELV_MEASUREMENT_HASH,
    PUBLIC_EVAL_ICC_HEAD_ID,
    PUBLIC_EVAL_IMPLEMENTATION_HOOK,
    PUBLIC_EVAL_JURISDICTIONAL_FINGERPRINT,
    PUBLIC_EVAL_LICENSE_TIER_ID,
    PUBLIC_EVAL_METHOD,
    PUBLIC_EVAL_POLICY_EPOCH,
)
from .permit import sign_permit
from .signed_head import sign_signed_head


BASE_PAYLOAD_HASH = "3f9d3c4a22e52bca663d8f6f7c1ca7ef5f067aac2c6804764347b7a8e4386f53"


def base_signed_head(timestamp: str = "2026-07-04T11:59:45Z", *, status: str = "ok") -> dict[str, Any]:
    unsigned = {
        "signed_head_id": "shd_20260704_115945_f5abd031",
        "log_id": "haltseal-synthetic-log-main",
        "tree_size": 1820394,
        "root_hash": "f5abd031" + "0" * 56,
        "timestamp": timestamp,
        "witness_cosigs": [
            {"witness_id": "synthetic-witness-a", "sig": "witness-a-demo-cosig"},
        ],
        "status": status,
    }
    return sign_signed_head(unsigned)


def base_action(head_id: str = "shd_20260704_115945_f5abd031") -> dict[str, Any]:
    return {
        "action_id": "act_external_tool_sensitive_payload_001",
        "action_type": PUBLIC_EVAL_ACTION_TYPE,
        "method": PUBLIC_EVAL_METHOD,
        "destination": PUBLIC_EVAL_DESTINATION,
        "tenant_id": "tenant-456",
        "agent_id": "agent-123",
        "mission_id": "mission-789",
        "payload_sha256": BASE_PAYLOAD_HASH,
        "policy_epoch": PUBLIC_EVAL_POLICY_EPOCH,
        "implementation_hook": PUBLIC_EVAL_IMPLEMENTATION_HOOK,
        "signed_head_id": head_id,
        "nonce": 4259182012,
        "monotonic_counter": 118,
    }


def base_policy() -> dict[str, Any]:
    return {
        "now": DEFAULT_NOW,
        "mmd_seconds": DEFAULT_MMD_SECONDS,
        "required_context_label": PERMIT_CONTEXT,
        "required_policy_epoch": PUBLIC_EVAL_POLICY_EPOCH,
        "required_icc_head_id": PUBLIC_EVAL_ICC_HEAD_ID,
        "required_license_tier_id": PUBLIC_EVAL_LICENSE_TIER_ID,
        "required_jurisdictional_fingerprint": PUBLIC_EVAL_JURISDICTIONAL_FINGERPRINT,
        "required_elv_measurement_hash": PUBLIC_EVAL_ELV_MEASUREMENT_HASH,
        "require_elv_attestation_ref": True,
        "required_witness_cosigs": 1,
        "require_continuity_proof": True,
        "revoked_permit_ids": [],
        "public_boundary": PUBLIC_BOUNDARY_NOTICE,
    }


def continuity(head_id: str = "shd_20260704_115945_f5abd031", verified: bool = True) -> dict[str, Any]:
    return {
        "type": "append_only_evolution_synthetic",
        "previous_signed_head_id": "shd_20260704_115900_prev",
        "current_signed_head_id": head_id,
        "verified": verified,
    }


def make_permit(
    action: dict[str, Any],
    *,
    issued_ts: str = "2026-07-04T11:59:40Z",
    expiration_ts: str = "2026-07-04T12:04:40Z",
    revoked: bool = False,
    context_label: str = PERMIT_CONTEXT,
    permit_id: str = "permit_7f3c8a2d_public_eval",
) -> dict[str, Any]:
    permit = {
        "context_label": context_label,
        "permit_id": permit_id,
        "audience": audience_from_action(action),
        "issued_ts": issued_ts,
        "expiration_ts": expiration_ts,
        "icc_head_id": PUBLIC_EVAL_ICC_HEAD_ID,
        "signed_head_id": action["signed_head_id"],
        "license_tier_id": PUBLIC_EVAL_LICENSE_TIER_ID,
        "jurisdictional_fingerprint": PUBLIC_EVAL_JURISDICTIONAL_FINGERPRINT,
        "nonce": action["nonce"],
        "monotonic_counter": action["monotonic_counter"],
        "action_digest": action_digest(action),
        "revoked": revoked,
        "elv_attestation_ref": {
            "measurement_hash": PUBLIC_EVAL_ELV_MEASUREMENT_HASH,
            "quote": "synthetic-attestation-quote",
            "cert_chain": ["synthetic-cert-chain"],
        },
    }
    return sign_permit(permit)


def base_packet(vector_id: str = "H01_ALLOW_current_permit_exact_action") -> dict[str, Any]:
    head = base_signed_head()
    action = base_action(head["signed_head_id"])
    permit = make_permit(action)
    return {
        "vector_id": vector_id,
        "title": "current permit exactly matches the protected action",
        "now": DEFAULT_NOW,
        "action": action,
        "permit": permit,
        "signed_head": head,
        "continuity_proof": continuity(head["signed_head_id"], True),
        "validation_policy": base_policy(),
        "expected": {
            "disposition": "ALLOW",
            "result_code": "GATEWAY_PERMIT_CURRENT",
            "stage": "GATEWAY_COMMIT",
        },
    }


def all_vectors() -> list[dict[str, Any]]:
    vectors: list[dict[str, Any]] = []

    h01 = base_packet("H01_ALLOW_current_permit_exact_action")
    vectors.append(h01)

    h02 = base_packet("H02_HOLD_stale_signed_head")
    h02["title"] = "signed head exceeds maximum merge delay and fails closed to HOLD"
    h02["signed_head"] = base_signed_head("2026-07-04T11:58:00Z")
    h02["action"]["signed_head_id"] = h02["signed_head"]["signed_head_id"]
    h02["permit"] = make_permit(h02["action"])
    h02["continuity_proof"] = continuity(h02["signed_head"]["signed_head_id"], True)
    h02["expected"] = {"disposition": "HOLD", "result_code": "FRESHNESS_STALE", "stage": "FRESHNESS_CONTINUITY"}
    vectors.append(h02)

    h03 = base_packet("H03_DENY_expired_permit")
    h03["title"] = "expired permit fails closed to DENY"
    h03["permit"] = make_permit(h03["action"], issued_ts="2026-07-04T11:40:00Z", expiration_ts="2026-07-04T11:59:59Z")
    h03["expected"] = {"disposition": "DENY", "result_code": "PERMIT_EXPIRED", "stage": "PERMIT_STATUS"}
    vectors.append(h03)

    h04 = base_packet("H04_DENY_action_digest_mismatch")
    h04["title"] = "permit digest is bound to a different action"
    tampered_action = deepcopy(h04["action"])
    tampered_action["payload_sha256"] = "4" * 64
    h04["permit"] = make_permit(tampered_action)
    h04["permit"]["audience"] = audience_from_action(h04["action"])
    h04["permit"] = sign_permit(h04["permit"])
    h04["expected"] = {"disposition": "DENY", "result_code": "ACTION_DIGEST_MISMATCH", "stage": "ACTION_BINDING"}
    vectors.append(h04)

    h05 = base_packet("H05_DENY_replay_nonce_monotonic")
    h05["title"] = "nonce and monotonic tuple has already been used for this audience"
    h05["preexisting_replay_state"] = [{
        "audience_key": audience_key(audience_from_action(h05["action"])),
        "nonce": h05["action"]["nonce"],
        "monotonic_counter": h05["action"]["monotonic_counter"],
    }]
    h05["expected"] = {"disposition": "DENY", "result_code": "REPLAY_NONCE_MONOTONIC", "stage": "ANTI_REPLAY"}
    vectors.append(h05)

    h06 = base_packet("H06_DENY_audience_mismatch")
    h06["title"] = "audience-bound permit is presented by a different tenant"
    bad = deepcopy(h06["permit"])
    bad["audience"] = {"agent_id": "agent-123", "tenant_id": "tenant-999", "mission_id": "mission-789"}
    h06["permit"] = sign_permit(bad)
    h06["expected"] = {"disposition": "DENY", "result_code": "AUDIENCE_MISMATCH", "stage": "AUDIENCE_BINDING"}
    vectors.append(h06)

    h07 = base_packet("H07_DENY_revoked_permit")
    h07["title"] = "revoked permit identifier fails closed to DENY"
    h07["permit"] = make_permit(h07["action"], revoked=True)
    h07["expected"] = {"disposition": "DENY", "result_code": "PERMIT_REVOKED", "stage": "PERMIT_STATUS"}
    vectors.append(h07)

    h08 = base_packet("H08_HOLD_missing_continuity_proof")
    h08["title"] = "fresh signed head is present but continuity proof is missing"
    h08["continuity_proof"] = continuity(h08["signed_head"]["signed_head_id"], False)
    h08["expected"] = {"disposition": "HOLD", "result_code": "PROOF_CONTINUITY_MISSING", "stage": "PROOF_CONTINUITY"}
    vectors.append(h08)

    h09 = base_packet("H09_DENY_missing_permit")
    h09["title"] = "protected action arrives without a permit"
    h09["permit"] = None
    h09["expected"] = {"disposition": "DENY", "result_code": "PERMIT_MISSING", "stage": "PERMIT_STATUS"}
    vectors.append(h09)

    h10 = base_packet("H10_DENY_bad_permit_signature")
    h10["title"] = "permit signature no longer matches canonical bytes"
    h10["permit"]["license_tier_id"] = "tampered-public-eval"
    h10["expected"] = {"disposition": "DENY", "result_code": "PERMIT_SIGNATURE_INVALID", "stage": "PERMIT_STATUS"}
    vectors.append(h10)

    h11 = base_packet("H11_DENY_context_label_mismatch")
    h11["title"] = "permit context label is wrong even though fields are otherwise shaped correctly"
    h11["permit"] = make_permit(h11["action"], context_label="HALTSEAL/permit/wrong-context")
    h11["expected"] = {"disposition": "DENY", "result_code": "CONTEXT_LABEL_MISMATCH", "stage": "CANONICALIZATION"}
    vectors.append(h11)

    h12 = base_packet("H12_HOLD_head_conflict")
    h12["title"] = "current signed head reports a cross-log conflict"
    h12["signed_head"] = base_signed_head("2026-07-04T11:59:45Z", status="conflict")
    h12["action"]["signed_head_id"] = h12["signed_head"]["signed_head_id"]
    h12["permit"] = make_permit(h12["action"])
    h12["continuity_proof"] = continuity(h12["signed_head"]["signed_head_id"], True)
    h12["expected"] = {"disposition": "HOLD", "result_code": "HEAD_CONFLICT", "stage": "FRESHNESS_CONTINUITY"}
    vectors.append(h12)

    h13 = base_packet("H13_DENY_unsupported_implementation_hook")
    h13["title"] = "action is outside the configured public-eval gateway hook"
    h13["action"]["implementation_hook"] = "unreviewed_private_hook"
    h13["permit"] = make_permit(h13["action"])
    h13["expected"] = {"disposition": "DENY", "result_code": "UNSUPPORTED_IMPLEMENTATION_HOOK", "stage": "BOUNDARY_MAPPER"}
    vectors.append(h13)

    h14 = base_packet("H14_DENY_signed_head_id_mismatch")
    h14["title"] = "permit signed-head identifier does not match the protected action"
    bad = deepcopy(h14["permit"])
    bad["signed_head_id"] = "shd_wrong_head"
    h14["permit"] = sign_permit(bad)
    h14["expected"] = {"disposition": "DENY", "result_code": "SIGNED_HEAD_ID_MISMATCH", "stage": "FRESHNESS_CONTINUITY"}
    vectors.append(h14)

    h15 = base_packet("H15_HOLD_missing_witness_cosignature")
    h15["title"] = "signed head is otherwise valid but lacks the required witness cosignature"
    unsigned = deepcopy(h15["signed_head"])
    unsigned["witness_cosigs"] = []
    unsigned.pop("signature", None)
    h15["signed_head"] = sign_signed_head(unsigned)
    h15["expected"] = {"disposition": "HOLD", "result_code": "WITNESS_COSIGNATURE_MISSING", "stage": "FRESHNESS_CONTINUITY"}
    vectors.append(h15)

    h16 = base_packet("H16_DENY_signed_head_signature_invalid")
    h16["title"] = "signed head signature is invalid after a root hash mutation"
    h16["signed_head"]["root_hash"] = "bad0" + "0" * 60
    h16["expected"] = {"disposition": "DENY", "result_code": "SIGNED_HEAD_SIGNATURE_INVALID", "stage": "FRESHNESS_CONTINUITY"}
    vectors.append(h16)

    h17 = base_packet("H17_DENY_boundary_destination_not_reviewed")
    h17["title"] = "a signed permit cannot expand the public-eval boundary to a different destination"
    h17["action"]["destination"] = "https://example.invalid/other-tool"
    h17["permit"] = make_permit(h17["action"])
    h17["expected"] = {"disposition": "DENY", "result_code": "UNSUPPORTED_PROTECTED_ACTION", "stage": "BOUNDARY_MAPPER"}
    vectors.append(h17)

    h18 = base_packet("H18_DENY_permit_not_yet_valid")
    h18["title"] = "permit issued in the future is denied"
    h18["permit"] = make_permit(h18["action"], issued_ts="2026-07-04T12:01:00Z", expiration_ts="2026-07-04T12:05:00Z")
    h18["expected"] = {"disposition": "DENY", "result_code": "PERMIT_NOT_YET_VALID", "stage": "PERMIT_STATUS"}
    vectors.append(h18)

    h19 = base_packet("H19_DENY_signed_head_from_future")
    h19["title"] = "signed head timestamp after verifier time is denied"
    h19["signed_head"] = base_signed_head("2026-07-04T12:00:30Z")
    h19["action"]["signed_head_id"] = h19["signed_head"]["signed_head_id"]
    h19["permit"] = make_permit(h19["action"])
    h19["continuity_proof"] = continuity(h19["signed_head"]["signed_head_id"], True)
    h19["expected"] = {"disposition": "DENY", "result_code": "SIGNED_HEAD_FROM_FUTURE", "stage": "FRESHNESS_CONTINUITY"}
    vectors.append(h19)

    h20 = base_packet("H20_HOLD_continuity_proof_mismatch")
    h20["title"] = "continuity proof points at a different signed head and therefore holds"
    h20["continuity_proof"] = continuity("shd_wrong_current", True)
    h20["expected"] = {"disposition": "HOLD", "result_code": "PROOF_CONTINUITY_MISMATCH", "stage": "PROOF_CONTINUITY"}
    vectors.append(h20)

    h21 = base_packet("H21_DENY_replay_counter_not_advanced")
    h21["title"] = "a fresh nonce still denies when the monotonic counter does not advance"
    aud_key = audience_key(audience_from_action(h21["action"]))
    h21["preexisting_replay_state"] = [{"audience_key": aud_key, "nonce": 1, "monotonic_counter": h21["action"]["monotonic_counter"]}]
    h21["action"]["nonce"] = h21["action"]["nonce"] + 1
    h21["permit"] = make_permit(h21["action"])
    h21["expected"] = {"disposition": "DENY", "result_code": "REPLAY_NONCE_MONOTONIC", "stage": "ANTI_REPLAY"}
    vectors.append(h21)

    h22 = base_packet("H22_DENY_icc_head_id_mismatch")
    h22["title"] = "permit signed for another ICC head is denied before gateway commit"
    bad = deepcopy(h22["permit"])
    bad["icc_head_id"] = "icc_head_unreviewed_private_eval"
    h22["permit"] = sign_permit(bad)
    h22["expected"] = {"disposition": "DENY", "result_code": "ICC_HEAD_ID_MISMATCH", "stage": "ICC_BOUNDARY"}
    vectors.append(h22)

    h23 = base_packet("H23_DENY_license_tier_mismatch")
    h23["title"] = "permit signed for an unreviewed license tier is denied at the synthetic GLG gate"
    bad = deepcopy(h23["permit"])
    bad["license_tier_id"] = "private-tier"
    h23["permit"] = sign_permit(bad)
    h23["expected"] = {"disposition": "DENY", "result_code": "LICENSE_TIER_MISMATCH", "stage": "GLG_GATE"}
    vectors.append(h23)

    h24 = base_packet("H24_DENY_jurisdictional_fingerprint_mismatch")
    h24["title"] = "permit signed for another jurisdictional fingerprint is denied at the synthetic GLG gate"
    bad = deepcopy(h24["permit"])
    bad["jurisdictional_fingerprint"] = "SYNTHETIC-OTHER-JURISDICTION"
    h24["permit"] = sign_permit(bad)
    h24["expected"] = {"disposition": "DENY", "result_code": "JURISDICTIONAL_FINGERPRINT_MISMATCH", "stage": "GLG_GATE"}
    vectors.append(h24)

    h25 = base_packet("H25_DENY_elv_attestation_mismatch")
    h25["title"] = "permit carries a valid signature but the ELV measurement hash is not the reviewed one"
    bad = deepcopy(h25["permit"])
    bad["elv_attestation_ref"]["measurement_hash"] = "a5" * 32
    h25["permit"] = sign_permit(bad)
    h25["expected"] = {"disposition": "DENY", "result_code": "ELV_ATTESTATION_MISMATCH", "stage": "ELV_ATTESTATION"}
    vectors.append(h25)

    h26 = base_packet("H26_DENY_policy_epoch_mismatch")
    h26["title"] = "signed action outside the reviewed policy epoch is denied by the public boundary mapper"
    h26["action"]["policy_epoch"] = "2026-07-04T13:00:00Z"
    h26["permit"] = make_permit(h26["action"])
    h26["expected"] = {"disposition": "DENY", "result_code": "POLICY_EPOCH_MISMATCH", "stage": "BOUNDARY_MAPPER"}
    vectors.append(h26)

    h27 = base_packet("H27_DENY_permit_replay_tuple_mismatch")
    h27["title"] = "permit nonce and monotonic counter must match the captured action tuple"
    bad = deepcopy(h27["permit"])
    bad["nonce"] = bad["nonce"] + 100
    h27["permit"] = sign_permit(bad)
    h27["expected"] = {"disposition": "DENY", "result_code": "PERMIT_REPLAY_TUPLE_MISMATCH", "stage": "ANTI_REPLAY"}
    vectors.append(h27)

    h28 = base_packet("H28_DENY_policy_revoked_permit_id")
    h28["title"] = "policy revocation list denies an otherwise well-formed permit identifier"
    h28["validation_policy"]["revoked_permit_ids"] = [h28["permit"]["permit_id"]]
    h28["expected"] = {"disposition": "DENY", "result_code": "PERMIT_REVOKED", "stage": "PERMIT_STATUS"}
    vectors.append(h28)

    h29 = base_packet("H29_DENY_unknown_action_field")
    h29["title"] = "unknown protected-action fields are denied rather than silently ignored"
    h29["action"]["unreviewed_effect"] = "attempted-expansion"
    h29["permit"] = make_permit(h29["action"])
    h29["expected"] = {"disposition": "DENY", "result_code": "ACTION_SHAPE_INVALID", "stage": "BOUNDARY_MAPPER"}
    vectors.append(h29)

    h30 = base_packet("H30_DENY_signed_head_shape_invalid")
    h30["title"] = "signed-head shape errors deny deterministically before freshness evaluation"
    unsigned = deepcopy(h30["signed_head"])
    unsigned.pop("root_hash", None)
    unsigned.pop("signature", None)
    h30["signed_head"] = sign_signed_head(unsigned)
    h30["expected"] = {"disposition": "DENY", "result_code": "SIGNED_HEAD_SHAPE_INVALID", "stage": "FRESHNESS_CONTINUITY"}
    vectors.append(h30)

    h31 = base_packet("H31_DENY_validation_policy_now_mismatch")
    h31["title"] = "packet time and validation-policy time must be the same review clock"
    h31["validation_policy"]["now"] = "2026-07-04T12:00:01Z"
    h31["expected"] = {"disposition": "DENY", "result_code": "POLICY_NOW_MISMATCH", "stage": "PACKET_VALIDATION"}
    vectors.append(h31)

    h32 = base_packet("H32_DENY_signature_algorithm_mismatch")
    h32["title"] = "signature metadata mismatch denies even when the surrounding fields are shaped correctly"
    h32["permit"]["signature"]["alg"] = "HS999-SYNTHETIC"
    h32["expected"] = {"disposition": "DENY", "result_code": "PERMIT_SIGNATURE_INVALID", "stage": "PERMIT_STATUS"}
    vectors.append(h32)

    return vectors
