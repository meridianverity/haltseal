# Start here

```bash
python -m pip install -r requirements.txt
PYTHONPATH=. python -m pytest tests_public_resolve
PYTHONPATH=. python -m haltseal_resolve.mock_server
```

Then run `bash examples/curl/run-local-challenge.sh` and verify the returned receipt offline.

**Boundary:** fixed synthetic payment profiles only; no credentials; no live provider call; no production or patent rights.
