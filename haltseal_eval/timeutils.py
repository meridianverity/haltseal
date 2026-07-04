from __future__ import annotations

from datetime import datetime, timezone


def parse_ts(ts: str) -> datetime:
    if not isinstance(ts, str) or not ts.endswith("Z"):
        raise ValueError(f"timestamp must be an ISO-8601 Z string: {ts!r}")
    return datetime.fromisoformat(ts[:-1] + "+00:00").astimezone(timezone.utc)


def seconds_between(later: str, earlier: str) -> int:
    return int((parse_ts(later) - parse_ts(earlier)).total_seconds())
