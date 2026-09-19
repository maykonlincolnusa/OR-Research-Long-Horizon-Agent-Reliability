from __future__ import annotations

import argparse

from .analysis import write_summary
from .dashboard import write_dashboard
from .harness import run_experiment
from .dataset import load_tasks
from .integrity import validate_tasks
from .quality import check_files, write_check
from .report import write_report
from .data_engineering import build_warehouse, validate_artifacts
from .benchmark import validate_benchmark_files, verify_source_artifact


def main() -> None:
    parser = argparse.ArgumentParser(description="Local-first long-horizon reliability research harness")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="run deterministic local fixtures")
    run.add_argument("--config", required=True)
    analyze = commands.add_parser("analyze", help="aggregate run records")
    analyze.add_argument("--results", required=True)
    analyze.add_argument("--output", required=True)
    dashboard = commands.add_parser("dashboard", help="create static HTML report")
    dashboard.add_argument("--summary", required=True)
    dashboard.add_argument("--output", required=True)
    validate = commands.add_parser("validate", help="validate a benchmark dataset")
    validate.add_argument("--dataset", required=True)
    check = commands.add_parser("check", help="enforce evidence-quality gates")
    check.add_argument("--summary", required=True)
    check.add_argument("--gates", required=True)
    check.add_argument("--output", required=True)
    report = commands.add_parser("report", help="write a public experiment report")
    report.add_argument("--summary", required=True)
    report.add_argument("--quality", required=True)
    report.add_argument("--manifest", required=True)
    report.add_argument("--output", required=True)
    data_validate = commands.add_parser("validate-data", help="validate normalized run and event artifacts")
    data_validate.add_argument("--runs", required=True)
    data_validate.add_argument("--events", required=True)
    warehouse = commands.add_parser("warehouse", help="build the local SQLite experiment warehouse")
    warehouse.add_argument("--runs", required=True)
    warehouse.add_argument("--events", required=True)
    warehouse.add_argument("--summary", required=True)
    warehouse.add_argument("--manifest", required=True)
    warehouse.add_argument("--database", required=True)
    benchmark = commands.add_parser("validate-benchmark", help="validate frozen benchmark task cards and split policy")
    benchmark.add_argument("--tasks", default="data/benchmark-v0.1/tasks.jsonl")
    benchmark.add_argument("--splits", default="data/benchmark-v0.1/splits.json")
    benchmark.add_argument("--source", default="data/benchmark-v0.1/source.json")
    verify_source = commands.add_parser("verify-benchmark-source", help="verify task cards against a pinned source parquet")
    verify_source.add_argument("--tasks", default="data/benchmark-v0.1/tasks.jsonl")
    verify_source.add_argument("--source", default="data/benchmark-v0.1/source.json")
    verify_source.add_argument("--parquet", required=True)
    args = parser.parse_args()
    if args.command == "run":
        output, count = run_experiment(args.config)
        print(f"Wrote {count} runs to {output}")
    elif args.command == "analyze":
        print(f"Wrote summary to {write_summary(args.results, args.output)}")
    elif args.command == "dashboard":
        print(f"Wrote dashboard to {write_dashboard(args.summary, args.output)}")
    elif args.command == "validate":
        errors = validate_tasks(load_tasks(args.dataset))
        if errors:
            parser.error("Invalid benchmark:\n" + "\n".join(errors))
        print(f"Benchmark valid: {args.dataset}")
    elif args.command == "check":
        result = check_files(args.summary, args.gates)
        print(f"Wrote quality check to {write_check(result, args.output)}")
        if not result["passed"]:
            raise SystemExit(1)
    else:
        if args.command == "validate-benchmark":
            print(f"Benchmark valid: {validate_benchmark_files(args.tasks, args.splits, args.source)} tasks")
            return
        if args.command == "verify-benchmark-source":
            print(f"Benchmark source verified: {verify_source_artifact(args.tasks, args.source, args.parquet)} tasks")
            return
        if args.command == "validate-data":
            runs, events = validate_artifacts(args.runs, args.events)
            print(f"Normalized artifacts valid: {len(runs)} runs, {len(events)} events")
            return
        if args.command == "warehouse":
            database, experiment_id = build_warehouse(args.runs, args.events, args.summary, args.manifest, args.database)
            print(f"Built warehouse {database} for experiment {experiment_id}")
            return
        print(f"Wrote report to {write_report(args.summary, args.quality, args.manifest, args.output)}")


if __name__ == "__main__":
    main()
