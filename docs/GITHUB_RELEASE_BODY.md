# HALTSEAL Gateway Proof Pack v0.3.1-proof-receipt

This release keeps the **v0.3.0 public evaluation boundary** intact and adds a portable **HALTSEAL Gateway Proof Receipt** layer for security review, legal intake, procurement routing, internal champion forwarding, and written-scope diligence handoff.

The underlying public evaluation remains intentionally narrow:

```text
One protected action.
One enabled public-eval gateway: network_egress_gateway.
One permit path.
One fail-closed decision surface.
Synthetic evaluation only.
No production SDK.
No patent license.
```

v0.3.1-proof-receipt adds:

```text
Proof receipt JSON.
One-page Markdown receipt.
Copy-paste procurement / diligence block.
Receipt schema.
Receipt verifier.
Receipt consistency tests.
Release-package hygiene.
```

## Release assets

```text
haltseal-gateway-proof-pack-v0.3.1-proof-receipt.zip
haltseal-gateway-proof-pack-v0.3.1-proof-receipt.zip.sha256.txt
```

## Recommended verification

```bash
sha256sum -c haltseal-gateway-proof-pack-v0.3.1-proof-receipt.zip.sha256.txt
unzip haltseal-gateway-proof-pack-v0.3.1-proof-receipt.zip
cd haltseal-gateway-proof-pack-v0.3.1-proof-receipt
python -m pip install -r requirements.txt
make all
HALTSEAL_STRICT_TREE=1 python tools/release_gate.py
python tools/export_proof_receipt.py
python tools/verify_proof_receipt.py
```

Expected result:

```text
Public evaluation: 32 / 32 PASS
Packet validation: PASS
Transparency report generation: PASS
Synthetic evaluation attestation: PASS
Proof receipt export: PASS
Proof receipt verification: PASS
Manifest verification: PASS
Pytest suite: 40 passed
Release gate: PASS / findings: 0
Strict release gate: PASS / findings: 0
Zip audit: PASS / findings: 0
```

The proof receipt headline should include:

```text
HALTSEAL Gateway Proof Receipt: PASS
Release SHA-256: OK
Public evaluation: 32 / 32 PASS
Boundary: network_egress_gateway
Rights posture: no production SDK · no patent license
```

## Public boundary

This release is designed to be reviewed, reproduced, and discussed without exposing private implementation depth.

Public:

```text
Synthetic fixtures.
Deterministic vectors.
Schema-backed validation.
Manifest verification.
Fail-closed malformed-input handling.
Boundary-mapper consistency.
Proof receipt generation and verification.
Copy-paste diligence block.
Reproducible public QA.
```

Not public:

```text
Production SDK.
Production API.
Private deployment internals.
Claim charts.
Commercial terms.
Field-of-use terms.
Patent-license grant.
Certification or conformance program.
Official standards artifact.
```

This release is not a production SDK, production attestation, security certification, conformance program, legal opinion, claim chart, commercial offer, field-of-use agreement, or patent-license grant.

The bundled proof receipt is portable review evidence for the canonical public evaluation result. Implementation depth, claim mapping, field-of-use terms, commercial terms, and patent-license questions remain written-scope only.
