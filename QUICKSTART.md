# Quickstart

```bash
python -m pip install -r requirements.txt
python tools/run_public_eval.py
python tools/validate_public_packet.py
python tools/export_proof_receipt.py
python tools/verify_proof_receipt.py
python tools/generate_transparency_bundle.py
python tools/verify_transparency_bundle.py
python tools/generate_ed25519_profile.py
python tools/verify_ed25519_profile.py
python tools/independent_recompute.py
python tools/verify_release_artifact.py --tree .
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest
```

No network services, private keys, cloud accounts, or external datasets are required.

The evaluation uses deterministic synthetic fixtures. Embedded demo keys are public fixture material and provide reproducibility only.

## Proof receipt

The generated receipt files are written to:

```text
receipts/haltseal-gateway-proof-receipt.json
receipts/haltseal-gateway-proof-receipt.md
receipts/haltseal-gateway-proof-receipt.txt
```

Use the text receipt as a copy-paste block for technical review, procurement intake, or written-scope diligence routing. It is not a certificate, not a production attestation, not a security certification, and not a patent-license grant.

## Full hardened preflight

```bash
make qa-full
```

This checks the public eval, schema validation, proof receipt, transparency bundle, deterministic Ed25519 profile, independent recomputation, manifest/source tree, release gate, strict release gate, release artifact verifier, zip audit, and pytest suite.
