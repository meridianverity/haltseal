# Boundary mapper

The public mapper names the last reviewed synthetic hook before the protected action proceeds.

Enabled public-eval hook:

```text
network_egress_gateway
```

This is the only implementation hook enabled by the public evaluation package. The flagship vector uses this hook for the reviewed protected action:

```text
POST /external-tool/send-sensitive-payload
```

Any other hook string fails closed with `UNSUPPORTED_IMPLEMENTATION_HOOK` at stage `BOUNDARY_MAPPER`.

The public package does not enumerate or preview future hook names. In real diligence, the boundary mapper would identify the last enforceable hook for the requested action. That mapping is written-scope only.
