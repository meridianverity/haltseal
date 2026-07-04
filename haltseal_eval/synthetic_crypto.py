from __future__ import annotations

import base64
import hmac
import hashlib
from typing import Any

from .canonicalization import contextual_preimage
from .constants import SYNTHETIC_ALG, SYNTHETIC_KID, SYNTHETIC_SECRET


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def synthetic_mac(context: str, value: Any, secret: bytes = SYNTHETIC_SECRET) -> str:
    digest = hmac.new(secret, contextual_preimage(context, value), hashlib.sha256).digest()
    return b64url(digest)


def signature_block(context: str, value: Any) -> dict:
    return {
        "alg": SYNTHETIC_ALG,
        "kid": SYNTHETIC_KID,
        "sig": synthetic_mac(context, value),
    }


def constant_time_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def verify_signature_block(context: str, value: Any, sig: dict | None) -> bool:
    if not isinstance(sig, dict):
        return False
    if sig.get("alg") != SYNTHETIC_ALG or sig.get("kid") != SYNTHETIC_KID:
        return False
    expected = synthetic_mac(context, value)
    return constant_time_equal(expected, str(sig.get("sig", "")))
