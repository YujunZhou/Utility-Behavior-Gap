# Utility-Behavior Gap

This repository contains the public reproduction code for the paper's
utility-behavior gap experiments. It is designed to rerun the behavioral
generation and blind pairwise judging stages through OpenRouter, then rebuild
the paper tables and figures from the newly generated local outputs.

The upstream utility fitting stage is the one exception: the fitted per-actor,
per-outcome utility scores are included as fixed inputs in
`data/inputs/utility_options.csv`. They were produced with the Utility
Engineering pipeline
([code](https://github.com/centerforaisafety/%65mergent-values/tree/main/utility_analysis),
[paper](https://arxiv.org/abs/2502.08640)); this artifact starts from those
scores and reruns the paper's behavioral experiments.

![Figure 1: Utility-behavior gap overview](figures/figure1.png)

![Figure 2: Experimental pipeline](figures/figure2.png)

## Setup

Use Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e . --no-deps
```

Copy the OpenRouter configuration template and replace every `xxx` value with
your local credentials and model ids:

```bash
cp .env.example .env
```

The repository never tracks `.env`, API keys, generated model outputs, judged
records, processed tables, or final figures. All generated files go under
`outputs/`, which is ignored by git.

## Data Layout

Tracked reproduction inputs:

- `data/inputs/utility_options.csv`: fixed fitted utility score for each paper
  actor alias, outcome domain, and outcome option.
- `data/inputs/task_items.csv`: essay topics and non-essay task items used for
  generation.
- `data/inputs/moral_cause_pairs.csv`: frozen good-cause / harmful-cause pairs
  used in the no-label moral cue check.
- `data/metadata/*.csv`: human-readable labels and ordering.
- `figures/figure1.png` and `figures/figure2.png`: static README illustrations.

Generated local outputs:

- `outputs/inputs/selected_pairs.csv`: high-utility and low-utility outcome
  pairs rebuilt from `utility_options.csv`.
- `outputs/api/generation_jobs.jsonl`: prompt jobs for actor generation.
- `outputs/api/generations.jsonl`: local actor outputs returned by OpenRouter.
- `outputs/api/judge_votes.jsonl`: local individual judge votes returned by
  OpenRouter.
- `outputs/raw/judged_pairs.csv` and `outputs/raw/judge_votes.csv`: parsed
  pair-level and vote-level records used by the analysis scripts.
- `outputs/processed/*.csv`, `outputs/analysis/*.csv`, and
  `outputs/figures/*`: regenerated tables, diagnostics, and plots.

No processed or intermediate CSVs are tracked, except for the fixed upstream
utility scores.

## Quick Smoke Test

This checks the pipeline shape without making API calls:

```bash
python -m utility_behavior_gap.scripts.reproduce_all --dry-run --smoke
```

For package sanity checks:

```bash
python -m pytest
```

## Full Reproduction

After filling `.env`, run:

```bash
python -m utility_behavior_gap.scripts.reproduce_all
```

This command:

1. Rebuilds high-low and same-count outcome pairs from fixed utility scores.
2. Builds actor-generation jobs for the reported high-low, same-count,
   system-prompt, moral no-label, and larger-amount comparisons.
3. Calls OpenRouter for actor generations.
4. Calls OpenRouter for the blind judge panel.
5. Aggregates votes into judged pair records.
6. Rebuilds paper tables, diagnostics, and optional figures.

Live API outputs can differ slightly across time, model versions, and sampling
settings. The code fixes the prompt construction, pair selection, parsing, and
aggregation rules so reviewers can rerun the same analysis pipeline.

To skip figure rendering after the API run:

```bash
python -m utility_behavior_gap.scripts.reproduce_all --no-plots
```

## Per-Step Commands

Rebuild utility-derived outcome pairs:

```bash
python -m utility_behavior_gap.scripts.select_pairs
```

Prepare generation jobs:

```bash
python -m utility_behavior_gap.scripts.prepare_generation_jobs \
  --comparisons highlow_main,highlow_same_count,system_prompt,moral_nolabel,amount
```

Run actor generations:

```bash
python -m utility_behavior_gap.scripts.run_generation
```

Run blind pairwise judging:

```bash
python -m utility_behavior_gap.scripts.run_judging
```

Aggregate live judge votes:

```bash
python -m utility_behavior_gap.scripts.aggregate_judgments
```

Build derived tables:

```bash
python -m utility_behavior_gap.scripts.aggregate_results
python -m utility_behavior_gap.scripts.summarize_paper_tables
python -m utility_behavior_gap.scripts.analyze_amount_pooled
python -m utility_behavior_gap.scripts.analyze_utility_gap_dose_response
```

Render figures:

```bash
python -m utility_behavior_gap.scripts.plot_highlow_main
python -m utility_behavior_gap.scripts.plot_highlow_within_count
python -m utility_behavior_gap.scripts.plot_sys_prompt_main
python -m utility_behavior_gap.scripts.plot_moral_nolabel_main
python -m utility_behavior_gap.scripts.plot_incentive_amount_main
python -m utility_behavior_gap.scripts.plot_utility_top_bottom
```

## Sampling Defaults

`select_pairs` samples 80 high-low pairs per actor-domain from the top and
bottom thirds of the fitted utility ranking, with replacement. Same-count pairs
use the same rule within each count group for the religion, animal, and country
domains.

`prepare_generation_jobs` uses the full task pool by default. High-low jobs
cycle task items across sampled pairs. System-prompt and larger-amount checks
default to five repeats per item. The no-label moral check defaults to five
cause-pair samples per item, rotating through the frozen cause set.

Use `--items-per-task`, `--pairs-per-actor-domain`, `--system-repeats`,
`--amount-repeats`, and `--moral-causes-per-item` to run smaller checks.

## Scope

Included: OpenRouter-based behavioral generation, OpenRouter-based blind
pairwise judging, pair selection from fitted utilities, prompt construction,
vote parsing, panel aggregation, paper summary tables, diagnostics, and plotting
scripts.

Excluded: re-running the upstream utility fitting stage, private run caches,
old exploratory experiments, private notes, logs, API key files, and generated
intermediate/final outputs.
