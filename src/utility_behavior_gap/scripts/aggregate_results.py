#!/usr/bin/env python3
"""Build all derived paper tables from the raw release data."""

from __future__ import annotations

from utility_behavior_gap.analysis import aggregate_all
from utility_behavior_gap.paths import ROOT


def main() -> None:
    aggregate_all(ROOT)
    print(f"wrote derived tables under {ROOT / 'outputs'}")


if __name__ == "__main__":
    main()
