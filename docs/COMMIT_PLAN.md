# Commit plan

Recommended branch:

```bash
git checkout -b prep/haltseal-v0.3.1-proof-receipt
```

Recommended commits:

```text
release: add HALTSEAL v0.3.1 proof receipt layer
release: add portable proof receipt artifacts and verifier
release: align GitHub release body and upload checklist
release: refresh manifest, source tree, and release gates
```

Recommended tag:

```bash
git tag -a v0.3.1-proof-receipt -m "HALTSEAL Gateway Proof Pack v0.3.1-proof-receipt"
```

Recommended final checks:

```bash
make all
HALTSEAL_STRICT_TREE=1 python tools/release_gate.py
python tools/package_release.py
```
