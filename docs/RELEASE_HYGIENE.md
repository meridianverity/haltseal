# Release hygiene

Before publishing a public release:

```bash
python -m pip install -r requirements.txt
PYTHONDONTWRITEBYTECODE=1 python tools/regenerate_vectors.py
PYTHONDONTWRITEBYTECODE=1 python tools/run_public_eval.py
PYTHONDONTWRITEBYTECODE=1 python tools/validate_public_packet.py
PYTHONDONTWRITEBYTECODE=1 python tools/generate_transparency_report.py
PYTHONDONTWRITEBYTECODE=1 python tools/generate_attestation.py
PYTHONDONTWRITEBYTECODE=1 python tools/make_manifest.py
PYTHONDONTWRITEBYTECODE=1 python verify_manifest.py
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q
PYTHONDONTWRITEBYTECODE=1 python tools/release_gate.py
make clean-caches
PYTHONDONTWRITEBYTECODE=1 python tools/zip_audit.py
```

Required result:

```text
vectors: 32 / 32 PASS
packet validation: PASS
transparency report: PASS
synthetic evaluation attestation: PASS
manifest verification: PASS
tests: PASS
release gate findings: 0
zip audit findings: 0
```

For a deterministic release archive:

```bash
PYTHONDONTWRITEBYTECODE=1 python tools/package_release.py
```

Do not publish target-company analysis, private legal mappings, confidential deployment architecture, commercial terms, or production implementation depth.
