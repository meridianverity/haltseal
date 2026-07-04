# Release readiness — v0.3.0-public-eval

Status: ready for public Git review after final ZIP hygiene and counsel review of public wording.

This is a public evaluation artifact, not a legal filing, not a production integration, and not a patent-license offer.

Readiness checks:

- Clear repo purpose: one protected action, one gateway, one permit path, one evidence shape.
- Public/private separation: implementation depth, legal mapping, commercial terms, production APIs, and licensing terms remain outside the repo.
- Determinism: vectors, expected results, evidence hashes, manifests, and aggregate reports are reproducible.
- Safety posture: malformed inputs produce deterministic fail-closed decisions rather than unhandled exceptions.
- Hygiene: generated caches and compiled bytecode are excluded from the release ZIP.

Recommended tag: `v0.3.0-public-eval`.
