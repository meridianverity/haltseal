# QA report — v0.3.0-public-eval

Validation target: HALTSEAL Gateway Proof Pack public evaluation artifact.

Expected final release gate:

```text
run_public_eval: 32 / 32 PASS
validate_public_packet: PASS
synthetic evaluation attestation: PASS
manifest verification: PASS
pytest: PASS
release_gate: PASS / findings: 0
zip_audit: PASS
```

Public boundary: synthetic evaluation only; no production SDK; no patent license.

The v0.3 vector set tests the reviewed boundary, permit status, canonical action binding, audience binding, replay tuple binding, signed-head freshness and witness posture, continuity proof posture, ICC head lock, synthetic GLG policy locks, ELV measurement lock, revocation-list lock, policy-time consistency, and malformed-input fail-closed behavior.
