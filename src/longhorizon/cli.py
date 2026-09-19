from __future__ import annotations

import argparse

from .analysis import write_summary
from .dashboard import write_dashboard
from .harness import run_experiment
from .dataset import load_tasks
from .integrity import validate_tasks


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
    args = parser.parse_args()
    if args.command == "run":
        output, count = run_experiment(args.config)
        print(f"Wrote {count} runs to {output}")
    elif args.command == "analyze":
        print(f"Wrote summary to {write_summary(args.results, args.output)}")
    elif args.command == "dashboard":
        print(f"Wrote dashboard to {write_dashboard(args.summary, args.output)}")
    else:
        errors = validate_tasks(load_tasks(args.dataset))
        if errors:
            parser.error("Invalid benchmark:\n" + "\n".join(errors))
        print(f"Benchmark valid: {args.dataset}")


if __name__ == "__main__":
    main()
