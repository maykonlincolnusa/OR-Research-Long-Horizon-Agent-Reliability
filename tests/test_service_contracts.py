import unittest
from pathlib import Path

import yaml

from services.common.contracts import ExperimentRequest, RunEvent
from services.runner.worker import RunJob, validate_job


ROOT = Path(__file__).resolve().parents[1]


class ServiceContractTests(unittest.TestCase):
    def test_experiment_and_event_contracts_are_valid(self):
        request = ExperimentRequest.model_validate({
            "experiment_id": "research-001", "benchmark_version": "seed-v1", "treatments": [{"model": "local"}],
            "repetitions": 1, "seed": 1,
            "budget": {"max_tokens": 100, "max_cost_usd": 1, "max_wall_time_seconds": 60},
        })
        event = RunEvent.model_validate({
            "source": "longhorizon.runner", "type": "run.started", "subject": "run-1",
            "data": {"experiment_id": request.experiment_id, "task_id": "task-1", "sequence": 0},
        })
        self.assertEqual(event.specversion, "1.0")

    def test_compose_declares_production_service_boundaries(self):
        compose = yaml.safe_load((ROOT / "deploy/docker-compose.yml").read_text(encoding="utf-8"))
        expected = {"control-plane", "outbox-relay", "telemetry", "evaluator", "model-gateway", "nats", "minio"}
        self.assertTrue(expected.issubset(compose["services"]))

    def test_runner_rejects_non_artifact_input(self):
        job = RunJob("experiment", "run", "https://unsafe.example/task", {}, 10, 1, 30)
        with self.assertRaises(ValueError):
            validate_job(job)


if __name__ == "__main__":
    unittest.main()
