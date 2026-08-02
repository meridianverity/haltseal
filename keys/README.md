# Evaluation verification keys

`sample-evaluation-jwks.json` verifies only the frozen sample receipts and local in-memory mock. The corresponding deterministic sample private key is intentionally public through the sample generator and **must never be used by the hosted service**.

The hosted service publishes its distinct live public keys at:

```text
https://eval.meridianverity.com/haltseal/evaluation/v1/jwks.json
```

Generate and protect the hosted private key outside the public repository. Snapshot the final hosted JWKS into the release record only after deployment and launch-gate verification.
