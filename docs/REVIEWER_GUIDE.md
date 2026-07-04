# Reviewer guide

## 3 minutes

```bash
python tools/run_public_eval.py
```

You should see 32 / 32 vectors pass.

## 10 minutes

Inspect:

- `haltseal_eval/verifier.py`
- `vectors/haltseal_gateway_vectors.json`
- `examples/h01_allow_current_permit_exact_action.json`
- `examples/h02_hold_stale_signed_head.json`
- `examples/h04_deny_action_digest_mismatch.json`
- `examples/h05_deny_replay_nonce_monotonic.json`

## 30 minutes

Run:

```bash
python tools/validate_public_packet.py
python tools/generate_transparency_report.py
python tools/make_manifest.py
python verify_manifest.py
python -m pytest -q
python tools/release_gate.py
make clean-caches
python tools/zip_audit.py
```

Then read:

- `docs/PUBLIC_BOUNDARY.md`
- `docs/LICENSING_HANDOFF.md`
- `docs/THREAT_MODEL_PUBLIC_EVAL.md`

## Review questions

- Is the protected action digest reproducible?
- Does an expired permit deny?
- Does a stale signed head hold?
- Does a replayed nonce/monotonic tuple deny?
- Does every outcome emit an evidence-only record?
- Is the public/private boundary explicit?
