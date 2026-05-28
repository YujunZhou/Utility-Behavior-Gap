from pathlib import Path

import pytest

from utility_behavior_gap.constants import ACTORS
from utility_behavior_gap.openrouter import actor_env_name, judge_model_ids, require_openrouter_key
from utility_behavior_gap.pair_selection import select_pairs


def test_pair_selection_rebuilds_full_default_and_same_count_sets():
    rows = select_pairs(default_pairs_per_cell=2, same_count_pairs_per_cell=3)
    default = [row for row in rows if row["pair_set"] == "default"]
    same_count = [row for row in rows if row["pair_set"] == "same_count"]

    assert len(default) == len(ACTORS) * 4 * 2
    assert len(same_count) == len(ACTORS) * 3 * 3
    assert all(float(row["delta_u"]) > 0 for row in rows)
    assert {row["category"] for row in same_count} <= {row["category"] for row in rows if row["category"].startswith("count_")}


def test_env_example_keeps_public_values_as_placeholders():
    text = Path(".env.example").read_text(encoding="utf-8")

    assert "OPENROUTER_API_KEY=xxx" in text
    assert "JUDGE_MODELS=xxx,xxx,xxx" in text
    for actor in ACTORS:
        assert f"{actor_env_name(actor)}=xxx" in text


def test_live_api_requires_non_placeholder_key(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "xxx")

    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        require_openrouter_key()


def test_live_judging_requires_non_placeholder_models(monkeypatch):
    monkeypatch.setenv("JUDGE_MODELS", "xxx,xxx,xxx")

    with pytest.raises(RuntimeError, match="JUDGE_MODELS"):
        judge_model_ids()
