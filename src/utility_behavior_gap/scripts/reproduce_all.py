#!/usr/bin/env python3
"""Run the full analysis reproduction pipeline."""

from __future__ import annotations

import subprocess
import sys

from utility_behavior_gap.paths import ROOT

COMMANDS = [
    [sys.executable, "-m", "pytest"],
    [sys.executable, "-m", "utility_behavior_gap.scripts.aggregate_results"],
    [sys.executable, "-m", "utility_behavior_gap.scripts.validate_release_inputs"],
    [sys.executable, "-m", "utility_behavior_gap.scripts.plot_highlow_main"],
    [sys.executable, "-m", "utility_behavior_gap.scripts.plot_highlow_within_count"],
    [sys.executable, "-m", "utility_behavior_gap.scripts.plot_sys_prompt_main"],
    [sys.executable, "-m", "utility_behavior_gap.scripts.plot_moral_nolabel_main"],
    [sys.executable, "-m", "utility_behavior_gap.scripts.plot_incentive_amount_main"],
    [sys.executable, "-m", "utility_behavior_gap.scripts.plot_utility_top_bottom"],
    [sys.executable, "-m", "utility_behavior_gap.scripts.summarize_paper_tables"],
    [sys.executable, "-m", "utility_behavior_gap.scripts.analyze_utility_gap_dose_response"],
    [sys.executable, "-m", "utility_behavior_gap.scripts.analyze_amount_pooled"],
]


def main() -> None:
    for command in COMMANDS:
        print("$ " + " ".join(command), flush=True)
        subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
