# TypeScript / Node offline verifier

```bash
node verifier/typescript/haltseal_verify.mjs \
  examples/receipts/accept-exact.receipt.jws \
  keys/sample-evaluation-jwks.json
```

The `.mjs` file is the dependency-free Node 22 executable. The `.ts` file preserves the same source for TypeScript-oriented review. It performs strict duplicate-member JSON parsing, Ed25519 JWS verification, action/authority digest recomputation, and bounded semantic replay. Hosted-service keys are distinct from the public sample key.

Both public verifiers enforce the same closed receipt profile and canonical, unpadded compact-JWS encoding. They reject signed receipts with wrong issuer/audience/profile/boundary values, invalid identifier or material types, inconsistent emission/consumption fields, non-canonical base64url, or semantic replay mismatch.
