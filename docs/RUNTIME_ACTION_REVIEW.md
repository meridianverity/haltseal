# Runtime action review

The runtime action review is the public-evaluation path from action capture to disposition.

1. Capture the protected action fields.
2. Canonicalize the action bytes under a HALTSEAL context label.
3. Compute the action digest.
4. Verify the permit context label and fixture signature.
5. Check expiration and revocation status.
6. Check audience binding.
7. Check signed-head freshness and witness posture.
8. Check continuity proof posture.
9. Check replay state using nonce and monotonic counter.
10. Emit ALLOW, HOLD, or DENY with an evidence-only record.

The public review intentionally does not include production device hooks or implementation maps.
