# Hosted launch gates

Do not publish v0.4.0 as an active hosted challenge until the external deployment gates pass against the exact tagged commit, release ZIP SHA-256, and deployed endpoint.

## Buyer-independent local release gates

These gates are exercised by the public package and the separately controlled private-runtime candidate.

```text
Contract and schema validation                 PASS
Exact action → ACCEPT → one record             PASS
Material mutation → REFUSE → zero records      PASS
Unknown outcome → HOLD → zero new records      PASS
Same-key retry → same stored response          PASS
New-use attempt → REFUSE                       PASS
64-way concurrency → one record                PASS
Tampered receipt → offline verification FAIL   PASS
Full closed receipt profile                     PASS
Python/TypeScript verifier parity 20/20         PASS
Canonical unpadded compact JWS                   PASS
HTTP 409/400/503 problem contract 5/5           PASS
Duplicate/ambiguous JSON → request rejection   PASS
Credential-like input → schema rejection       PASS
Arbitrary URL/callback → schema rejection      PASS
Public provider-egress source scan             PASS
Private-runtime provider-egress source scan    PASS
Rate and body-size controls                     PASS
Historical v0.3.2 proof lineage                PASS
```

## External deployment gates

The following are external facts and remain pending until the hosted service is deployed and independently reviewed.

```text
Exact tagged Git commit recorded               PENDING
Hosted evaluation key generated in secret store PENDING
Live JWKS distinct from public sample key      PENDING
Durable state mounted and recovery checked     PENDING
Signer unavailable → service never ACCEPT      PENDING
State unavailable → service never ACCEPT       PENDING
Deployment-level deny-egress canary            PENDING
TLS, WAF, origin and quota policy               PENDING
Hosted endpoint health and HTTP smoke           PENDING
Fresh-download receipt verification             PENDING
Named reviewer exact-SHA disposition            PENDING
Website and status links                        PENDING
```

## Promotion rule

```text
Any external deployment gate PENDING or FAIL
→ do not describe the hosted API as active
→ keep the local contract mock and frozen samples public
```

The GitHub package may be prepared and reviewed before activation. The active hosted-service announcement must wait for a separately signed launch record.
