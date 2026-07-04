import ast
import json
from pathlib import Path

from haltseal_eval.constants import PUBLIC_EVAL_IMPLEMENTATION_HOOK, VERSION

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def count_tests() -> int:
    total = 0
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        total += sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
            for node in ast.walk(tree)
        )
    return total


def test_synthetic_evaluation_attestation_counts_are_current():
    vectors = load_json("vectors/haltseal_gateway_vectors.json")
    qa = load_json("QA_RESULTS.json")
    att = load_json("attestations/synthetic_evaluation_attestation.json")
    assert att["version"] == VERSION
    assert att["vector_count"] == len(vectors) == 32
    assert att["expected_pass_count"] == len(vectors)
    assert att["actual_pass_count"] == qa["passed"] == 32
    assert att["failed_count"] == qa["failed"] == 0
    assert att["test_count"] == count_tests()


def test_transparency_report_counts_match_qa_results():
    qa = load_json("QA_RESULTS.json")
    report = load_json("attestations/privacy_preserving_transparency_report.json")
    assert report["total_vectors"] == qa["total"] == 32
    assert report["passed_vectors"] == qa["passed"] == 32
    assert report["failed_vectors"] == qa["failed"] == 0


def test_boundary_mapper_doc_names_only_enabled_public_eval_hook():
    text = (ROOT / "docs" / "BOUNDARY_MAPPER.md").read_text(encoding="utf-8")
    assert PUBLIC_EVAL_IMPLEMENTATION_HOOK in text
    assert "only implementation hook enabled" in text
    assert "device_io_gateway" not in text
    assert "dispatch_gateway" not in text
    assert "actuation_gateway" not in text
