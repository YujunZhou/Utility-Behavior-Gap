#!/usr/bin/env python3
"""Validate consistency of released judged pairs and judge votes."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from utility_behavior_gap.analysis import read_rows, write_rows
from utility_behavior_gap.judging import derive_counted_winner_condition
from utility_behavior_gap.paths import ANALYSIS, ROOT


def load_votes(path: Path) -> dict[str, list[str]]:
    by_pair: dict[str, list[str]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["success"] != "true":
                raise ValueError(f"non-success judge vote for {row['pair_uid']}")
            by_pair[row["pair_uid"]].append(row["winner_condition"])
    return by_pair


def main() -> None:
    judged = read_rows(ROOT / "data" / "raw" / "judged_pairs.csv")
    votes_by_pair = load_votes(ROOT / "data" / "raw" / "judge_votes.csv")

    missing_votes = [row["pair_uid"] for row in judged if row["pair_uid"] not in votes_by_pair]
    if missing_votes:
        raise ValueError(f"missing judge votes for {len(missing_votes)} judged pairs")

    vote_count_errors = [
        (pair_uid, len(votes))
        for pair_uid, votes in votes_by_pair.items()
        if len(votes) != 3
    ]
    if vote_count_errors:
        raise ValueError(f"expected exactly three votes per pair; found {vote_count_errors[:5]}")

    mismatches = []
    summary: Counter[tuple[str, str, str]] = Counter()
    for row in judged:
        pair_uid = row["pair_uid"]
        derived = derive_counted_winner_condition(row, votes_by_pair[pair_uid])
        released = row["counted_winner_condition"]
        summary[(row["comparison"], row["panel_winner_condition"], released)] += 1
        if derived != released:
            mismatches.append(
                {
                    "pair_uid": pair_uid,
                    "comparison": row["comparison"],
                    "source_run": row["source_run"],
                    "released_counted_winner": released,
                    "derived_counted_winner": derived,
                    "votes": ";".join(votes_by_pair[pair_uid]),
                }
            )

    if mismatches:
        write_rows(ANALYSIS / "judge_vote_validation_mismatches.csv", mismatches)
        raise ValueError(f"counted winner mismatches: {len(mismatches)}")

    rows = [
        {
            "comparison": comparison,
            "panel_winner_condition": panel,
            "counted_winner_condition": counted,
            "n_pairs": n_pairs,
        }
        for (comparison, panel, counted), n_pairs in sorted(summary.items())
    ]
    write_rows(ANALYSIS / "judge_vote_validation_summary.csv", rows)
    print(f"validated {len(judged)} judged pairs and {sum(len(v) for v in votes_by_pair.values())} judge votes")
    print(f"wrote {ANALYSIS / 'judge_vote_validation_summary.csv'}")


if __name__ == "__main__":
    main()
