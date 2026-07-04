# GitHub upload checklist

Repository name recommendation:

```text
haltseal-gateway-proof-pack
```

Before the first public push:

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
make clean-bytecode
PYTHONDONTWRITEBYTECODE=1 python tools/release_gate.py
PYTHONDONTWRITEBYTECODE=1 python tools/zip_audit.py
```

Recommended first tag:

```text
v0.3.0-public-eval
```

Recommended release title:

```text
HALTSEAL Gateway Proof Pack v0.3.0 — Public Evaluation Artifact
```

Upload the repo ZIP plus `MANIFEST.sha256.json` and the SHA-256 text file as release assets.
