# 3-minute demo script

```bash
python tools/run_public_eval.py
```

Narration:

```text
This is HALTSEAL Gateway Proof Pack.
It is synthetic and public-safe.
It evaluates one protected action boundary.
ALLOW happens only when the action digest, permit, audience, signed head, continuity proof, and replay posture are current.
Stale or missing continuity yields HOLD.
Expired, revoked, mismatched, bad-signature, unsupported-hook, and replay cases yield DENY.
Every result emits an evidence-only record.
No production SDK, no claim chart, no patent license.
```
