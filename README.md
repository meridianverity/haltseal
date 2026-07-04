# HALTSEAL Gateway Proof Pack

**Public-safe · synthetic · runnable · fail-closed · no patent license · written-scope depth**

HALTSEAL Gateway Proof Pack is a synthetic, public-safe evaluation artifact for permit-before-action runtime control at one protected action boundary.

It demonstrates canonical action binding, short-lived permit checks, signed-head freshness/continuity posture, fail-closed HOLD/DENY behavior, anti-replay posture, boundary mapping, schema validation, malformed-input denial, audit-ready evidence shapes, and a portable proof receipt for written-scope diligence handoff.

It is not production software, not a production SDK, not a certification program, not endorsed as a formal standards-track output, not a private legal mapping, and grants no patent license.

## The 3-minute run

```bash
python -m pip install -r requirements.txt
python tools/run_public_eval.py
```

Expected summary:

```text
HALTSEAL Gateway Proof Pack — synthetic public evaluation
...
Result: 32 / 32 PASS
Public boundary: synthetic evaluation only; no production SDK; no patent license.
```

Generate the proof receipt:

```bash
python tools/export_proof_receipt.py
python tools/verify_proof_receipt.py
```

Expected receipt headline:

```text
HALTSEAL Gateway Proof Receipt: PASS
Release SHA-256: OK
Public evaluation: 32 / 32 PASS
Boundary: network_egress_gateway
Rights posture: no production SDK · no patent license
```

## What this proves publicly

The artifact narrows the review to one protected action:

```text
POST /external-tool/send-sensitive-payload
```

The synthetic gateway captures:

```text
method, destination, tenant_id, agent_id, mission_id, payload_sha256,
policy_epoch, signed_head_id, nonce, monotonic_counter, implementation_hook
```

The verifier checks:

```text
canonical bytes, action digest, permit signature, permit status, audience binding,
signed-head freshness, continuity proof, witness posture, replay state, policy-epoch
lock, ICC head lock, synthetic GLG locks, ELV measurement lock, strict public-eval
boundary mapping, and malformed-input handling
```

The result is deliberately simple:

```text
ALLOW only if the exact proof is current and inside the public-eval boundary.
HOLD when freshness or continuity cannot be established.
DENY when permit, digest, audience, signature, revocation, context, hook, boundary,
timestamp, policy, replay, shape, or signed-head checks fail.
```

## v0.3.1 proof-receipt focus

v0.3.1-proof-receipt keeps the v0.3.0 public evaluation boundary intact and adds a review-ready proof receipt: JSON receipt, Markdown one-pager, copy-paste diligence block, receipt schema, receipt verifier, and tests that keep the receipt aligned with QA results.

The underlying public evaluation remains v0.3.0-public-eval: 32 deterministic vectors, policy-epoch/ICC/GLG/ELV locks, schema-validated packets/results/evidence, malformed-input fail-closed tests, release hygiene checks, and reproducible manifest generation.

## Public/private split

Public here means reviewable, deterministic, and safe to run. It does **not** mean production use, commercial deployment, claim mapping, implementation depth, or license grant.

Private written-scope diligence is where implementation maps, field-of-use terms, commercial terms, production APIs, and patent-license questions belong.

## Repository map

```text
haltseal_eval/       synthetic verifier code
vectors/             32 deterministic gateway vectors
examples/            one JSON packet per vector plus proof-receipt examples
schemas/             strict review schemas for packet/result/evidence/receipt shapes
tools/               eval runner, packet validator, proof receipt, release gate, manifest builder
docs/                public boundary, reviewer guide, proof receipt, licensing handoff, QA report
receipts/            generated JSON, Markdown, and copy-paste proof receipt outputs
tests/               reproducibility, schema, malformed-input, receipt, and fail-closed tests
```

## Reviewer path

1. Run `python tools/run_public_eval.py`.
2. Generate `python tools/export_proof_receipt.py`.
3. Verify `python tools/verify_proof_receipt.py`.
4. Inspect `vectors/haltseal_gateway_vectors.json`.
5. Read `docs/PUBLIC_BOUNDARY.md` and `docs/PROOF_RECEIPT.md`.
6. Use `docs/REVIEWER_GUIDE.md` for a 30-minute technical review.
7. Use `docs/DILIGENCE_PACKET.md` and `docs/LICENSING_HANDOFF.md` only for written-scope diligence routing.

## Legal/IP posture

See `LICENSE-EVALUATION.md` and `PATENT-NOTICE.md` before running, redistributing, or discussing implementation depth.
