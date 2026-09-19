# Data architecture

The project uses a local, rebuildable three-layer design. It deliberately starts with JSONL and SQLite, which keeps the research environment portable and auditable without a cloud account or a distributed-data stack.

| Layer | Location | Contract | Purpose |
| --- | --- | --- | --- |
| Raw | `data/benchmarks/` and externally captured artifacts | preserve source provenance | tasks and source evidence |
| Normalized | `results/runs.jsonl`, `results/events.jsonl` | `schemas/*.schema.json` + runtime validation | one run/event per line |
| Curated | `results/warehouse.sqlite` | foreign keys and indexed tables | reproducible SQL analysis |

## Data contracts and validation

`run-record.schema.json` defines the unit of analysis: task × treatment × seed. `event.schema.json` defines the audit trail. `longhorizon validate-data` enforces required fields, treatment dimensions, nonnegative metrics, unique run IDs, event/run referential integrity, contiguous event sequences and sensitive-payload-key detection.

The logger redacts sensitive fields before writing. The data validator is a second line of defense; a failed validation stops warehouse construction.

## Lineage

The experiment manifest binds the config and benchmark hashes to every warehouse experiment ID. The warehouse never relies on a mutable filename as identity. Rebuild it with:

```powershell
$env:PYTHONPATH = "src"
py -m longhorizon validate-data --runs results/runs.jsonl --events results/events.jsonl
py -m longhorizon warehouse --runs results/runs.jsonl --events results/events.jsonl --summary results/summary.json --manifest results/manifest.json --database results/warehouse.sqlite
```

## Warehouse model

- `experiments`: provenance and manifest snapshot.
- `runs`: one measured agent attempt.
- `events`: ordered run trace, keyed by `(experiment_id, run_id, sequence)`.
- `treatment_kpis`: curated aggregate used by reports/dashboard.

For real runs, preserve raw artifacts in an access-controlled location, normalize only reviewed/redacted fields and publish only curated aggregates plus approved evidence samples.
