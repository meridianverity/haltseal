from copy import deepcopy

from haltseal_eval.fixtures import base_packet
from haltseal_eval.permit import sign_permit
from haltseal_eval.replay import ReplayCache
from haltseal_eval.verifier import verify_packet


def decision(packet):
    return verify_packet(packet, ReplayCache())


def test_icc_head_lock_denies_signed_permit_for_other_head():
    packet = base_packet()
    bad = deepcopy(packet["permit"])
    bad["icc_head_id"] = "icc_head_private"
    packet["permit"] = sign_permit(bad)
    result = decision(packet)
    assert result["disposition"] == "DENY"
    assert result["result_code"] == "ICC_HEAD_ID_MISMATCH"
    assert result["stage"] == "ICC_BOUNDARY"


def test_glg_license_tier_lock_denies_signed_permit_for_other_tier():
    packet = base_packet()
    bad = deepcopy(packet["permit"])
    bad["license_tier_id"] = "private-tier"
    packet["permit"] = sign_permit(bad)
    result = decision(packet)
    assert result["disposition"] == "DENY"
    assert result["result_code"] == "LICENSE_TIER_MISMATCH"
    assert result["stage"] == "GLG_GATE"


def test_elv_measurement_lock_denies_signed_permit_for_other_measurement():
    packet = base_packet()
    bad = deepcopy(packet["permit"])
    bad["elv_attestation_ref"]["measurement_hash"] = "ab" * 32
    packet["permit"] = sign_permit(bad)
    result = decision(packet)
    assert result["disposition"] == "DENY"
    assert result["result_code"] == "ELV_ATTESTATION_MISMATCH"
    assert result["stage"] == "ELV_ATTESTATION"


def test_policy_epoch_lock_denies_signed_action_outside_epoch():
    packet = base_packet()
    packet["action"]["policy_epoch"] = "2026-07-04T13:00:00Z"
    result = decision(packet)
    assert result["disposition"] == "DENY"
    assert result["result_code"] == "POLICY_EPOCH_MISMATCH"
    assert result["stage"] == "BOUNDARY_MAPPER"
