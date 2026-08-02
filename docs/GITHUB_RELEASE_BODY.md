# HALTSEAL Public Resolve Challenge v0.4.0

**Call one exact action. Receive one bounded decision. Verify the receipt yourself.**

This release adds a hosted-synthetic API contract and independent receipt-verification surface to the immutable HALTSEAL v0.3.2 local Gateway Proof Pack lineage.

A server-issued synthetic authority challenge is resolved against one complete final synthetic payment action:

```text
ACCEPT  → exactly one synthetic request record, at most once
HOLD    → no new request while a prior synthetic outcome is unknown
REFUSE  → no request
```

Each result carries an Ed25519-signed receipt. The receipt can be verified offline with either included verifier; both enforce the same closed receipt profile, exact decision/emission/consumption invariants, and canonical unpadded compact-JWS encoding. The hosted `/verify` endpoint is only a convenience.

## Public API

```text
POST /haltseal/evaluation/v1/challenges
POST /haltseal/evaluation/v1/resolve
POST /haltseal/evaluation/v1/verify
GET  /haltseal/evaluation/v1/jwks.json
```

Canonical hosted endpoint:

```text
https://eval.meridianverity.com/haltseal/evaluation/v1
```

The release must be published only after the hosted launch gate passes. The local in-memory contract mock remains available independently of hosted activation.

## What is public

```text
OpenAPI contract
closed JSON Schemas
fixed synthetic authority profiles
decision and reason-code registry
signed sample receipts
public sample verification key
Python and TypeScript offline verifiers
32 conformance vectors
local in-memory contract mock
manifest, SBOM, provenance, and QA record
```

## What remains controlled

```text
hosted resolver implementation
atomic durable one-use state
live evaluation signer
rate and abuse controls
production policy and revocation sources
provider adapters and provider request mapping
protected credentialed emitter
KMS/HSM configuration
live reconciliation and reversal
buyer trust roots and confidential diligence material
```

## 60-second local proof

```bash
python -m pip install -r requirements.txt
PYTHONPATH=. python -m haltseal_resolve.mock_server --host 127.0.0.1 --port 8787
```

In another terminal:

```bash
bash examples/curl/run-local-challenge.sh
```

Verify a frozen receipt offline:

```bash
PYTHONPATH=. python -m haltseal_resolve.cli verify \
  examples/receipts/accept-exact.receipt.jws \
  --jwks keys/sample-evaluation-jwks.json

node verifier/typescript/haltseal_verify.mjs \
  examples/receipts/accept-exact.receipt.jws \
  keys/sample-evaluation-jwks.json
```

## Replay semantics

```text
Same challenge + same action + same Idempotency-Key
→ stored response returned
→ zero additional records

Same authority + new Idempotency-Key after consumption
→ REFUSE · AUTHORIZED_USE_ALREADY_CONSUMED
→ zero additional records
```

A transport retry is not a new economic use.

## Verification record

```text
Historical Gateway Proof Pack vectors: 32 / 32 PASS
Public Resolve Challenge vectors:       32 / 32 PASS
Combined public pytest:                 80 / 80 PASS
Python/TypeScript verifier parity:      20 / 20 PASS
HTTP contract regression:               5 / 5 PASS
Hosted private-runtime tests:           11 / 11 PASS
64-way one-use concurrency:             exactly one synthetic record
Live provider egress:                   zero
```

The hosted private-runtime counts are release-preparation evidence only; private runtime source is not part of the public release asset.

## Hard boundary

This is synthetic evaluation, not a payment sandbox or live payment service. It accepts no payment credentials, user-supplied endpoints, callbacks, PAN, CVV, provider secrets, or payment tokens. It makes no live provider request and grants no production, implementation, certification, trademark, or patent rights.

## Recommended review

- inspect the OpenAPI contract and closed schemas;
- call the local or hosted synthetic challenge;
- mutate one material field and confirm `REFUSE` with no request;
- reproduce `HOLD · NO_NEW_REQUEST`;
- retry an identical request and confirm zero additional records;
- attempt a new use after consumption and confirm `REFUSE`;
- verify the signed receipt offline;
- inspect the public/private boundary and launch-gate evidence.

## Release assets

```text
haltseal-public-resolve-challenge-v0.4.0.zip
haltseal-public-resolve-challenge-v0.4.0.zip.sha256.txt
openapi-haltseal-public-resolve-v1.yaml
haltseal-public-resolve-schemas-v1.zip
haltseal-public-resolve-sample-receipts-v1.zip
haltseal-public-resolve-verifiers-v1.zip
HALTSEAL_PUBLIC_RESOLVE_RELEASE_MANIFEST.json
SBOM.spdx.json
provenance.json
```

Publication, API use, download, execution, issue discussion, or contribution does not grant a patent license or commercial deployment right. See `LICENSE-EVALUATION.md`, `PATENT-NOTICE.md`, and `docs/public-resolve/API_EVALUATION_TERMS.md`.
