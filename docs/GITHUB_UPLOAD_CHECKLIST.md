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
make qa-full
HALTSEAL_STRICT_TREE=1 python tools/release_gate.py
python tools/package_release.py
```

Recommended tag:

```text
v0.3.2-hardened-eval
```

Recommended release title:

```text
HALTSEAL Gateway Proof Pack v0.3.2-hardened-eval — Public Gateway Proof Pack
```

Recommended release body:

```text
docs/GITHUB_RELEASE_BODY.md
```

Release positioning:

```text
v0.3.2-hardened-eval keeps the v0.3.0 public evaluation boundary intact and adds hardened reviewer-facing verification: proof receipt, transparency bundle, deterministic Ed25519 proof profile, independent recomputation, release-artifact verification, strict manifest/source-tree locking, and full QA preflight.
```

Upload these release assets from `dist/`:

```text
haltseal-gateway-proof-pack-v0.3.2-hardened-eval.zip
haltseal-gateway-proof-pack-v0.3.2-hardened-eval.zip.sha256.txt
```

Optional supporting asset:

```text
MANIFEST.sha256.json
```

Do not describe this release as a production SDK, production attestation, certification, conformance program, legal opinion, commercial offer, field-of-use agreement, IETF endorsement, formal standards-track output, or patent-license grant.
