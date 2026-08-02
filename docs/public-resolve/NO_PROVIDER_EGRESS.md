# No provider egress

The public challenge runtime must have no route to a payment provider.

Required deployment posture:

```text
user-supplied URL fields          absent from schema
provider SDKs                     absent
payment credentials               rejected
outbound network policy           deny by default
ACCEPT side effect                one local synthetic ledger append only
```

The private deployment reference includes a Kubernetes `NetworkPolicy` denying all egress. A reverse proxy, DNS policy, and cloud firewall should independently preserve the same boundary.
