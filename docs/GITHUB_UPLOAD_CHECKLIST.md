# GitHub upload checklist — HALTSEAL Public Resolve Challenge v0.4.0

## Canonical repository

```text
https://github.com/meridianverity/haltseal
```

Do not create a second public repository. Preserve `v0.3.2-hardened-eval` as an immutable historical local proof.

## Repository metadata

**About description**

```text
Hosted-synthetic exact-action challenge with ACCEPT, HOLD, or REFUSE and independently verifiable signed receipts. No live provider call.
```

**Website**

```text
https://meridianverity.com/haltseal/
```

**Topics**

```text
ai-agents
agentic-commerce
payments
authorization
api-security
receipts
openapi
jws
idempotency
fail-closed
synthetic-evaluation
```

## Tag and title

```text
Tag:   v0.4.0-public-resolve-challenge
Title: HALTSEAL Public Resolve Challenge v0.4.0 — Hosted Synthetic Evaluation
```

## Pre-publication requirements

```bash
python -m pip install -r requirements.txt
make qa-full
python tools/package_release.py
```

In addition, the separately controlled hosted runtime must pass:

```text
strict raw-body parsing
state-store fail-closed behavior
signer fail-closed behavior
64-way one-use concurrency
zero provider egress
rate limits and payload caps
hosted JWKS verification
local/offline semantic replay
health/readiness probes
```

Do not publish the release as active until the hosted endpoint returns ready and the public website links resolve successfully.

## Release body

Copy the content of:

```text
docs/GITHUB_RELEASE_BODY.md
```

## Public release assets

Upload only the files listed in:

```text
release/v0.4.0/PUBLIC_GITHUB_ASSET_INDEX.json
```

Never upload:

```text
HALTSEAL_v0_4_0_PRIVATE_HOSTED_RUNTIME.zip
signing seed or private key
SQLite state
runtime environment files
provider credentials
buyer trust roots
provider adapter or protected-emitter code
confidential claim or target material
```

## Final visual and link check

- release body renders correctly;
- hosted endpoint and website links use HTTPS;
- OpenAPI file resolves;
- sample receipt verifies from a fresh download;
- JWKS contains public keys only;
- no endpoint accepts credentials, URLs, or callbacks;
- all public assets match their SHA-256 sidecars;
- GitHub release is not marked as a prerelease after launch activation;
- previous tags and assets remain unchanged.
