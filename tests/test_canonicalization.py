import pytest

from haltseal_eval.canonicalization import CanonicalizationError, canonical_json_bytes, contextual_sha256


def test_canonical_json_is_stable_for_key_order():
    a = {"b": 2, "a": 1, "nested": {"z": True, "a": None}}
    b = {"nested": {"a": None, "z": True}, "a": 1, "b": 2}
    assert canonical_json_bytes(a) == canonical_json_bytes(b)
    assert contextual_sha256("ctx", a) == contextual_sha256("ctx", b)


def test_context_changes_digest():
    value = {"x": "y"}
    assert contextual_sha256("ctx-a", value) != contextual_sha256("ctx-b", value)


def test_floats_are_rejected():
    with pytest.raises(CanonicalizationError):
        canonical_json_bytes({"bad": 1.25})
