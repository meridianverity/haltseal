from copy import deepcopy

from haltseal_eval.constants import DEFAULT_NOW, DEFAULT_MMD_SECONDS, PERMIT_CONTEXT
from haltseal_eval.fixtures import base_action, base_signed_head, make_permit
from haltseal_eval.permit import validate_permit_signature, validate_permit_status
from haltseal_eval.signed_head import validate_signed_head


def test_permit_signature_accepts_fixture():
    action = base_action()
    permit = make_permit(action)
    assert validate_permit_signature(permit)


def test_permit_signature_rejects_tamper():
    action = base_action()
    permit = make_permit(action)
    permit["license_tier_id"] = "tampered"
    assert not validate_permit_signature(permit)


def test_context_label_mismatch_rejected_before_status_allow():
    action = base_action()
    permit = make_permit(action, context_label="wrong")
    ok, code, stage = validate_permit_status(permit, now=DEFAULT_NOW, required_context_label=PERMIT_CONTEXT, revoked_ids=set())
    assert not ok
    assert code == "CONTEXT_LABEL_MISMATCH"
    assert stage == "CANONICALIZATION"


def test_signed_head_freshness_accepts_current_head():
    head = base_signed_head("2026-07-04T11:59:45Z")
    ok, code, stage = validate_signed_head(head, now=DEFAULT_NOW, mmd_seconds=DEFAULT_MMD_SECONDS, required_witness_cosigs=1)
    assert ok
    assert code == "SIGNED_HEAD_OK"


def test_signed_head_freshness_rejects_stale_head():
    head = base_signed_head("2026-07-04T11:58:00Z")
    ok, code, stage = validate_signed_head(head, now=DEFAULT_NOW, mmd_seconds=DEFAULT_MMD_SECONDS, required_witness_cosigs=1)
    assert not ok
    assert code == "FRESHNESS_STALE"


def test_signed_head_signature_rejects_mutation():
    head = base_signed_head()
    head["root_hash"] = "a" * 64
    ok, code, stage = validate_signed_head(head, now=DEFAULT_NOW, mmd_seconds=DEFAULT_MMD_SECONDS, required_witness_cosigs=1)
    assert not ok
    assert code == "SIGNED_HEAD_SIGNATURE_INVALID"
