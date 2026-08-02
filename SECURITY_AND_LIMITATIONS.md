# Security and limitations

This repository is a public synthetic evaluation and verification surface, not a production security boundary.

The v0.4.0 receipt profile uses Ed25519 JWS and two independent offline verifier implementations. Both enforce a closed payload profile, strict types, exact decision/emission/consumption invariants, and canonical unpadded compact-JWS encoding. The historical v0.3.2 proof lineage separately contains deterministic synthetic fixture mechanisms.

Limitations:

- the public contract mock uses in-memory one-use and idempotency state;
- the hosted durable state, live signer, abuse controls, and operations remain private and are not established by this public source tree;
- no live payment provider, payment credential, callback URL, or user-supplied endpoint is accepted;
- no provider-side effect, production non-bypassability, network compatibility, certification, partnership, or production readiness is established;
- no commercial deployment right or patent license is granted.
