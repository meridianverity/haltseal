# HALTSEAL Public Resolve Challenge

**Call one exact action. Receive one bounded decision. Verify the receipt yourself.**

HALTSEAL Public Resolve Challenge is a hosted, synthetic, API-addressable evaluation surface for one receiver-owned payment decision. A server-issued authority challenge is resolved against one complete final synthetic payment action and returns:

```text
ACCEPT  → one synthetic request record, at most once
HOLD    → no new request while a prior synthetic outcome is unknown
REFUSE  → no request
```

Every bounded decision includes an Ed25519-signed receipt that can be verified offline with the public Python or TypeScript verifier. Both verifiers enforce the same closed receipt profile, decision-specific emission and consumption invariants, and canonical unpadded compact-JWS encoding.

## Hard public boundary

```text
Synthetic evaluation only
No payment credentials accepted
No live provider call
No user-supplied URL or callback
No production SDK or service rights
No implementation or patent license
```

The hosted endpoint is designed to run at:

```text
https://eval.meridianverity.com/haltseal/evaluation/v1
```

**Do not publish the v0.4.0 release until the hosted launch gate reports PASS.** The public repository remains useful before launch through the local in-memory contract mock and signed sample receipts.

## 60-second local proof

```bash
python -m pip install -r requirements.txt
PYTHONPATH=. python -m haltseal_resolve.mock_server
```

In a second terminal:

```bash
bash examples/curl/run-local-challenge.sh
```

Verify a frozen sample receipt without trusting any MVG verification endpoint:

```bash
PYTHONPATH=. python -m haltseal_resolve.cli verify \
  examples/receipts/accept-exact.receipt.jws \
  --jwks keys/sample-evaluation-jwks.json

node verifier/typescript/haltseal_verify.mjs \
  examples/receipts/accept-exact.receipt.jws \
  keys/sample-evaluation-jwks.json
```

## Public HTTP contract

```text
POST /challenges  → server-issued synthetic authority
POST /resolve     → ACCEPT | HOLD | REFUSE + signed receipt
POST /verify      → convenience verification
GET  /jwks.json   → hosted evaluation verification keys
```

Canonical OpenAPI contract:

```text
openapi/haltseal-public-resolve-v1.yaml
```

## Why the server issues authority

The caller may propose an action but may not define the authority against which that action is judged. Otherwise a caller could simply authorize its own action. Each challenge therefore fixes a synthetic amount, currency, merchant, terms, destination, currentness, and one-use state before `/resolve` is called.

## Replay semantics

Two cases are deliberately separated:

```text
Same challenge + same exact action + same Idempotency-Key
→ stored response returned
→ no additional synthetic request record

Same authority after its one authorized use, but a new Idempotency-Key
→ REFUSE · AUTHORIZED_USE_ALREADY_CONSUMED
→ no additional synthetic request record
```

A transport retry is not a new economic use.

## Public repository contents

```text
openapi/                    versioned HTTP contract
schemas/public-resolve/     closed JSON Schemas
profiles/                   fixed synthetic authority profiles
reason-codes/               decision and reason-code registry
haltseal_resolve/           offline verifier and in-memory contract mock
verifier/typescript/        dependency-free Node verifier
examples/                   curl, Python, TypeScript, and signed receipts
vectors/public-resolve/     positive and adversarial conformance vectors
keys/                       public sample verification key only
release/v0.4.0/             release manifest, SBOM, provenance, QA
website/                    surgical HALTSEAL page copy patch
```

The historical v0.3.2 Gateway Proof Pack remains preserved in the same repository lineage. It demonstrates a local generic gateway proof. v0.4.0 adds the callable synthetic payment decision and independent receipt-verification surface; it does not publish the hosted runtime or the real effect-custody kernel.

## Public/private split

### Public

```text
contract
schemas
profiles
reason codes
sample receipts
public verification keys
Python and TypeScript verifiers
conformance vectors
local in-memory mock
release manifest, SBOM, and provenance
```

### Controlled by MVG

```text
hosted resolver runtime
atomic durable one-use state
live evaluation signing key
rate and abuse controls
operational telemetry
```

### Written-scope buyer diligence only

```text
production policy and revocation sources
provider adapter and provider request mapping
protected credentialed emitter
KMS/HSM configuration
buyer trust roots
live provider reconciliation and reversal
claim charts, evidence-of-use, and commercial terms
```

## Verification

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. python -m pytest -q
PYTHONPATH=. python tools/public_resolve/run_verifier_parity.py
PYTHONPATH=. python tools/public_resolve/run_http_contract.py
node verifier/typescript/haltseal_verify.mjs \
  examples/receipts/accept-exact.receipt.jws \
  keys/sample-evaluation-jwks.json
```

The public challenge does not establish production non-bypassability, payment processing, network compatibility, certification, partnership, independent validation, production readiness, or implementation rights.

## Review path

1. Read `docs/public-resolve/PUBLIC_API_BOUNDARY.md`.
2. Inspect the OpenAPI contract and closed schemas.
3. Run the local contract mock.
4. Verify the signed samples offline.
5. Run the public conformance suite.
6. Inspect `docs/public-resolve/PRIVATE_IMPLEMENTATION_BOUNDARY.md`.
7. For a real effect boundary, nominate one buyer-owned purchase or payout under written scope.

## Legal/IP posture

See `LICENSE-EVALUATION.md`, `PATENT-NOTICE.md`, and `docs/public-resolve/API_EVALUATION_TERMS.md`. Publication, download, API access, execution, issue discussion, or contribution grants no patent license, production right, commercial deployment right, certification, or trademark license.
