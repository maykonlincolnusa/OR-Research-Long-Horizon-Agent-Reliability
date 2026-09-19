# Benchmark v0.1: frozen real-task pilot

`longhorizon-v0.1` is a 12-task feasibility benchmark based on the human-validated SWE-bench Verified test split. It is a platform-validation pilot, not a leaderboard and not a contamination-resistant measure of frontier-model ability.

## Provenance and license

The source is `SWE-bench/SWE-bench_Verified` revision `78f471bf655a3137b2e8a75af1501690ec009ec3`, pinned by the SHA-256 in [source.json](../data/benchmark-v0.1/source.json). The upstream SWE-bench project is MIT licensed. SWE-bench Verified provides 500 human-validated issue–PR pairs, source commits, test patches and evaluation metadata. [SWE-bench source](https://github.com/SWE-bench/SWE-bench) · [dataset card](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified)

## Selection

The fixed set has 6 development and 6 holdout tasks, one task per repository in each split, with no repository overlap. It spans difficulty labels from `<15 min fix` to `1-4 hours`, `FAIL_TO_PASS` counts of 1–10 and `PASS_TO_PASS` counts of 0–411. These are upstream labels/metadata, not claims about autonomous-agent difficulty.

Task cards retain only source coordinates and integrity hashes. They deliberately omit the issue statement, gold patch, test patch and evaluation script. At run time the materializer must fetch the source at the pinned revision, verify the parquet hash and expose only the issue statement plus base repository to the runner. The evaluator receives the test patch and reference metadata through a separate private path.

## Use policy

- Development outcomes may change operational reliability fixes, but must not tune prompts, memory policy, tool policy or model selection after a holdout run.
- Holdout outcomes are recorded once for the registered experiment. Any substantive adaptation creates `benchmark-v0.2` and a new holdout.
- Report source contamination as a limitation: these historical public tasks may have appeared in model training data.
- Record every materialized image digest. The source `image_reference` is a compatibility hint, not an immutable image digest.

Run `python -m longhorizon validate-benchmark` before scheduling an experiment.

After downloading the pinned source parquet, run `python -m longhorizon verify-benchmark-source --parquet <path>`. This re-computes hashes against the source without persisting solution-bearing fields in this repository.
