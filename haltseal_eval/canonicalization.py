from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class CanonicalizationError(ValueError):
    """Raised when an object cannot be canonically represented for this eval."""


def _reject_unsupported(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        raise CanonicalizationError(f"floats are not permitted at {path}; use strings or integers")
    if isinstance(value, list):
        for i, item in enumerate(value):
            _reject_unsupported(item, f"{path}[{i}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError(f"non-string key at {path}: {key!r}")
            _reject_unsupported(item, f"{path}.{key}")
        return
    raise CanonicalizationError(f"unsupported type at {path}: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes.

    This is a small public-evaluation canonicalization profile: sorted object keys,
    no insignificant whitespace, UTF-8, and no floats. It is intentionally strict so
    reviewers can reproduce every digest exactly with standard-library Python.
    """
    _reject_unsupported(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def contextual_preimage(context: str, value: Any) -> bytes:
    if not isinstance(context, str) or not context:
        raise CanonicalizationError("context must be a non-empty string")
    return context.encode("utf-8") + b"\x00" + canonical_json_bytes(value)


def sha256_hex_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def contextual_sha256(context: str, value: Any) -> str:
    return sha256_hex_bytes(contextual_preimage(context, value))


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, value: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
