import json
import tempfile
import unittest
from pathlib import Path

from longhorizon.analysis import analyze
from longhorizon.dataset import load_tasks
from longhorizon.fixture_agent import execute_fixture
from longhorizon.logging import sanitize
from longhorizon.evaluator import evaluate_fixture
from longhorizon.integrity import build_manifest, validate_tasks
from longhorizon.quality import assess_quality
from longhorizon.types import Treatment

ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def test_seed_dataset_loads(self):
        self.assertEqual(len(load_tasks(ROOT / "data/benchmarks/seed_tasks.jsonl")), 3)

    def test_fixture_is_deterministic(self):
        task = load_tasks(ROOT / "data/benchmarks/seed_tasks.jsonl")[0]
        treatment = Treatment("fixture-gpt-like", "single-agent", "bounded", "planner-executor", "summary")
        self.assertEqual(execute_fixture(task, treatment, 12, 0).to_dict(), execute_fixture(task, treatment, 12, 0).to_dict())

    def test_analysis_marks_fixture_as_simulated(self):
        task = load_tasks(ROOT / "data/benchmarks/seed_tasks.jsonl")[0]
        record = execute_fixture(task, Treatment("fixture-gpt-like", "single-agent", "none", "react", "full"), 7, 0).to_dict()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runs.jsonl"
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            self.assertTrue(analyze(path)["simulated"])

    def test_logs_redact_sensitive_values(self):
        self.assertEqual(sanitize({"token": "nope", "name": "safe"}), {"token": "[REDACTED]", "name": "safe"})

    def test_fixture_evaluator_has_acceptance_contract(self):
        task = load_tasks(ROOT / "data/benchmarks/seed_tasks.jsonl")[0]
        record = execute_fixture(task, Treatment("fixture-gpt-like", "single-agent", "none", "react", "full"), 7, 0)
        self.assertEqual(evaluate_fixture(task, record).acceptance, task.acceptance)

    def test_seed_benchmark_passes_integrity_checks(self):
        tasks = load_tasks(ROOT / "data/benchmarks/seed_tasks.jsonl")
        self.assertEqual(validate_tasks(tasks), [])
        manifest = build_manifest(ROOT / "configs/experiment.local.json", ROOT / "data/benchmarks/seed_tasks.jsonl", tasks)
        self.assertEqual(manifest["dataset"]["task_count"], 3)
        self.assertEqual(len(manifest["dataset"]["sha256"]), 64)

    def test_quality_gates_reject_underpowered_summary(self):
        gates = {"minimum_runs": 2, "minimum_groups": 1, "minimum_runs_per_group": 2, "required_metrics": ["task_success_rate"], "expect_simulated": True}
        summary = {"runs": 1, "simulated": True, "groups": [{"n": 1, "task_success_rate": 1.0}]}
        self.assertFalse(assess_quality(summary, gates)["passed"])


if __name__ == "__main__":
    unittest.main()
