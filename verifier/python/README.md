# Python offline verifier

```bash
PYTHONPATH=. python verifier/python/haltseal_verify.py verify \
  examples/receipts/accept-exact.receipt.jws \
  --jwks keys/sample-evaluation-jwks.json
```

The verifier accepts only a compact JWS and an explicitly supplied JWKS file. It performs no network request.

Both public verifiers enforce the same closed receipt profile and canonical, unpadded compact-JWS encoding. They reject signed receipts with wrong issuer/audience/profile/boundary values, invalid identifier or material types, inconsistent emission/consumption fields, non-canonical base64url, or semantic replay mismatch.
