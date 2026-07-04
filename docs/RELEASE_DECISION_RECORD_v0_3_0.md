# Release decision record — v0.3.0-public-eval

Decision: publishable as a public-safe synthetic evaluation artifact after v0.3 hardening and final archive hygiene.

Rationale:

- The artifact is runnable in minutes and produces deterministic evidence hashes.
- The public/private boundary is explicit across README, license, security notes, and handoff docs.
- The code demonstrates a single reviewed action boundary rather than a broad implementation.
- The evaluation uses synthetic fixtures and does not expose production APIs, deployment internals, commercial terms, or patent-license terms.
- The final pre-public gate synchronizes QA counts, vector counts, test counts, transparency report counts, and boundary-mapper wording with the code.

Release condition: final ZIP must be rebuilt from a clean tree after tests, with manifest verification and ZIP audit passing.
