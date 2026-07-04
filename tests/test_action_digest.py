from copy import deepcopy

from haltseal_eval.action_digest import action_digest, validate_action_shape
from haltseal_eval.fixtures import base_action


def test_action_digest_binds_destination():
    a = base_action()
    b = deepcopy(a)
    b["destination"] = "https://example.invalid/other"
    assert action_digest(a) != action_digest(b)


def test_action_shape_rejects_unknown_hook():
    a = base_action()
    a["implementation_hook"] = "unknown"
    assert any("unsupported implementation hook" in f for f in validate_action_shape(a))
