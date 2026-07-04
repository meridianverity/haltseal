from haltseal_eval.action_digest import audience_from_action, audience_key
from haltseal_eval.fixtures import base_packet
from haltseal_eval.replay import ReplayCache
from haltseal_eval.verifier import verify_packet


def test_replay_cache_denies_same_nonce_tuple_on_second_use():
    packet = base_packet()
    cache = ReplayCache()
    first = verify_packet(packet, cache)
    second = verify_packet(packet, cache)
    assert first["disposition"] == "ALLOW"
    assert second["disposition"] == "DENY"
    assert second["result_code"] == "REPLAY_NONCE_MONOTONIC"


def test_replay_preload_vector_path():
    packet = base_packet()
    aud_key = audience_key(audience_from_action(packet["action"]))
    packet["preexisting_replay_state"] = [{"audience_key": aud_key, "nonce": packet["action"]["nonce"], "monotonic_counter": packet["action"]["monotonic_counter"]}]
    result = verify_packet(packet, ReplayCache())
    assert result["result_code"] == "REPLAY_NONCE_MONOTONIC"
