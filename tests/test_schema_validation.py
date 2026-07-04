import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_public_packet_schema_validator_passes():
    proc = subprocess.run([sys.executable, "tools/validate_public_packet.py"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert proc.returncode == 0, proc.stdout
