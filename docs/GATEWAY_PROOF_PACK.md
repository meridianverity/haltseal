# Gateway Proof Pack

The proof pack answers one question:

> Can a reviewer run a narrow, deterministic, fail-closed gateway evaluation that binds one protected action to one short-lived permit and one evidence record?

The answer is yes.

## One protected action

```text
POST /external-tool/send-sensitive-payload
```

## One gateway

```text
network_egress_gateway
```

## One first HOLD condition

```text
Freshness or proof continuity cannot be established.
```

## One evidence bundle

Each decision emits an evidence-only IAL-style record containing the disposition, result code, action digest, permit identifier when present, signed-head identifier when present, implementation hook, audience tuple, evidence hash, and fixture signature.

## Why it is narrow

A narrow public artifact is easier to audit, easier to reproduce, and harder to misread as production software. Depth moves to written-scope diligence.
