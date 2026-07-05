# Commit plan

Recommended branch:

```bash
git checkout -b prep/haltseal-v0.3.2-hardened-eval
```

Recommended commits:

```text
release: add HALTSEAL v0.3.2 hardened public-eval packet
release: add proof receipt, transparency bundle, and Ed25519 proof profile
release: add independent recomputation and release artifact verification
release: align GitHub release body, upload checklist, manifest, and source tree
```

Recommended tag:

```bash
git tag -a v0.3.2-hardened-eval -m "HALTSEAL Gateway Proof Pack v0.3.2-hardened-eval"
```

Recommended final checks:

```bash
make qa-full
HALTSEAL_STRICT_TREE=1 python tools/release_gate.py
python tools/package_release.py
```
