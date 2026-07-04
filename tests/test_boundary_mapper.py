from haltseal_eval.fixtures import base_packet, make_permit
from haltseal_eval.replay import ReplayCache
from haltseal_eval.verifier import verify_packet


def test_signed_permit_cannot_expand_to_unreviewed_destination():
    packet = base_packet()
    packet["action"]["destination"] = "https://example.invalid/other-tool"
    packet["permit"] = make_permit(packet["action"])
    result = verify_packet(packet, ReplayCache())
    assert result["disposition"] == "DENY"
    assert result["result_code"] == "UNSUPPORTED_PROTECTED_ACTION"
    assert result["stage"] == "BOUNDARY_MAPPER"


def test_signed_permit_cannot_expand_to_other_hook():
    packet = base_packet()
    packet["action"]["implementation_hook"] = "device_io_gateway"
    packet["permit"] = make_permit(packet["action"])
    result = verify_packet(packet, ReplayCache())
    assert result["disposition"] == "DENY"
    assert result["result_code"] == "UNSUPPORTED_IMPLEMENTATION_HOOK"
    assert result["stage"] == "BOUNDARY_MAPPER"
