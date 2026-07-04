# Quickstart

```bash
python -m pip install -r requirements.txt
python tools/run_public_eval.py
python tools/validate_public_packet.py
python tools/export_proof_receipt.py
python tools/verify_proof_receipt.py
python -m pytest -q
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
