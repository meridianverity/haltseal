# Public-evaluation threat model

This threat model is scoped to the synthetic artifact only.

## Covered public-eval failures

- Missing permit
- Expired permit
- Future-issued permit
- Revoked permit
- Revocation-list denial
- Bad permit signature
- Signature-algorithm metadata mismatch
- Context label mismatch
- Action digest mismatch
- Unsupported protected-action destination
- Unsupported implementation hook
- Unknown protected-action fields
- Policy-epoch mismatch
- Packet time / validation-policy time mismatch
- Audience mismatch
- ICC head mismatch
- License-tier mismatch
- Jurisdictional-fingerprint mismatch
- ELV measurement / attestation mismatch
- Stale signed head
- Signed-head conflict
- Signed-head ID mismatch
- Signed-head timestamp from the future
- Signed-head shape invalid
- Invalid signed-head signature
- Missing witness cosignature
- Missing continuity proof
- Continuity-proof mismatch
- Replay via nonce/monotonic tuple
- Replay where nonce changes but monotonic counter does not advance
- Permit replay tuple mismatch against captured action
- Malformed public-eval packets returning deterministic fail-closed decisions

## Out of scope

- Production non-bypassability
- Kernel driver internals
- Firmware microcode internals
- Hypervisor internals
- Accelerator queue or doorbell implementation details
- Cloud deployment architecture
- Hardware attestation deployment
- Commercial licensing
- Claim mapping
- Legal advice or infringement analysis

The out-of-scope items require written-scope diligence.
