# Registered pilot protocol v0.1

## Scope

This is a feasibility and instrumentation study on `longhorizon-v0.1`. It establishes whether the platform can materialize real tasks, isolate runs, collect complete evidence and recover from controlled failures. It does not support a general performance claim or a model leaderboard.

## Hypotheses

- H1: bounded memory will increase recovery after injected transient tool failure relative to no memory.
- H2: planner-executor will improve tool-call accuracy relative to ReAct under the same model, context strategy and tool policy.
- H3: summary context will reduce input-token usage relative to full context, with a possible task-success tradeoff.

## Treatment design

The first confirmatory study is a balanced factorial design with fixed model aliases `M1` and `M2`, memory `{none,bounded}`, planning `{react,planner-executor}` and context `{full,summary}`. Agent topology remains `single-agent`; multi-agent topology is a separate study because it changes orchestration and budget semantics. Every cell uses identical task snapshots, tool allowlists, system prompt version, time budget and seed schedule.

The v0.1 pilot runs only the development split to validate materialization. Holdout is locked until the design, model aliases, decoding parameters and budget are committed in a tagged protocol revision. The confirmatory sample-size decision must be documented before holdout execution; the 12-task pilot is not powered for interaction effects.

## Outcomes and analysis

Primary outcome: objective task success from the evaluator. Secondary outcomes: tool-call accuracy, hallucinations/run, input/output tokens, wall-clock latency, cost and recovery after injected failures. Report a 95% bootstrap interval by task and seed. For the confirmatory analysis, fit a mixed-effects or cluster-robust model with task as the clustering unit; do not treat repeated events from one run as independent observations.

## Exclusions and failures

Exclude only a task whose pinned environment cannot be materialized before the run begins; preserve the failed materialization artifact and report it. Do not silently retry a completed agent run. Infrastructure retries create a new attempt ID; agent retries follow the fixed treatment policy and count against budget.

## Reproducibility record

Persist benchmark/source hashes, repository commit, image digest, evaluator version, agent/container image digest, model alias/version, decoding parameters, prompt/tool-policy hashes, budgets, patch, test output, event stream and final verdict. Publish only redacted/approved artifacts.
