from __future__ import annotations

from typing import Any

from .replay import ReplayCache
from .verifier import verify_packet


def evaluate_gateway_packet(packet: dict[str, Any]) -> dict[str, Any]:
    return verify_packet(packet, ReplayCache())
