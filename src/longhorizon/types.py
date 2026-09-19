from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Task:
    id: str
    repository: str
    prompt: str
    horizon: int
    expected_tools: list[str]
    acceptance: str
    inject_transient_failure: bool = False
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Treatment:
    model: str
    topology: str
    memory: str
    strategy: str
    context: str

    @property
    def key(self) -> str:
        return "|".join((self.model, self.topology, self.memory, self.strategy, self.context))


@dataclass
class RunRecord:
    run_id: str
    task_id: str
    treatment: dict[str, str]
    seed: int
    task_success: bool
    hallucinations: int
    tool_calls: int
    accurate_tool_calls: int
    input_tokens: int
    output_tokens: int
    latency_ms: int
    estimated_cost_usd: float
    failure_injected: bool
    recovered_after_failure: bool | None
    events: list[dict[str, Any]]

    @property
    def tool_call_accuracy(self) -> float:
        return self.accurate_tool_calls / self.tool_calls if self.tool_calls else 0.0

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["tool_call_accuracy"] = round(self.tool_call_accuracy, 6)
        return result
