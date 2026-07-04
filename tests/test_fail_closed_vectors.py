from pathlib import Path

from haltseal_eval.canonicalization import load_json
from haltseal_eval.replay import ReplayCache
from haltseal_eval.verifier import verify_packet

ROOT = Path(__file__).resolve().parents[1]


def test_all_public_vectors_match_expected_results():
    vectors = load_json(ROOT / "vectors" / "haltseal_gateway_vectors.json")
    assert len(vectors) == 32
    for packet in vectors:
        result = verify_packet(packet, ReplayCache())
        expected = packet["expected"]
        assert result["disposition"] == expected["disposition"], packet["vector_id"]
        assert result["result_code"] == expected["result_code"], packet["vector_id"]
        assert result["stage"] == expected["stage"], packet["vector_id"]
        assert result["evidence"]["evidence_hash"]


def test_allow_vector_emits_evidence_only_boundary_notice():
    packet = load_json(ROOT / "examples" / "h01_allow_current_permit_exact_action.json")
    result = verify_packet(packet, ReplayCache())
    assert result["evidence"]["public_boundary"] == "synthetic evaluation only; no production SDK; no patent license"
