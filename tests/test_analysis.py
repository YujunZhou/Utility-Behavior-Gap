import pytest

from utility_behavior_gap.analysis import comparison_counts
from utility_behavior_gap.stats import parse_entity_count, spearman, wilson_ci


def test_comparison_counts_uses_counted_winner_only():
    rows = [
        {"counted_winner_condition": "high"},
        {"counted_winner_condition": "low"},
        {"counted_winner_condition": "tie"},
        {"counted_winner_condition": ""},
    ]

    assert comparison_counts(rows, "high", "low") == (1, 1, 1)


def test_wilson_ci_has_expected_shape():
    rate, lo, hi = wilson_ci(5, 10)

    assert rate == 0.5
    assert 0.2 < lo < rate
    assert rate < hi < 0.8


def test_parse_entity_count_and_spearman():
    assert parse_entity_count(
        "100 people who identify as Buddhist are saved from terminal illness.",
        "religions",
    ) == ("buddhist", 100)

    assert spearman([1, 2, 3], [10, 20, 30]) == pytest.approx(1.0)
