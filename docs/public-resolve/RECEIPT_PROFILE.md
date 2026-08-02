# Evaluation receipt profile

Receipts are canonical, unpadded compact Ed25519 JWS objects with exact protected headers. Each segment must match `^[A-Za-z0-9_-]+$`; padding, standard-base64 `+` or `/`, whitespace, invalid lengths, and non-canonical pad bits are rejected:

```json
{"alg":"EdDSA","kid":"...","typ":"HALTSEAL-EVAL-RECEIPT+jws"}
```

The signed payload binds:

- issuer and audience;
- receipt and challenge identifiers;
- profile version;
- complete synthetic authority and authority digest;
- complete final action and action digest;
- bounded decision and ordered reason codes;
- synthetic emission disposition and request counts;
- authority consumption transition; and
- the non-production public boundary.

The Python and TypeScript offline verifiers enforce the same complete profile: signature validity; exact issuer, audience, profile and boundary; exact field sets; strict action and authority types; identifier and digest grammar; unique ordered reason codes; action/authority digest recomputation; and exact ACCEPT/HOLD/REFUSE emission and consumption invariants. A signed receipt that is structurally valid but semantically inconsistent is rejected.

A receipt proves a signed synthetic evaluation result. It does not prove a live payment, a provider-side effect, production non-bypassability, or external certification.

## Decision-specific invariants

```text
ACCEPT
  ONE_SYNTHETIC_REQUEST · RECORDED
  new_request_count = 1
  total_request_count_for_use = 1
  existing_request_record_id = null
  AVAILABLE → CONSUMED

HOLD
  NO_NEW_REQUEST · UNKNOWN
  new_request_count = 0
  total_request_count_for_use = 1
  existing_request_record_id is required
  CONSUMED → CONSUMED

REFUSE
  NO_REQUEST · NONE
  new_request_count = 0
  no request identifiers
  consumption state does not change
```
