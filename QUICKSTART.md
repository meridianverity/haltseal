# HALTSEAL Public Resolve Challenge quickstart

## Local contract mock

```bash
python -m pip install -r requirements.txt
PYTHONPATH=. python -m haltseal_resolve.mock_server --host 127.0.0.1 --port 8787
```

```bash
bash examples/curl/run-local-challenge.sh
```

## Offline receipt verification

```bash
PYTHONPATH=. python -m haltseal_resolve.cli verify \
  examples/receipts/refuse-changed-terms.receipt.jws \
  --jwks keys/sample-evaluation-jwks.json
```

## Hosted evaluation

After the launch gate is complete, change the base URL to:

```text
https://eval.meridianverity.com/haltseal/evaluation/v1
```

Download the live JWKS from `/jwks.json`. Hosted keys are deliberately different from the public sample key.

## Verification parity and HTTP contract

```bash
PYTHONPATH=. python tools/public_resolve/run_verifier_parity.py
PYTHONPATH=. python tools/public_resolve/run_http_contract.py
```

The first command proves Python/TypeScript agreement across canonical and malformed signed receipts. The second starts the local HTTP mock and verifies `409`, `400`, and `503` `application/problem+json` behavior against the declared contract.
