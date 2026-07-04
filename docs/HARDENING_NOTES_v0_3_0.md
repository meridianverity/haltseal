# Hardening notes — v0.3.0-public-eval

v0.3.0-public-eval keeps the artifact narrow and public-safe while increasing reviewer confidence.

Key hardening additions:

- 32 deterministic vectors covering allow, hold, and denial outcomes.
- Policy-epoch locking for the single reviewed action boundary.
- ICC head, GLG license-tier, jurisdictional fingerprint, and ELV measurement locks.
- Revocation-list denial independent of the permit's embedded revoked flag.
- Signed-head shape denial and signature metadata denial.
- Schema validation for packets, protected actions, permits, signed heads, verifier results, and evidence records.
- Reproducible manifest generation and final ZIP hygiene audit.
- Attestation-count lock: vector/test/QA counts are generated and checked before release.
- Boundary-doc lock: the public mapper names only the single enabled hook.

The package remains synthetic. It is not production software, not a production SDK, not a certification program, not an official standards artifact, not a legal mapping, and grants no patent license.
