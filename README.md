# Utility-Behavior Gap

This repository contains the reproducibility artifact for the paper's reported
utility-behavior gap analyses. It starts from releasable experimental inputs:
outcome utility data, selected high-low pairs, task items, moral cause pairs,
panel-level judged comparisons, and individual judge votes. The scripts
regenerate the processed tables, appendix diagnostics, and figures used in the
paper.

No live model access or model calls are required. Raw generated model
outputs and judge free-text rationales are not included; the released judged
records contain the condition metadata and parsed judge decisions needed to
reproduce the reported statistics.

![Figure 1: Utility-behavior gap overview](figures/figure1.png)

![Figure 2: Experimental pipeline](figures/figure2.png)

## Setup

Use Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Generated files are written under `outputs/`, which is created on demand and
ignored by git. The repository does not store generated intermediate or final
analysis outputs.

## Data Layout

Raw releasable inputs:

- `data/raw/utility_options.csv`: fitted utility values for each actor,
  outcome domain, and option.
- `data/raw/utility_pairwise_choices.csv`: compact pairwise utility-choice
  counts used for the fitted utility stage.
- `data/raw/selected_pairs.csv`: sampled high-utility and low-utility outcome
  pairs used in the behavior experiments.
- `data/raw/task_items.csv`: essay topics and non-essay task items.
- `data/raw/moral_cause_pairs.csv`: paired good-cause and harmful-cause texts
  used in the no-label moral cue check.
- `data/raw/judged_pairs.csv`: one row per judged pair, including the raw panel
  winner and the winner used by the paper's counting rule.
- `data/raw/judge_votes.csv`: individual parsed judge votes for each judged
  pair.

Metadata:

- `data/metadata/actors.csv`
- `data/metadata/domains.csv`
- `data/metadata/tasks.csv`

Derived outputs are regenerated into:

- `outputs/processed/*.csv`
- `outputs/analysis/*.csv`
- `outputs/figures/*.{png,pdf}`

## Reproduce Everything

```bash
python scripts/reproduce_all.py
```

This runs tests, builds derived tables from `data/raw`, regenerates figures,
and writes paper-summary tables.

## Per-Result Commands

Build all derived CSVs:

```bash
python scripts/aggregate_results.py
```

Main high-low utility result:

```bash
python scripts/plot_highlow_main.py
```

Inputs: `outputs/processed/highlow_main_data.csv`

Outputs: `outputs/figures/highlow_main.png`,
`outputs/figures/highlow_main.pdf`

Within-count check:

```bash
python scripts/plot_highlow_within_count.py
```

Inputs: `outputs/processed/highlow_within_count_data.csv`

Outputs: `outputs/figures/highlow_within_count.png`,
`outputs/figures/highlow_within_count.pdf`

System-prompt calibration:

```bash
python scripts/plot_sys_prompt_main.py
```

Inputs: `outputs/processed/system_prompt_calibration_data.csv`

Outputs: `outputs/figures/sys_prompt_main.png`,
`outputs/figures/sys_prompt_main.pdf`

Moral no-label cue check:

```bash
python scripts/plot_moral_nolabel_main.py
```

Inputs: `outputs/processed/moral_nolabel_main_data.csv`

Outputs: `outputs/figures/moral_nolabel_main.png`,
`outputs/figures/moral_nolabel_main.pdf`

Larger-amount consequence check:

```bash
python scripts/plot_incentive_amount_main.py
python scripts/analyze_amount_pooled.py
```

Inputs: `outputs/processed/incentive_channel_data.csv`

Outputs: `outputs/figures/incentive_amount_main.png`,
`outputs/figures/incentive_amount_main.pdf`,
`outputs/analysis/amount_condition_per_cell.csv`, and
`outputs/analysis/amount_condition_pooled_by_task.csv`

Paper summary tables:

```bash
python scripts/summarize_paper_tables.py
```

Outputs: `outputs/analysis/cue_summary.csv`,
`outputs/analysis/judging_tie_summary.csv`,
`outputs/analysis/utility_replication_holdout.csv`, and
`outputs/analysis/utility_replication_monotonicity.csv`

Utility-gap dose response:

```bash
python scripts/analyze_utility_gap_dose_response.py
```

Inputs: `outputs/analysis/utility_gap_dose_response_trials.csv`

Outputs: `outputs/analysis/utility_gap_dose_response_bins.csv`,
`outputs/analysis/utility_gap_dose_response_regression.csv`,
`outputs/figures/utility_gap_dose_response.png`, and
`outputs/figures/utility_gap_dose_response.pdf`

The regenerated trial table contains 10,487 reported high-low judged pairs,
including 10,230 non-tied pairs.

## Prompt Templates

Prompt templates for the reported generation and judging conditions are in
`src/utility_behavior_gap/prompts.py`. Task-item prompt strings used in the
released non-essay records are also included in `data/raw/task_items.csv`.

## Scope

Included: reported high-low utility, same-count high-low, system-prompt
calibration, moral no-label cue check, larger-amount consequence check,
utility-fit diagnostics, utility-gap dose-response, and top/bottom utility
examples.

Excluded: live API calling code, raw model-response dumps, run caches, logs,
private notes, exploratory runs, and generated intermediate artifacts.
