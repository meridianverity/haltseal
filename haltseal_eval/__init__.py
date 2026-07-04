"""HALTSEAL Gateway Proof Pack public evaluation package.

Synthetic only. No production SDK. No patent license.
"""

__version__ = "0.3.0-public-eval"

from .gateway import evaluate_gateway_packet
from .verifier import verify_packet

__all__ = ["evaluate_gateway_packet", "verify_packet", "__version__"]
