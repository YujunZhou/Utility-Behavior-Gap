"""Repository paths shared by the reproduction entry points."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"
PROCESSED = OUTPUTS / "processed"
ANALYSIS = OUTPUTS / "analysis"
FIGURES = OUTPUTS / "figures"
