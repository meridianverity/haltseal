# HALTSEAL Gateway Proof Pack v0.3.2-hardened-eval

This release provides a **public-safe, synthetic, runnable Gateway Proof Pack** for HALTSEAL permit-before-action review at one protected external-effect boundary.

It keeps the narrow v0.3.0 public evaluation boundary intact and adds the v0.3.2 hardened review layer: proof receipt, transparency bundle, deterministic Ed25519 proof profile, independent recomputation, release-artifact verification, strict manifest/source-tree locking, and full QA preflight.

The public evaluation remains intentionally narrow:

```text
One protected action.
One enabled public-eval gateway: network_egress_gateway.
One permit path.
One fail-closed decision surface.
Synthetic evaluation only.
No production SDK.
No patent license.
```

## What this release demonstrates

The packet demonstrates a gateway control path for one protected action:

```text
canonical action representation
→ action_digest
→ short-lived audience-bound permit check
→ signed-head freshness / continuity posture
→ replay and policy-lock checks
→ ALLOW, HOLD, or fail-closed DENY before action
```

It is designed for public technical review, security review, procurement intake, standards-adjacent boundary discussion, and written-scope diligence routing.

## Hardened materials included

```text
32 deterministic public-eval vectors.
47 pytest checks.
Portable HALTSEAL Gateway Proof Receipt.
Receipt JSON, Markdown, and copy-paste diligence block.
Receipt schema and verifier.
Merkle transparency bundle with selected inclusion proofs.
Deterministic Ed25519 public-eval proof profile.
Standard-library independent recomputation checker.
Fresh-archive release verifier.
Regenerated manifest and source-tree locks.
GitHub workflow, issue template, PR template, and release hygiene checks.
```

## Release assets

```text
haltseal-gateway-proof-pack-v0.3.2-hardened-eval.zip
haltseal-gateway-proof-pack-v0.3.2-hardened-eval.zip.sha256.txt
```

## Recommended verification

```bash
sha256sum -c haltseal-gateway-proof-pack-v0.3.2-hardened-eval.zip.sha256.txt
unzip haltseal-gateway-proof-pack-v0.3.2-hardened-eval.zip
cd haltseal-gateway-proof-pack-v0.3.2-hardened-eval
python -m pip install -r requirements.txt
make qa-full
```

Expected public evaluation result:

```text
Result: 32 / 32 PASS
Public boundary: synthetic evaluation only; no production SDK; no patent license.
```

Expected hardened checks:

```text
Manifest verification: PASS
Packet validation: PASS
Release gate: PASS
Strict release gate: PASS
Independent recomputation: 16 / 16 PASS
Pytest: 47 passed
Release artifact verification: PASS
Zip audit: PASS
```

## Public-safety and scope boundaries

This release contains synthetic public evaluation artifacts only.

It does not process live payments, store payment credentials, call live processors, operate a production gateway, or provide production payment, wallet, issuer, PSP, network-token, settlement-rail, cloud, endpoint, firmware, hypervisor, robotics, or device-control functionality.

It does not include customer data, production deployment material, non-public implementation mapping, claim charts, evidence-of-use materials, target-company analysis, field-of-use analysis, commercial terms, or confidential information.

This release is not a certification, conformance program, production authorization, formal standards-track output, IETF endorsement, legal opinion, valuation request, licensing demand, commercial commitment, patent-license grant, trademark-license grant, or implementation-rights grant.

Publication, download, execution, issue discussion, or contribution does not grant any patent license or commercial deployment right.

## Review focus

Useful review includes:

- whether the field model is understandable;
- whether canonical action binding is deterministic;
- whether `action_digest` binding is reproducible;
- whether malformed inputs fail closed;
- whether HOLD versus DENY is clear for freshness and continuity cases;
- whether replay, policy epoch, ICC, GLG, and ELV locks are understandable as public-eval fixtures;
- whether the proof receipt is useful for reviewer, counsel, procurement, and written-scope diligence handoff; and
- whether additional negative vectors or conformance vectors should be added in future public iterations.

## Release posture

This packet is meant to make the public boundary easier to inspect without revealing private licensing depth.

Engineers get a runnable, falsifiable artifact. Reviewers get deterministic vectors and independent recomputation. Counsel and procurement get clean public-safety boundaries. Implementation mapping, field-of-use, claim mapping, commercial terms, and production rights remain written-scope.
