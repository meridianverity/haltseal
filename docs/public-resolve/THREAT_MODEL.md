# Public challenge threat model

Protected public claims:

1. The caller cannot define its own authority.
2. A material action mismatch cannot create a synthetic request record.
3. A single synthetic authorized use cannot create more than one record under concurrency or retry.
4. An uncertain prior outcome cannot authorize a blind new request.
5. Malformed, ambiguous, or credential-like input cannot reach decision semantics.
6. A receipt cannot pass offline verification after tampering.
7. Hosted service failure cannot fail open to `ACCEPT`.
8. The public runtime cannot contact a provider.

Not protected or claimed:

- live provider effects;
- production availability or non-bypassability;
- external KMS/HSM custody;
- network certification;
- fraud, AML, KYC, settlement, chargeback, or merchant fulfillment;
- independent validation before a named reviewer completes it.
