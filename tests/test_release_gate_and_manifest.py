import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_gate_passes():
    proc = subprocess.run([sys.executable, "tools/release_gate.py"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert proc.returncode == 0, proc.stdout


def test_manifest_verifies_when_present():
    proc = subprocess.run([sys.executable, "verify_manifest.py"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert proc.returncode == 0, proc.stdout
