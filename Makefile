PYTHON ?= python
export PYTHONDONTWRITEBYTECODE=1

.PHONY: regenerate eval validate transparency attestation receipt ed25519 independent manifest test release-gate strict-release-gate zip-audit release-verify package all qa-full clean clean-caches clean-bytecode

regenerate:
	$(PYTHON) tools/regenerate_vectors.py

eval:
	$(PYTHON) tools/run_public_eval.py

validate:
	$(PYTHON) tools/validate_public_packet.py

transparency:
	$(PYTHON) tools/generate_transparency_report.py
	$(PYTHON) tools/generate_transparency_bundle.py
	$(PYTHON) tools/verify_transparency_bundle.py

attestation:
	$(PYTHON) tools/generate_attestation.py

receipt:
	$(PYTHON) tools/export_proof_receipt.py
	$(PYTHON) tools/verify_proof_receipt.py

ed25519:
	$(PYTHON) tools/generate_ed25519_profile.py
	$(PYTHON) tools/verify_ed25519_profile.py

independent:
	$(PYTHON) tools/independent_recompute.py

manifest:
	$(PYTHON) tools/make_manifest.py
	$(PYTHON) verify_manifest.py

release-verify:
	$(PYTHON) tools/verify_release_artifact.py --tree .

test:
	PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $(PYTHON) -m pytest -vv -s

release-gate:
	$(PYTHON) tools/release_gate.py

strict-release-gate:
	HALTSEAL_STRICT_TREE=1 $(PYTHON) tools/release_gate.py

zip-audit: clean-caches
	$(PYTHON) tools/zip_audit.py

qa-full: clean-caches regenerate eval validate transparency attestation receipt ed25519 independent manifest test release-gate strict-release-gate release-verify zip-audit

package: clean-caches regenerate eval validate transparency attestation receipt ed25519 independent manifest test release-gate strict-release-gate release-verify zip-audit
	$(PYTHON) tools/package_release.py

all: qa-full

clean-caches:
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache \) -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete
	rm -rf *.egg-info build

clean-bytecode: clean-caches

clean: clean-caches
	rm -f QA_RESULTS.json MANIFEST.json MANIFEST.sha256.json
	rm -rf dist build *.egg-info
