# KPI framework

KPIs are separated into **evidence quality** and **agent outcomes**. Passing an evidence gate means the run is interpretable; it does not mean an agent is reliable.

| Dimension | KPI | Definition | Initial gate | Real-study target |
| --- | --- | --- | --- | --- |
| Coverage | runs | Total `(task, treatment, seed)` records | ≥ 60 | power analysis driven |
| Balance | runs/group | Minimum observations per treatment | ≥ 15 | equal paired seeds/tasks |
| Completeness | required metrics | Every group includes all outcome fields | 100% | 100% |
| Integrity | dataset/config hash | Manifest binds inputs to output | required | required |
| Reliability | task success | Objective evaluator success rate | descriptive | preregistered |
| Tool use | tool-call accuracy | Correct calls / all calls | descriptive | report by task class |
| Safety | hallucinations/run | Invalid/unjustified action count | descriptive | lower is better |
| Resilience | recovery rate | Recovered failures / injected failures | descriptive | report denominator |
| Efficiency | tokens, latency, cost | Mean per run | descriptive | Pareto frontier |

The initial gates in `configs/quality-gates.local.json` deliberately check **observability**, not performance. Do not set an empirical success threshold until a real benchmark, evaluator and sample-size plan are frozen.
