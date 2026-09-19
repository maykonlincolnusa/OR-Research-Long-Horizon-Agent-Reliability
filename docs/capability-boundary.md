# Capability boundary

## What this project can establish today

- The complete data path from a benchmark task to logs, evaluator output, aggregate statistics, dashboard and public report.
- Reproducibility of fixture runs through deterministic seeds, hashes and a manifest.
- Detection of incomplete experiment evidence through quality gates.

## What it cannot establish today

- That GPT, Codex, an open model, memory system or multi-agent design is more reliable. Fixture profiles are synthetic by design.
- Generalization to production software repositories; the seed benchmark contains only toy tasks.
- Causal effects: current treatments change several factors at once and are a smoke test, not a factorial study.

## Capability requirements for the next empirical phase

1. A frozen task split from real repositories, each with an isolated evaluator and license record.
2. One change per treatment comparison, paired on task and seed.
3. A local/open-model adapter or an approved hosted-model adapter, with model version and decoding settings logged.
4. A sandboxed workspace per run, command allowlist and captured test output.
5. Preregistered hypotheses, repetition count and exclusion rules.

The research harness is ready for those integrations; no conclusion should outrun these boundaries.
