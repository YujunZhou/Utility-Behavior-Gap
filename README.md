# Utility-Behavior Gap

This repository contains the reproducibility artifact for the paper's main
utility-behavior gap analyses and releaseable appendix diagnostics. It starts
from releasable experimental inputs: outcome utility data, selected high-low
pairs, task items, moral cause pairs, panel-level judged comparisons, and
individual judge votes. The scripts regenerate the processed tables,
diagnostics, and figures listed below.

No live model access or model calls are required. Raw generated model outputs,
judge free-text rationales, run caches, logs, and private notes are not
included; the released judged records contain the condition metadata and parsed
judge decisions needed to reproduce the listed statistics.

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

Generated files are written under `outputs/`, which is created on demand and
ignored by git. The repository does not store generated intermediate or final
analysis outputs.

## Data Layout

Raw releasable inputs:

- `data/raw/utility_options.csv`: fitted utility values for each actor,
  outcome domain, and option. These fixed scores are the utility inputs used
  by this paper's behavior experiments. They were produced with the Utility
  Engineering utility-analysis pipeline
  ([code](https://github.com/centerforaisafety/emergent-values/tree/main/utility_analysis),
  [paper](https://arxiv.org/abs/2502.08640)); this release uses them as
  upstream reproducibility inputs rather than re-running live utility
  elicitation.
- `data/raw/utility_pairwise_choices.csv`: compact pairwise utility-choice
  counts used for the fitted utility stage. Included for inspection of the
  upstream utility-engineering inputs; the release scripts start from the
  fitted scores in `utility_options.csv`.
- `data/raw/selected_pairs.csv`: sampled high-utility and low-utility outcome
  pairs used in the behavior experiments. Included as a transparency record of
  the sampled contrasts.
- `data/raw/task_items.csv`: essay topics and non-essay task items.
  Essay rows store the topic in `item_id` / `item_label`; non-essay rows also
  include the full task prompt in `base_prompt`.
- `data/raw/moral_cause_pairs.csv`: paired good-cause and harmful-cause texts
  used in the no-label moral cue check. Included as a transparency record of
  the curated cause pairs.
- `data/raw/judged_pairs.csv`: one row per judged pair, including the raw panel
  winner and the winner used by the paper's counting rule.
- `data/raw/judge_votes.csv`: individual parsed judge votes for each judged
  pair. The validation script checks that these votes reproduce the counted
  winner used by `judged_pairs.csv`.

Metadata:

- `data/metadata/actors.csv`
- `data/metadata/domains.csv`
- `data/metadata/tasks.csv`

Source code:

- `src/utility_behavior_gap/analysis.py`: aggregates raw release inputs into
  derived paper tables.
- `src/utility_behavior_gap/stats.py`: statistical helpers used by the
  aggregation and diagnostics.
- `src/utility_behavior_gap/prompts.py`: prompt templates for the reported
  generation and judging conditions.
- `src/utility_behavior_gap/scripts/`: command-line entry points for full and
  per-result reproduction.

Derived outputs are regenerated into:

- `outputs/processed/*.csv`
- `outputs/analysis/*.csv`
- `outputs/figures/*.{png,pdf}`

## Reproduce Release Results

```bash
python -m utility_behavior_gap.scripts.reproduce_all
```

This runs tests, builds derived tables from `data/raw`, validates judged-pair
counting, regenerates release figures, and writes paper-summary tables. The
release covers the paper's main high-low utility result, same-count control,
system-prompt calibration, moral no-label cue check, larger-amount consequence
check, utility-fit diagnostics, utility-gap dose response, top/bottom utility
examples, and aggregate judging tie counts.

## Per-Result Commands

Build all derived CSVs:

```bash
python -m utility_behavior_gap.scripts.aggregate_results
```

Validate judged-pair inputs:

```bash
python -m utility_behavior_gap.scripts.validate_release_inputs
```

Inputs: `data/raw/judged_pairs.csv`, `data/raw/judge_votes.csv`

Outputs: `outputs/analysis/judge_vote_validation_summary.csv`

Main high-low utility result:

```bash
python -m utility_behavior_gap.scripts.plot_highlow_main
```

Inputs: `outputs/processed/highlow_main_data.csv`

Outputs: `outputs/figures/highlow_main.png`,
`outputs/figures/highlow_main.pdf`

Within-count check:

```bash
python -m utility_behavior_gap.scripts.plot_highlow_within_count
```

Inputs: `outputs/processed/highlow_within_count_data.csv`

Outputs: `outputs/figures/highlow_within_count.png`,
`outputs/figures/highlow_within_count.pdf`

System-prompt calibration:

```bash
python -m utility_behavior_gap.scripts.plot_sys_prompt_main
```

Inputs: `outputs/processed/system_prompt_calibration_data.csv`

Outputs: `outputs/figures/sys_prompt_main.png`,
`outputs/figures/sys_prompt_main.pdf`

Moral no-label cue check:

```bash
python -m utility_behavior_gap.scripts.plot_moral_nolabel_main
```

Inputs: `outputs/processed/moral_nolabel_main_data.csv`

Outputs: `outputs/figures/moral_nolabel_main.png`,
`outputs/figures/moral_nolabel_main.pdf`

Larger-amount consequence check:

```bash
python -m utility_behavior_gap.scripts.plot_incentive_amount_main
python -m utility_behavior_gap.scripts.analyze_amount_pooled
```

Inputs: `outputs/processed/incentive_channel_data.csv`

Outputs: `outputs/figures/incentive_amount_main.png`,
`outputs/figures/incentive_amount_main.pdf`,
`outputs/analysis/amount_condition_per_cell.csv`, and
`outputs/analysis/amount_condition_pooled_by_task.csv`

Paper summary tables:

```bash
python -m utility_behavior_gap.scripts.summarize_paper_tables
```

Outputs: `outputs/analysis/cue_summary.csv`,
`outputs/analysis/judging_tie_summary.csv`,
`outputs/analysis/utility_replication_holdout.csv`, and
`outputs/analysis/utility_replication_monotonicity.csv`

Utility-gap dose response:

```bash
python -m utility_behavior_gap.scripts.analyze_utility_gap_dose_response
```

Inputs: `outputs/analysis/utility_gap_dose_response_trials.csv`

Outputs: `outputs/analysis/utility_gap_dose_response_bins.csv`,
`outputs/analysis/utility_gap_dose_response_regression.csv`,
`outputs/figures/utility_gap_dose_response.png`, and
`outputs/figures/utility_gap_dose_response.pdf`

The regenerated trial table contains 10,487 reported high-low judged pairs,
including 10,230 non-tied pairs.

Utility top/bottom examples:

```bash
python -m utility_behavior_gap.scripts.plot_utility_top_bottom
```

Inputs: `outputs/analysis/utility_top_bottom_10_by_actor_domain.csv`

Outputs: `outputs/figures/utility_top_bottom_examples.png`,
`outputs/figures/utility_top_bottom_examples.pdf`

## Counting Rule

`judged_pairs.csv` stores both `panel_winner_condition` and
`counted_winner_condition`. The latter is the condition used for all win-rate
denominators. Tied panel decisions are excluded from non-tied denominators
unless the paper reports ties explicitly.

The historical essay high-low runs (`bg_fixed_topic_default` and
`bg_fixed_topic_same_count`) used an older judge-panel export in which panel
ties or three-way judge disagreements are not counted; these rows have an empty
`counted_winner_condition`. Later high-low scale-up runs count panel ties as
`tie`. Calibration comparisons (`system_prompt`, `moral_nolabel`, and
`amount`) map unresolved or tied panel outcomes to `tie`, which is reported but
excluded from the non-tied win-rate denominator. The implementation of this
rule is in `src/utility_behavior_gap/judging.py`, and
`python -m utility_behavior_gap.scripts.validate_release_inputs` verifies the
released `counted_winner_condition` values from `judge_votes.csv`.

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
private notes, exploratory runs, generated intermediate artifacts, and
re-running the upstream Utility Engineering utility elicitation stage. The
appendix's explicit moral-label diagnostic is not part of the release data; the
release includes the moral no-label cue check used in the main text. Additional
supporting task checks outside the main four-task generation grid are summarized
in the paper but are not part of this artifact.

## Anonymous Release Notes

The repository is intended to be published from tracked files only. Generated
directories such as `outputs/`, virtual environments, Python caches, local
configuration directories, and any existing local `.git` metadata should not be
included in archival zip files unless they are intentionally regenerated by the
reviewer.
