# Idempotency and replay

## Transport retry

An identical request using the same `Idempotency-Key` returns the stored response. The service sets:

```text
X-HALTSEAL-Idempotent-Replayed: true
```

No additional synthetic request record is created.

## New economic-use attempt

After an authority's single use is consumed, a new `Idempotency-Key` does not create a second use. The result is:

```text
REFUSE
AUTHORIZED_USE_ALREADY_CONSUMED
NO_REQUEST
```

## Idempotency-key conflict

Reusing one `Idempotency-Key` with a different challenge/action request is a protocol error and returns HTTP 409. It is not converted into an `ACCEPT`, `HOLD`, or `REFUSE` receipt.
