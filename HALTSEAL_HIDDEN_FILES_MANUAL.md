# HALTSEAL v0.3.1 hidden-files manual restore overlay

This overlay contains no hidden filenames. Use it when a manual upload path strips `.gitignore` or `.github/`.

## One-command restore

Place these visible overlay files in the repository root, then run:

```bash
python HALTSEAL_HIDDEN_FILES_RESTORE.py --force --cleanup
python verify_manifest.py
python -m pytest -q
python tools/release_gate.py
```

The restore helper writes exactly these four hidden targets and verifies their SHA-256 hashes:

- `.gitignore` — `2200de0e4fef993523606dbe5aa38248c61bffdd3cb57692b8c72959d8f2886d` (76 bytes)
- `.github/workflows/public-eval.yml` — `bedd3fc966be51462ead548c4e523cf84f1fe65111b7f93214aef3464c9c3e70` (1171 bytes)
- `.github/pull_request_template.md` — `e2c1ee3860e523004ffd52eb91debed7a00851c2a27c2416990bbf5d820bd6e4` (430 bytes)
- `.github/ISSUE_TEMPLATE/boundary_question.md` — `a8d3dd9cb9382867112796b474afb4ec701f3bfc00f9849d8464eaaa380bc6aa` (323 bytes)

## Manual copy fallback

If no terminal is available, create each target path manually in the repository UI and paste the corresponding content below. After that, do not keep these overlay files in the final release tree.

### `.gitignore`

SHA-256: `2200de0e4fef993523606dbe5aa38248c61bffdd3cb57692b8c72959d8f2886d`  
Size: `76` bytes

```
__pycache__/
*.pyc
.pytest_cache/
.venv/
dist/
build/
*.egg-info/
.DS_Store
```

### `.github/workflows/public-eval.yml`

SHA-256: `bedd3fc966be51462ead548c4e523cf84f1fe65111b7f93214aef3464c9c3e70`  
Size: `1171` bytes

```
name: HALTSEAL public evaluation

on:
  push:
  pull_request:

jobs:
  public-eval:
    runs-on: ubuntu-latest
    env:
      PYTHONDONTWRITEBYTECODE: "1"
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install test dependency
        run: python -m pip install -r requirements.txt
      - name: Regenerate deterministic vectors
        run: python tools/regenerate_vectors.py
      - name: Run public evaluation
        run: python tools/run_public_eval.py
      - name: Validate packet boundary
        run: python tools/validate_public_packet.py
      - name: Generate transparency report
        run: python tools/generate_transparency_report.py
      - name: Generate synthetic evaluation attestation
        run: python tools/generate_attestation.py
      - name: Check manifest
        run: python tools/make_manifest.py && python verify_manifest.py
      - name: Run tests
        run: python -m pytest -q
      - name: Release gate
        run: python tools/release_gate.py
      - name: Zip hygiene audit
        run: make clean-caches && python tools/zip_audit.py
```

### `.github/pull_request_template.md`

SHA-256: `e2c1ee3860e523004ffd52eb91debed7a00851c2a27c2416990bbf5d820bd6e4`  
Size: `430` bytes

```
# Public-eval pull request

## Scope

- [ ] Synthetic evaluation only
- [ ] No implementation-depth material
- [ ] No private legal mapping
- [ ] No target-specific analysis
- [ ] No commercial terms
- [ ] No patent-license terms

## Checks

```bash
python tools/run_public_eval.py
python tools/validate_public_packet.py
python tools/make_manifest.py
python verify_manifest.py
python -m pytest -q
python tools/release_gate.py
```
```

### `.github/ISSUE_TEMPLATE/boundary_question.md`

SHA-256: `a8d3dd9cb9382867112796b474afb4ec701f3bfc00f9849d8464eaaa380bc6aa`  
Size: `323` bytes

```
---
name: Boundary question
about: Ask about the synthetic public evaluation boundary
labels: boundary, public-eval
---

## Question

## File or vector

## Why it matters for public review

Please do not include secrets, confidential deployment details, private legal mapping, target-specific analysis, or licensing terms.
```

## Source artifact

- Source ZIP: `haltseal-main-v0.3.1-verified-hidden-files-complete(1).zip`
- Source ZIP SHA-256: `3f2cb8fdea32fa2d7516494b2cd7e0467d8a5fa92baa92d28fca7f92af970412`

## Important cleanup rule

These visible helper files are a transfer kit, not part of the final HALTSEAL release tree. After the hidden files are restored, run the helper with `--cleanup` or delete:

- `HALTSEAL_HIDDEN_FILES_RESTORE.py`
- `HALTSEAL_HIDDEN_FILES_MANUAL.md`
- `HALTSEAL_HIDDEN_FILES_RESTORE_MANIFEST.json`
- `HALTSEAL_HIDDEN_FILES_SHA256SUMS.txt`
