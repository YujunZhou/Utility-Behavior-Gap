#!/usr/bin/env python3
"""Run the full analysis reproduction pipeline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "-m", "pytest"],
    [sys.executable, "scripts/plot_highlow_main.py"],
    [sys.executable, "scripts/plot_highlow_within_count.py"],
    [sys.executable, "scripts/plot_sys_prompt_main.py"],
    [sys.executable, "scripts/plot_moral_nolabel_main.py"],
    [sys.executable, "scripts/plot_incentive_amount_main.py"],
    [sys.executable, "scripts/summarize_paper_tables.py"],
    [sys.executable, "scripts/analyze_utility_gap_dose_response.py"],
    [sys.executable, "scripts/analyze_amount_pooled.py"],
]


def main() -> None:
    for command in COMMANDS:
        print("$ " + " ".join(command), flush=True)
        subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
