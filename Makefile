PYTHON ?= python
export PYTHONDONTWRITEBYTECODE=1

.PHONY: regenerate eval validate transparency attestation receipt manifest test release-gate zip-audit package all clean clean-caches clean-bytecode

regenerate:
	$(PYTHON) tools/regenerate_vectors.py

eval:
	$(PYTHON) tools/run_public_eval.py

validate:
	$(PYTHON) tools/validate_public_packet.py

transparency:
	$(PYTHON) tools/generate_transparency_report.py

attestation:
	$(PYTHON) tools/generate_attestation.py

receipt:
	$(PYTHON) tools/export_proof_receipt.py
	$(PYTHON) tools/verify_proof_receipt.py

manifest:
	$(PYTHON) tools/make_manifest.py
	$(PYTHON) verify_manifest.py

test:
	$(PYTHON) -m pytest -q

release-gate:
	$(PYTHON) tools/release_gate.py

zip-audit: clean-caches
	$(PYTHON) tools/zip_audit.py

package: clean-caches regenerate eval validate transparency attestation receipt manifest test release-gate zip-audit
	$(PYTHON) tools/package_release.py

all: clean-caches regenerate eval validate transparency attestation receipt manifest test release-gate zip-audit

clean-caches:
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache \) -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete

clean-bytecode: clean-caches

clean: clean-caches
	rm -f QA_RESULTS.json MANIFEST.json MANIFEST.sha256.json
	rm -rf dist build *.egg-info
