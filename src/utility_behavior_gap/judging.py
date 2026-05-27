"""Judge-panel counting rules for the released pairwise comparisons."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping


LEGACY_ESSAY_HIGHLOW_RUNS = {"bg_fixed_topic_default", "bg_fixed_topic_same_count"}
CALIBRATION_COMPARISONS = {"system_prompt", "moral_nolabel", "amount"}


def derive_panel_winner_condition(row: Mapping[str, str], vote_conditions: Iterable[str]) -> str:
    """Derive a panel winner from sanitized individual vote conditions.

    Older essay high-low runs represented a three-way X/Y/TIE split as a
    non-counted disagreement. Later scale-up runs treated the same split as a
    panel tie. The release keeps this source-specific rule explicit so the
    counted winner can be checked from `judge_votes.csv`.
    """

    valid = [value for value in vote_conditions if value and value != "unresolved"]
    if not valid:
        return "unresolved"

    counts = Counter(valid)
    top_count = max(counts.values())
    top = [condition for condition, count in counts.items() if count == top_count]
    if len(top) == 1:
        return top[0]

    if row.get("source_run") in LEGACY_ESSAY_HIGHLOW_RUNS:
        return "unresolved"
    return "tie"


def derive_counted_winner_condition(row: Mapping[str, str], vote_conditions: Iterable[str]) -> str:
    """Return the winner condition used by the paper's win-rate denominators."""

    panel = derive_panel_winner_condition(row, vote_conditions)
    comparison = row.get("comparison", "")
    predicted = row.get("predicted_condition", "")
    other = row.get("other_condition", "")

    if comparison in {"highlow_main", "highlow_same_count"}:
        if row.get("source_run") in LEGACY_ESSAY_HIGHLOW_RUNS:
            return panel if panel in {"high", "low"} else ""
        return panel if panel in {"high", "low", "tie"} else ""

    if comparison in CALIBRATION_COMPARISONS:
        return panel if panel in {predicted, other, "tie"} else "tie"

    return panel if panel in {predicted, other, "tie"} else ""
