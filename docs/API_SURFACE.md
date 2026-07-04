# API surface for public review

This package exposes only tiny helper functions for deterministic review.

```python
from haltseal_eval import evaluate_gateway_packet, verify_packet
```

Primary files:

- `haltseal_eval/verifier.py` — ordered fail-closed checks
- `haltseal_eval/action_digest.py` — protected-action canonical digest
- `haltseal_eval/permit.py` — synthetic permit signature and status checks
- `haltseal_eval/signed_head.py` — signed-head freshness and witness checks
- `haltseal_eval/replay.py` — nonce and monotonic replay cache
- `haltseal_eval/evidence.py` — evidence-only record builder

No production integration surface is provided.
