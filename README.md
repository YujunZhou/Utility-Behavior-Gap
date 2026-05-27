# Utility-Behavior Gap

This repository accompanies the paper and provides the code, prompt templates,
and data tables needed to reproduce the reported analyses. The experiments test
whether model-specific utility rankings predict downstream output quality when
high- and low-utility consequences are embedded into matched generation
prompts.

Scripts read the data in `data/` and write regenerated tables and figures to
`outputs/`. Figure 1 gives the high-level research question.

![Figure 1: Utility-behavior gap overview](figures/figure1.png)

## Method Overview

The main experiment compares paired outputs from the same actor model on the
same task item. The only experimental difference is the consequence attached to
success: one prompt uses a consequence that was high utility for that actor,
and the matched prompt uses a lower-utility consequence. Outputs are then
evaluated by blind pairwise quality judgment, with ties tracked separately.

Figure 2 summarizes the experimental pipeline used in the reported experiments.

![Figure 2: Experimental pipeline](figures/figure2.png)

## Reproduction Environment

Use Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Generated files are written under `outputs/`, which is ignored by git. The
tracked inputs are the CSV files under `data/`, the scripts under `scripts/`,
the prompt templates under `src/`, and the two overview figures used in this
README.

To rerun from a clean output directory:

```bash
rm -rf outputs
```

## Experiment Settings

The experiments use seven actor models:
DeepSeek V3.2, GPT-5.4 mini, GLM-5.1, Kimi K2.5, MiMo V2 Pro, Qwen3.5 9B, and
Qwen3.6 Plus.

The four output tasks are essay writing, grant-proposal abstracts, incident
postmortems, and Chinese-to-English translation. The main high-low analysis
uses the essay competition/no-opponent framing. Non-essay prompts use the
guard sentence:

> Do not mention the reward, donation, judging setup, or sponsoring organization
> in your output.

Reported win rates exclude ties unless the table explicitly says otherwise.
Confidence intervals are Wilson 95% intervals. The plotting scripts consume the
input tables in `data/processed/`; derived analysis scripts write their
results to `outputs/analysis/`.

## Reproduce Everything

Run the full check and regenerate all derived outputs:

```bash
python scripts/reproduce_all.py
```

The individual commands are listed below for targeted reruns.

Summary tables written by the full reproduction command:
`outputs/analysis/cue_summary.csv`,
`outputs/analysis/judging_tie_summary.csv`,
`outputs/analysis/utility_replication_holdout.csv`, and
`outputs/analysis/utility_replication_monotonicity.csv`.

## Main High-Low Utility Result

Input:
`data/processed/highlow_main_data.csv`

Command:

```bash
python scripts/plot_highlow_main.py
```

Output:
`outputs/figures/highlow_main.png` and
`outputs/figures/highlow_main.pdf`

This reproduces the actor-by-task high-utility-side win-rate plot for the main
behavioral test.

## Within-Count Check

Input:
`data/processed/highlow_within_count_data.csv`

Command:

```bash
python scripts/plot_highlow_within_count.py
```

Output:
`outputs/figures/highlow_within_count.png` and
`outputs/figures/highlow_within_count.pdf`

This check keeps the saved count fixed and varies only the entity or group in
the consequence.

## System-Prompt Calibration

Input:
`data/processed/system_prompt_calibration_data.csv`

Command:

```bash
python scripts/plot_sys_prompt_main.py
```

Output:
`outputs/figures/sys_prompt_main.png` and
`outputs/figures/sys_prompt_main.pdf`

This verifies that the same task and judging pipeline can detect large quality
changes when the prompt directly asks for stronger writing.

## Moral No-Label Cue Check

Input:
`data/processed/moral_nolabel_main_data.csv`

Command:

```bash
python scripts/plot_moral_nolabel_main.py
```

Output:
`outputs/figures/moral_nolabel_main.png` and
`outputs/figures/moral_nolabel_main.pdf`

This condition removes explicit moral labels while preserving the cause text.

## Larger-Amount Consequence Check

Input:
`data/processed/incentive_channel_data.csv`

Commands:

```bash
python scripts/plot_incentive_amount_main.py
python scripts/analyze_amount_pooled.py
```

Outputs:
`outputs/figures/incentive_amount_main.png`,
`outputs/figures/incentive_amount_main.pdf`,
`outputs/analysis/amount_condition_per_cell.csv`, and
`outputs/analysis/amount_condition_pooled_by_task.csv`

This condition compares a larger stated donation amount against a smaller one.

## Paper Summary Tables

Inputs:
`data/processed/*.csv` and
`data/analysis/utility_replication_diagnostics_2026-05-06.csv`

Command:

```bash
python scripts/summarize_paper_tables.py
```

Outputs:
`outputs/analysis/cue_summary.csv`,
`outputs/analysis/judging_tie_summary.csv`,
`outputs/analysis/utility_replication_holdout.csv`, and
`outputs/analysis/utility_replication_monotonicity.csv`

## Utility-Gap Dose Response

Input:
`data/analysis/utility_gap_dose_response_trials.csv`

Command:

```bash
python scripts/analyze_utility_gap_dose_response.py
```

Outputs:
`outputs/analysis/utility_gap_dose_response_bins.csv`,
`outputs/analysis/utility_gap_dose_response_regression.csv`,
`outputs/figures/utility_gap_dose_response.png`, and
`outputs/figures/utility_gap_dose_response.pdf`

The trial file contains 10,487 reported judged pairs.

## Additional Tables

Two appendix input tables are included directly:

- `data/analysis/utility_replication_diagnostics_2026-05-06.csv`
- `data/analysis/utility_top_bottom_10_by_actor_domain_2026-05-06.csv`

These tables are included as source data for appendix summaries and utility
example checks.

## Prompt Templates

Generation prompt templates are in
`src/utility_behavior_gap/prompts.py`. The prompt test checks that the
non-essay templates include the guard sentence and that all generation
templates include the prompt-encoded consequence. The same file also contains
the blind pairwise judge prompt template.

```bash
python -m pytest
```

## Scope

Included: reported high-low utility, within-count, system-prompt, moral
no-label, larger-amount, utility-fit diagnostic, utility-gap dose-response, and
top/bottom utility-example inputs. Generated intermediate outputs are written
to `outputs/` rather than tracked in the repository.
