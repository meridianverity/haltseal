# HALTSEAL Public Resolve Challenge implementation plan

## Objective

Create one public, callable, synthetic proof surface between the browser-local HALTSEAL experience and a confidential buyer-owned provider pilot.

## Immutable boundaries

```text
Public GitHub repository
= contract, schemas, vectors, samples, public keys, verifier, local mock, release record

MVG-controlled evaluation service
= hosted resolver, durable one-use state, evaluation signer, abuse controls

Written-scope buyer environment
= real authority sources, protected credentialed emitter, provider route, reconciliation, reversal
```

## Workstreams

### 1. Contract freeze

- freeze three fixed profiles;
- freeze action and authority schemas;
- freeze decision, reason-code, and emission semantics;
- freeze challenge, idempotency, retry, and economic-use behavior;
- publish OpenAPI 3.1.1 and closed schemas.

### 2. Public verification

- publish sample JWKS;
- publish signed ACCEPT, HOLD, and REFUSE receipts;
- publish Python and TypeScript offline verifiers;
- publish tamper vectors and conformance runner;
- require strict JSON and exact semantic replay.

### 3. Hosted evaluation runtime

- use a dedicated evaluation-only signing key;
- persist challenge, attempt, and synthetic emission state atomically;
- return the identical stored response for identical retries;
- reject idempotency-key conflicts;
- fail closed if state or signing is unavailable;
- deny all provider egress;
- accept no credentials or URLs;
- apply payload, rate, and retention limits.

### 4. Release assurance

- preserve v0.3.2 unchanged;
- generate deterministic public release assets;
- produce manifest, SBOM, provenance, and QA summary;
- verify all SHA-256 sidecars from fresh downloads;
- run 64-way concurrency and strict-input attacks;
- obtain a named bounded external review before representing independent validation.

### 5. Website conversion

- keep the executive hero unchanged;
- add the developer proof block after the browser experience;
- link hosted API, curl example, verifier, and OpenAPI;
- preserve the buyer-owned pilot CTA;
- never imply a live payment, network endorsement, or deployment right.

## Promotion sequence

```text
Local contract and signed samples
→ hosted evaluation launch gate
→ public GitHub release and website block
→ named external review
→ qualified developer usage
→ one written-scope buyer-owned provider boundary
```

## Stop condition

Do not expand the public API into arbitrary policy upload, user-defined provider endpoints, credentials, callbacks, or a general authorization service. New production semantics belong in buyer-owned diligence, not the public challenge.
