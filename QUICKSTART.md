# Quickstart

```bash
python -m pip install -r requirements.txt
python tools/run_public_eval.py
python tools/validate_public_packet.py
python -m pytest -q
```

No network services, private keys, cloud accounts, or external datasets are required.

The evaluation uses deterministic synthetic fixtures. Embedded demo keys are public fixture material and provide reproducibility only.
