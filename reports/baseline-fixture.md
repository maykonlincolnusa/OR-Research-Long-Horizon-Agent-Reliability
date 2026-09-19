# Baseline experiment report

**This is a fixture simulation, not empirical model evidence.**

## Evidence integrity: PASS

| Check | Observed | Expected | Status |
| --- | --- | --- | --- |
| minimum_runs | 60 | 60 | pass |
| minimum_groups | 4 | 4 | pass |
| runs_per_group | [15, 15, 15, 15] | 15 | pass |
| required_metrics | [] | [] | pass |
| simulation_state | True | True | pass |

## KPI snapshot

| Treatment | n | Success | Tool accuracy | Hallucinations/run | Recovery | Tokens | Latency ms | Cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixture-gpt-like / single-agent / bounded / planner-executor / summary | 15 | 0.9333 | 0.8511 | 0.1333 | 1.0 | 1745 | 25752.33 | 0.01396 |
| fixture-gpt-like / single-agent / none / react / full | 15 | 0.3333 | 0.7267 | 0.5333 | 0.1 | 1906 | 28032.8 | 0.015248 |
| fixture-open-small / multi-agent / bounded / planner-executor / summary | 15 | 0.7333 | 0.7189 | 0.7333 | 0.8 | 1736.33 | 13981.07 | 0.001736 |
| fixture-open-small / single-agent / none / react / sliding | 15 | 0.2667 | 0.66 | 0.8667 | 0.5 | 1573.33 | 12692 | 0.001573 |

## Provenance

- Harness: `0.1.0`
- Dataset SHA-256: `083070526d166a389efba1bb5409ec9afcd25007a4a0b48491a9b7455f1a691e`
- Config SHA-256: `8aa6f17935d984ea84d559a7b6546020b2cd9d1d6cbdeafbf7552c7dfd00529a`
- Runs: `60`
- Runtime: Python `3.14.5` on `Windows-10-10.0.19045-SP0`

Interpretation is intentionally withheld: the treatments are not factorially isolated and fixture profiles are synthetic. This report establishes observability and a reproducible baseline only.
