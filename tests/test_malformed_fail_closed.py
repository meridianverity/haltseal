from copy import deepcopy

from haltseal_eval.fixtures import base_packet, make_permit
from haltseal_eval.permit import sign_permit
from haltseal_eval.replay import ReplayCache
from haltseal_eval.signed_head import sign_signed_head
from haltseal_eval.verifier import verify_packet


def decision(packet):
    return verify_packet(packet, ReplayCache())


def test_non_object_packet_denies_without_exception():
    result = decision(["not", "a", "packet"])
    assert result["disposition"] == "DENY"
    assert result["result_code"] == "PACKET_SHAPE_INVALID"


def test_bad_now_timestamp_denies_without_exception():
    packet = base_packet()
    packet["now"] = "not-a-timestamp"
    packet["validation_policy"]["now"] = "not-a-timestamp"
    result = decision(packet)
    assert result["disposition"] == "DENY"
    assert result["result_code"] == "TIMESTAMP_INVALID"


def test_missing_permit_timestamp_with_valid_signature_denies_without_exception():
    packet = base_packet()
    permit = deepcopy(packet["permit"])
    del permit["issued_ts"]
    packet["permit"] = sign_permit(permit)
    result = decision(packet)
    assert result["disposition"] == "DENY"
    assert result["result_code"] == "PERMIT_SHAPE_INVALID"


def test_bad_signed_head_timestamp_denies_without_exception():
    packet = base_packet()
    head = deepcopy(packet["signed_head"])
    head["timestamp"] = "bad-timestamp"
    head.pop("signature", None)
    packet["signed_head"] = sign_signed_head(head)
    result = decision(packet)
    assert result["disposition"] == "DENY"
    assert result["result_code"] == "SIGNED_HEAD_TIMESTAMP_INVALID"


def test_bad_policy_integer_denies_without_exception():
    packet = base_packet()
    packet["validation_policy"]["mmd_seconds"] = "abc"
    result = decision(packet)
    assert result["disposition"] == "DENY"
    assert result["result_code"] == "VALIDATION_POLICY_INVALID"


def test_bad_replay_preload_denies_without_exception():
    packet = base_packet()
    packet["preexisting_replay_state"] = [{"bad": "x"}]
    result = decision(packet)
    assert result["disposition"] == "DENY"
    assert result["result_code"] == "REPLAY_STATE_INVALID"


def test_unknown_action_field_denies_before_digest_expansion():
    packet = base_packet()
    packet["action"]["extra_effect"] = "unreviewed"
    packet["permit"] = make_permit(packet["action"])
    result = decision(packet)
    assert result["disposition"] == "DENY"
    assert result["result_code"] == "ACTION_SHAPE_INVALID"
