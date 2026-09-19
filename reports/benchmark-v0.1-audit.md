# Benchmark v0.1 audit

- Status: frozen pilot manifest.
- Source: `SWE-bench/SWE-bench_Verified` revision `78f471bf655a3137b2e8a75af1501690ec009ec3`.
- Source parquet SHA-256: `030cfd7f2a704c4c0226e7f104c725a3b41230b1d3517f9c915ad7ea5be3fa25`.
- Tasks: 12; development: 6; holdout: 6.
- Repository overlap across splits: none.
- Source content committed here: task coordinates and one-way integrity hashes only.
- Source content intentionally excluded: issue text, gold patch, test patch, evaluation script and hints.

The task manifest passes `longhorizon validate-benchmark`. This validates manifest integrity, not runtime reproducibility; environment/image materialization is the next gated operation.
