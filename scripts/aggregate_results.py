#!/usr/bin/env python3
"""Build all derived paper tables from the raw release data."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utility_behavior_gap.analysis import aggregate_all  # noqa: E402


def main() -> None:
    aggregate_all(ROOT)
    print(f"wrote derived tables under {ROOT / 'outputs'}")


if __name__ == "__main__":
    main()
