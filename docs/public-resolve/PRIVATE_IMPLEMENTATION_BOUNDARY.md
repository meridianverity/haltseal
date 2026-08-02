# Private implementation boundary

The public repository intentionally omits:

```text
hosted resolver source
atomic durable one-use implementation
signing private key and signer service
production policy resolver
provider request mapper
protected credentialed emitter
KMS/HSM integration
live provider status and reversal logic
buyer trust roots
commercial deployment topology
claim charts and target mappings
```

A separate private hosted-evaluation runtime may implement durable synthetic state and abuse controls, but still contains no provider adapter or provider credential. Real effect custody remains written-scope buyer diligence.
