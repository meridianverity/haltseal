# Vector guide

| Vector | Expected | Purpose |
|---|---:|---|
| H01 | ALLOW | Current permit exactly matches protected action |
| H02 | HOLD | Signed head is stale |
| H03 | DENY | Permit is expired |
| H04 | DENY | Action digest mismatch |
| H05 | DENY | Replay via nonce/monotonic tuple |
| H06 | DENY | Audience mismatch |
| H07 | DENY | Permit is revoked |
| H08 | HOLD | Continuity proof missing |
| H09 | DENY | Permit missing |
| H10 | DENY | Permit signature invalid after field mutation |
| H11 | DENY | Context label mismatch |
| H12 | HOLD | Signed-head conflict |
| H13 | DENY | Unsupported implementation hook |
| H14 | DENY | Signed-head ID mismatch |
| H15 | HOLD | Witness cosignature missing |
| H16 | DENY | Signed-head signature invalid |
| H17 | DENY | Signed permit attempts to expand to another destination |
| H18 | DENY | Permit is not yet valid |
| H19 | DENY | Signed-head timestamp is from the future |
| H20 | HOLD | Continuity proof points at a different signed head |
| H21 | DENY | Monotonic replay counter does not advance |
| H22 | DENY | ICC head ID is outside the reviewed boundary |
| H23 | DENY | License tier fails the synthetic GLG policy lock |
| H24 | DENY | Jurisdictional fingerprint fails the synthetic GLG policy lock |
| H25 | DENY | ELV measurement hash fails the reviewed attestation lock |
| H26 | DENY | Action policy epoch is outside the reviewed boundary |
| H27 | DENY | Permit replay tuple does not match the captured action |
| H28 | DENY | Revocation-list policy denies the permit identifier |
| H29 | DENY | Unknown action field attempts boundary expansion |
| H30 | DENY | Signed-head shape is malformed |
| H31 | DENY | Packet time and policy time disagree |
| H32 | DENY | Signature algorithm metadata mismatches the configured synthetic profile |

The vector set is intentionally negative-heavy because fail-closed behavior is easier to audit when the failure modes are explicit.

The public artifact intentionally contains a few malformed sub-object vectors. Those vectors are not examples of valid input shape; they prove that malformed public-eval packets return deterministic fail-closed decisions rather than unhandled exceptions.
