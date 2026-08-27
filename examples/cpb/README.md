# CPB identifier vectors for the HALTSEAL public resolve receipt

This directory publishes owner-authored conformance vectors for the proposed
CPB artifact type `haltseal-public-resolve-receipt`, profile
`haltseal-public-resolve-1`.

## Registered construction under test

The identifier context is intentionally narrow:

- algorithm: `as-transmitted`
- byte-boundary selector: RFC 7515 §5.1, **JWS Signing Input**
- pre-image: the exact ASCII bytes `BASE64URL(protected-header) + "." + BASE64URL(payload)`
- digest: SHA-256
- representation: bare 64-character lowercase hexadecimal

The compact-JWS signature segment is **outside** the identifier pre-image.

These vectors do not define, register, or modify HALTSEAL's inner
`action_digest` or `authority_digest` equivalence constructions.

## Source pin

The receipt fixtures and receipt profile exercised here are pinned to public
HALTSEAL commit:

`6e1e4c1fabf97cf057cc3299dafb09c2ffe182c3`

Each positive vector additionally pins the SHA-256 of its receipt fixture bytes,
so later fixture drift is detected rather than silently changing a known answer.

## Coverage

The vector set contains four positive known-answer tests across the published
ACCEPT, HOLD, and REFUSE receipt examples, plus four negative cases:

1. full compact JWS (`header.payload.signature`) used as the pre-image;
2. one LF octet appended to the correct JWS Signing Input;
3. `sha256:`-prefixed representation accepted in place of bare hex; and
4. uppercase hexadecimal accepted in place of lowercase hex.

`hs-cpb-id-fail-01-full-jws-boundary` is the primary discriminating vector for
the Artifact Type Registry: it pins HALTSEAL's signature-defined byte boundary
and prevents a full-JWS component selector from being treated as equivalent.

## Recompute

From the repository root:

```sh
python3 tools/public_resolve/verify_cpb_identifier_vectors.py
```

The verifier is standard-library only. It recomputes every positive digest from
the published receipt bytes, exercises every negative assertion, and exits
nonzero on any mismatch.
