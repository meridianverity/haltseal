#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from haltseal_eval.canonicalization import write_json
from haltseal_eval.fixtures import all_vectors


def main() -> int:
    vectors = all_vectors()
    write_json(ROOT / "vectors" / "haltseal_gateway_vectors.json", vectors)
    write_json(ROOT / "vectors" / "expected_results.json", {v["vector_id"]: v["expected"] for v in vectors})
    examples_dir = ROOT / "examples"
    examples_dir.mkdir(exist_ok=True)
    for stale in examples_dir.glob("h*.json"):
        if re.match(r"^h\d{2}_", stale.stem):
            stale.unlink()
    for packet in vectors:
        write_json(examples_dir / f"{packet['vector_id'].lower()}.json", packet)
    print(f"vectors: regenerated {len(vectors)} public-eval packets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
