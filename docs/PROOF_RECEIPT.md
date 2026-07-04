# HALTSEAL Gateway Proof Receipt

Turn a public eval run into a review-ready proof receipt.

The proof receipt is a portable public-evaluation record for technical review and written-scope diligence handoff. It lets a reviewer carry the result of a local HALTSEAL public evaluation into an internal security ticket, legal review note, procurement intake, or licensing-scope discussion without exposing private implementation depth.

It is intentionally narrow:

```text
Not a certificate.
Not a production attestation.
Not a patent-license grant.
Not a security certification.
```

## What the receipt proves in the public package

```text
I verified the release SHA-256.
I reproduced the 32-vector public evaluation.
I confirmed the enabled public-eval boundary: network_egress_gateway.
I confirmed the public/private boundary: synthetic evaluation only.
I confirmed the rights posture: no production SDK · no patent license.
```

## Generate the receipt

```bash
python tools/run_public_eval.py
python tools/export_proof_receipt.py --out haltseal-gateway-proof-receipt.json
python tools/verify_proof_receipt.py haltseal-gateway-proof-receipt.json
```

Expected headline:

```text
HALTSEAL Gateway Proof Receipt: PASS
Release SHA-256: OK
Public evaluation: 32 / 32 PASS
Boundary: network_egress_gateway
Rights posture: no production SDK · no patent license
```

## Default outputs

```text
receipts/haltseal-gateway-proof-receipt.json
receipts/haltseal-gateway-proof-receipt.md
receipts/haltseal-gateway-proof-receipt.txt
```

The JSON file is the machine-readable receipt. The Markdown file is the one-page review receipt. The text file is the copy-paste block for internal intake systems.

## Receipt fields

```text
artifact
receipt_type
receipt_version
receipt_tool_release
public_eval_version
repository
release
release_sha256
vector_result
enabled_public_eval_hook
public_boundary
rights_posture
receipt_purpose
evidence_hash
evidence_sig
```

The `evidence_hash` is computed from canonical receipt bytes under the public proof-receipt context. The synthetic signature is reproducibility evidence only; it is not a production trust root and not a certification.

## Public/private boundary

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
```
