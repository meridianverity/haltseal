from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Any


def _is_int_not_bool(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass
class ReplayCache:
    """Tiny in-memory replay state for the synthetic public evaluation."""

    max_counter_by_audience: dict[str, int] = field(default_factory=dict)
    seen_nonces_by_audience: dict[str, set[int]] = field(default_factory=dict)

    def preload(self, entries: Iterable[dict] | None) -> tuple[bool, str]:
        if entries is None:
            return True, "REPLAY_PRELOAD_OK"
        if not isinstance(entries, list):
            return False, "REPLAY_STATE_INVALID"
        for entry in entries:
            if not isinstance(entry, dict):
                return False, "REPLAY_STATE_INVALID"
            audience_key = entry.get("audience_key")
            nonce = entry.get("nonce")
            monotonic_counter = entry.get("monotonic_counter")
            if not isinstance(audience_key, str) or not audience_key:
                return False, "REPLAY_STATE_INVALID"
            if not _is_int_not_bool(nonce) or not _is_int_not_bool(monotonic_counter):
                return False, "REPLAY_STATE_INVALID"
            if nonce < 0 or monotonic_counter < 0:
                return False, "REPLAY_STATE_INVALID"
            self.record(audience_key, nonce, monotonic_counter, strict=False)
        return True, "REPLAY_PRELOAD_OK"

    def record(self, audience_key: str, nonce: int, monotonic_counter: int, *, strict: bool = True) -> tuple[bool, str]:
        if not isinstance(audience_key, str) or not audience_key:
            return False, "REPLAY_AUDIENCE_INVALID"
        if not _is_int_not_bool(nonce) or not _is_int_not_bool(monotonic_counter) or nonce < 0 or monotonic_counter < 0:
            return False, "REPLAY_COUNTER_INVALID"
        seen = self.seen_nonces_by_audience.setdefault(audience_key, set())
        previous_max = self.max_counter_by_audience.get(audience_key)
        if strict:
            if nonce in seen:
                return False, "REPLAY_NONCE_REUSE"
            if previous_max is not None and monotonic_counter <= previous_max:
                return False, "REPLAY_MONOTONIC_NOT_ADVANCED"
        seen.add(nonce)
        if previous_max is None or monotonic_counter > previous_max:
            self.max_counter_by_audience[audience_key] = monotonic_counter
        return True, "REPLAY_OK"
