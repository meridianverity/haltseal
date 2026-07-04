# GitHub upload checklist

Repository name recommendation:

```text
haltseal-gateway-proof-pack
```

Public repo description:

```text
Public-safe deterministic evaluation for permit-before-action AI-agent gateway control.
```

Before the public push or release asset upload:

```bash
python -m pip install -r requirements.txt
make all
HALTSEAL_STRICT_TREE=1 python tools/release_gate.py
python tools/package_release.py
```

Recommended tag:

```text
v0.3.1-proof-receipt
```

Recommended release title:

```text
HALTSEAL Gateway Proof Pack v0.3.1-proof-receipt — Public Evaluation Receipt Layer
```

Recommended release body:

```text
docs/GITHUB_RELEASE_BODY.md
```

Release positioning:

```text
v0.3.1-proof-receipt keeps the v0.3.0 public evaluation boundary intact and adds a portable proof receipt for security, legal, procurement, and written-scope diligence handoff.
```

Upload these release assets from `dist/`:

```text
haltseal-gateway-proof-pack-v0.3.1-proof-receipt.zip
haltseal-gateway-proof-pack-v0.3.1-proof-receipt.zip.sha256.txt
```

Optional supporting asset:

```text
MANIFEST.sha256.json
```

Do not describe this release as a production SDK, production attestation, certification, conformance program, legal opinion, commercial offer, field-of-use agreement, or patent-license grant.
