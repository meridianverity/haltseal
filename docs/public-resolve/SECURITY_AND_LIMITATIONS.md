# Security and limitations

- The local mock is in-memory, single-process, and non-durable.
- The sample signing key is deterministic and public; it never signs hosted receipts.
- The hosted evaluation runtime is private and uses a separate protected key and durable store.
- Evaluation profiles are fixed. Arbitrary policies, URLs, credentials, callbacks, and provider endpoints are not accepted.
- Request bodies are small and closed-schema.
- Duplicate JSON members, floating-point numbers, non-finite numbers, unknown fields, wrong types, invalid UTF-8, and BOM-prefixed JSON fail closed.
- The public API is rate-limited and may change or suspend evaluation access.
- The API is not payment processing, a production authorization service, or a provider sandbox.
- Offline verification confirms a signed synthetic receipt and internal semantic coherence; it does not certify the hosted service, network, or a live effect.
