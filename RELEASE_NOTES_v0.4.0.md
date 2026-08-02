# HALTSEAL Public Resolve Challenge v0.4.0

## Release classification

```text
Hosted synthetic evaluation contract
Public verification surface
No live provider call
No payment credentials
No production or patent rights
```

v0.4.0 extends the immutable v0.3.2 local Gateway Proof Pack with a network-addressable public contract for one server-issued synthetic authority and one complete final synthetic payment action.

The public surface returns `ACCEPT`, `HOLD`, or `REFUSE` together with an Ed25519-signed receipt that can be verified without trusting an MVG verification endpoint.

## Crown behavior

```text
Exact current action
→ ACCEPT
→ exactly one synthetic request record

Material mutation
→ REFUSE
→ zero request records

Prior synthetic outcome unknown
→ HOLD
→ zero new request records

Identical transport retry
→ same stored response
→ zero additional records

New economic-use attempt after consumption
→ REFUSE
→ zero additional records
```

## Included public surface

- OpenAPI 3.1.1 contract;
- closed JSON Schemas;
- three fixed synthetic authority profiles;
- decision and reason-code registry;
- signed sample receipts;
- public sample JWKS;
- Python and TypeScript offline verifiers enforcing one closed receipt profile;
- local deterministic in-memory contract mock aligned to the OpenAPI success and problem-response contract;
- 32 public-resolve conformance vectors;
- release manifest, SBOM, provenance, and QA record;
- surgical website copy and launch checklist.

## Surgical verifier and HTTP-contract closure

The release candidate was hardened before publication so that the public verification claim and local HTTP contract are exact rather than illustrative:

- both offline verifiers enforce issuer, audience, profile version, evaluation-only boundary, complete closed receipt fields, strict action and authority types, and decision-specific emission/consumption invariants;
- Python and TypeScript are exercised against one 20-case parity corpus, including signed malformed receipts;
- compact JWS segments must be canonical, unpadded base64url and reject padding, `+`, `/`, whitespace, invalid lengths, and non-canonical pad bits;
- an idempotency-key conflict returns `409 application/problem+json`; validation returns `400 application/problem+json`; and a fail-closed internal failure returns `503 application/problem+json`; and
- HTTP-level regression tests exercise the running local mock rather than only the engine exception.

## Deliberately excluded

- hosted resolver source;
- durable one-use persistence source;
- live evaluation signing key;
- production policy or revocation sources;
- provider adapters or provider request mapping;
- payment credentials or payment tokens;
- KMS/HSM configuration;
- protected credentialed emitter;
- live reconciliation or reversal internals;
- buyer trust roots, claim maps, or commercial material.

## Publication gate

Publish this release only after the MVG-controlled hosted endpoint passes the exact launch gate in `docs/public-resolve/LAUNCH_GATES.md`. Before activation, the repository remains fully usable through the local contract mock and frozen signed samples.
