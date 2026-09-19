from __future__ import annotations

import hashlib
import random

from .types import RunRecord, Task, Treatment

PROFILE = {
    "fixture-gpt-like": {"base": 0.83, "tool": 0.92, "cost_per_1k": 0.008, "latency": 145},
    "fixture-open-small": {"base": 0.68, "tool": 0.80, "cost_per_1k": 0.001, "latency": 78},
}


def _rng(seed: int, task_id: str, treatment: Treatment) -> random.Random:
    material = f"{seed}:{task_id}:{treatment.key}".encode()
    return random.Random(int.from_bytes(hashlib.sha256(material).digest()[:8], "big"))


def _success_probability(task: Task, treatment: Treatment) -> float:
    if treatment.model not in PROFILE:
        raise ValueError(f"Unsupported local model profile: {treatment.model}")
    score = PROFILE[treatment.model]["base"] - max(0, task.horizon - 6) * 0.018
    score += 0.075 if treatment.memory == "bounded" else 0
    score += 0.055 if treatment.strategy == "planner-executor" else 0
    score += 0.025 if treatment.topology == "multi-agent" else 0
    score += 0.025 if treatment.context == "summary" and task.horizon >= 9 else 0
    score -= 0.020 if treatment.context == "sliding" else 0
    return min(0.98, max(0.05, score))


def execute_fixture(task: Task, treatment: Treatment, seed: int, repetition: int) -> RunRecord:
    """Deterministic simulator for validating the pipeline, never empirical evidence."""
    rng, profile = _rng(seed + repetition, task.id, treatment), PROFILE[treatment.model]
    expected, events = list(task.expected_tools), []
    accurate = calls = 0
    if treatment.strategy == "planner-executor":
        events.append({"kind": "plan", "steps": expected})
    if treatment.memory == "bounded":
        events.append({"kind": "memory", "policy": treatment.context, "budget_tokens": 800})
    if treatment.topology == "multi-agent":
        events.append({"kind": "handoff", "from": "planner", "to": "executor"})
    tool_probability = profile["tool"] + (0.035 if treatment.strategy == "planner-executor" else 0)
    failure_seen = False
    for index, tool in enumerate(expected):
        calls += 1
        if task.inject_transient_failure and index == len(expected) // 2:
            failure_seen = True
            events.append({"kind": "tool", "name": tool, "outcome": "transient_failure"})
            recovery = 0.32 + (0.42 if treatment.memory == "bounded" else 0) + (0.12 if treatment.strategy == "planner-executor" else 0)
            if rng.random() < recovery:
                calls += 1
                accurate += 1
                events.append({"kind": "tool", "name": tool, "outcome": "recovered_retry"})
            else:
                events.append({"kind": "recovery", "outcome": "abandoned"})
        elif rng.random() < tool_probability:
            accurate += 1
            events.append({"kind": "tool", "name": tool, "outcome": "ok"})
        else:
            events.append({"kind": "tool", "name": f"invalid:{tool}", "outcome": "invalid"})
    hallucinations = sum(event.get("outcome") == "invalid" for event in events)
    recovered = any(event.get("outcome") == "recovered_retry" for event in events)
    probability = _success_probability(task, treatment)
    if failure_seen and not recovered:
        probability *= 0.20
    if accurate < len(expected) - 1:
        probability *= 0.35
    success = rng.random() < probability
    input_tokens = 260 + task.horizon * 90 + (190 if treatment.memory == "bounded" else 0)
    input_tokens += task.horizon * 35 if treatment.context == "full" else -task.horizon * 12 if treatment.context == "summary" else 0
    output_tokens = 110 + calls * 65 + (80 if treatment.strategy == "planner-executor" else 0)
    latency = int((input_tokens + output_tokens) * profile["latency"] / 10 + calls * 90)
    return RunRecord(
        run_id=f"{task.id}-{treatment.key}-{seed}-{repetition}", task_id=task.id,
        treatment={"model": treatment.model, "topology": treatment.topology, "memory": treatment.memory, "strategy": treatment.strategy, "context": treatment.context},
        seed=seed + repetition, task_success=success, hallucinations=int(hallucinations), tool_calls=calls, accurate_tool_calls=accurate,
        input_tokens=input_tokens, output_tokens=output_tokens, latency_ms=latency,
        estimated_cost_usd=round((input_tokens + output_tokens) / 1000 * profile["cost_per_1k"], 6),
        failure_injected=failure_seen, recovered_after_failure=recovered if failure_seen else None, events=events,
    )
