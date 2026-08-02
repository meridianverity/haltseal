from __future__ import annotations

from .canonical import action_digest, authority_digest
from .constants import RECEIPT_TYP
from .jws import JWSError, verify
from .receipt_profile import ReceiptProfileError, validate_receipt_payload
from .semantics import evaluate_action


class ReceiptVerificationError(ValueError):
    pass


def verify_receipt(receipt_jws, jwks):
    try:
        _, payload = verify(receipt_jws, jwks, expected_typ=RECEIPT_TYP)
        authority, action, emission, consumption = validate_receipt_payload(payload)

        if payload["authority_digest"] != authority_digest(authority):
            raise ReceiptVerificationError("authority digest mismatch")
        if payload["action_digest"] != action_digest(action):
            raise ReceiptVerificationError("action digest mismatch")

        outcome_unknown = payload["decision"] == "HOLD"
        already_consumed = (
            payload["decision"] == "REFUSE"
            and consumption["state_before"] == "CONSUMED"
        )
        expected = evaluate_action(
            authority,
            action,
            outcome_unknown=outcome_unknown,
            already_consumed=already_consumed,
        )
        if payload["decision"] != expected.decision:
            raise ReceiptVerificationError("decision semantic replay mismatch")
        if tuple(payload["reason_codes"]) != expected.reason_codes:
            raise ReceiptVerificationError("reason-code semantic replay mismatch")
        if emission["disposition"] != expected.emission_disposition:
            raise ReceiptVerificationError("emission semantic replay mismatch")

        return {
            "signature": "VALID",
            "semantic_replay": "PASS",
            "decision": payload["decision"],
            "reason_codes": payload["reason_codes"],
            "action_digest": payload["action_digest"],
            "authority_digest": payload["authority_digest"],
            "emission": emission,
            "receipt_id": payload["jti"],
            "profile_version": payload["profile_version"],
        }
    except (JWSError, ReceiptProfileError, ReceiptVerificationError, KeyError, TypeError, ValueError) as exc:
        raise ReceiptVerificationError(str(exc)) from exc
