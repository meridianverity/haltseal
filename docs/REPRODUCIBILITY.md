# Reproducibility

The evaluation is deterministic.

```bash
python tools/run_public_eval.py
python tools/make_manifest.py
python verify_manifest.py
python -m pytest -q
```

No network calls are made. No external service is required. Demo signatures use fixture material that is intentionally public and deterministic.

`MANIFEST.json` records file sizes and SHA-256 digests for release review.
