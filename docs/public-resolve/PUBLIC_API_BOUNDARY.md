# Public API boundary

HALTSEAL Public Resolve Challenge exposes one narrow, synthetic payment-decision surface.

## In scope

- Server-issued fixed authority profiles.
- One complete final synthetic payment action.
- `ACCEPT`, `HOLD`, or `REFUSE`.
- At most one synthetic request record for an accepted authorized use.
- Transport idempotency distinct from economic-use consumption.
- Ed25519-signed evaluation receipts.
- Offline semantic replay.

## Structurally out of scope

- PAN, CVV, payment token, wallet secret, API credential, or merchant secret.
- User-supplied callback, destination URL, provider URL, or webhook.
- Live payment, network, issuer, PSP, acquirer, wallet, settlement, or reversal call.
- Arbitrary policy or arbitrary authority upload.
- Production use, certification, conformance status, partnership, or network compatibility.
- Patent, implementation, commercial, or field-of-use rights.

## Public output vocabulary

```text
ACCEPT · ONE_SYNTHETIC_REQUEST
HOLD   · NO_NEW_REQUEST
REFUSE · NO_REQUEST
```

`provider_request_id` is intentionally absent. No provider is called. The public coordinate is `synthetic_request_record_id`.
