from __future__ import annotations

import base64
import binascii
import hashlib
import re

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from .strict_json import dumps, loads


class JWSError(ValueError):
    pass


_B64URL = re.compile(r"^[A-Za-z0-9_-]+$")


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def unb64u(value: str) -> bytes:
    """Decode one canonical, unpadded base64url segment.

    Rejects padding, standard-base64 characters, whitespace, invalid lengths, and
    non-canonical encodings whose unused pad bits are not zero.
    """
    if not isinstance(value, str) or not _B64URL.fullmatch(value) or len(value) % 4 == 1:
        raise JWSError("base64url segment is not canonical unpadded base64url")
    try:
        padded = value + "=" * ((4 - len(value) % 4) % 4)
        decoded = base64.b64decode(padded.encode("ascii"), altchars=b"-_", validate=True)
    except (ValueError, binascii.Error) as exc:
        raise JWSError("invalid base64url") from exc
    if b64u(decoded) != value:
        raise JWSError("base64url segment is not canonical")
    return decoded


def deterministic_private_key(label: str):
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(label.encode()).digest())


def public_jwk(private_key, kid: str):
    raw = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return {"kty": "OKP", "crv": "Ed25519", "x": b64u(raw), "kid": kid, "use": "sig", "alg": "EdDSA"}


def sign(payload, private_key, *, kid, typ):
    header = {"alg": "EdDSA", "kid": kid, "typ": typ}
    h = b64u(dumps(header).encode())
    p = b64u(dumps(payload).encode())
    data = f"{h}.{p}".encode("ascii")
    return f"{h}.{p}.{b64u(private_key.sign(data))}"


def decode_unverified(token):
    if not isinstance(token, str) or token.count(".") != 2:
        raise JWSError("compact JWS must contain three parts")
    h, p, s = token.split(".")
    try:
        header = loads(unb64u(h), require_object=True)
        payload = loads(unb64u(p), require_object=True)
    except Exception as exc:
        raise JWSError(str(exc)) from exc
    return header, payload, f"{h}.{p}".encode("ascii"), unb64u(s)


def _pub(jwk):
    if not isinstance(jwk, dict) or set(jwk) != {"kty", "crv", "x", "kid", "use", "alg"}:
        raise JWSError("JWK field set is not exact")
    if jwk.get("kty") != "OKP" or jwk.get("crv") != "Ed25519" or jwk.get("alg") != "EdDSA" or jwk.get("use") != "sig":
        raise JWSError("unsupported JWK")
    try:
        return Ed25519PublicKey.from_public_bytes(unb64u(jwk["x"]))
    except Exception as exc:
        raise JWSError("invalid JWK") from exc


def verify(token, jwks, *, expected_typ):
    header, payload, data, sig = decode_unverified(token)
    if set(header) != {"alg", "kid", "typ"} or header.get("alg") != "EdDSA" or header.get("typ") != expected_typ:
        raise JWSError("protected header is not exact")
    if not isinstance(header.get("kid"), str) or not header["kid"]:
        raise JWSError("protected header kid is invalid")
    keys = jwks.get("keys") if isinstance(jwks, dict) and set(jwks) == {"keys"} else None
    if not isinstance(keys, list):
        raise JWSError("JWKS field set or keys is invalid")
    matches = [k for k in keys if isinstance(k, dict) and k.get("kid") == header.get("kid")]
    if len(matches) != 1:
        raise JWSError("kid must identify exactly one key")
    try:
        _pub(matches[0]).verify(sig, data)
    except InvalidSignature as exc:
        raise JWSError("invalid signature") from exc
    return header, payload
