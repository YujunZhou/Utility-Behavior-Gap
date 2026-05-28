#!/usr/bin/env python3
"""Aggregate live judge votes into pair-level judged records."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

from utility_behavior_gap.io_utils import read_jsonl, write_csv_rows
from utility_behavior_gap.job_builder import read_generation_jobs
from utility_behavior_gap.judging import derive_counted_winner_condition, derive_panel_winner_condition
from utility_behavior_gap.paths import OUTPUT_API, OUTPUT_RAW


JUDGE_VOTES_JSONL = OUTPUT_API / "judge_votes.jsonl"
JUDGED_PAIRS_CSV = OUTPUT_RAW / "judged_pairs.csv"
JUDGE_VOTES_CSV = OUTPUT_RAW / "judge_votes.csv"


def votes_by_pair(path: Path) -> dict[str, list[dict[str, Any]]]:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in read_jsonl(path):
        by_pair[row["pair_uid"]].append(row)
    return by_pair


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-votes", type=int, default=3)
    args = parser.parse_args()

    jobs = read_generation_jobs()
    votes = votes_by_pair(JUDGE_VOTES_JSONL)
    judged_rows: list[dict[str, Any]] = []
    vote_rows: list[dict[str, Any]] = []
    for job in jobs:
        pair_votes = votes.get(job["pair_uid"], [])
        if len(pair_votes) < args.min_votes:
            continue
        conditions = [str(row["winner_condition"]) for row in pair_votes]
        panel = derive_panel_winner_condition(job, conditions)
        counted = derive_counted_winner_condition(job, conditions)
        judged_rows.append(
            {
                "pair_uid": job["pair_uid"],
                "comparison": job["comparison"],
                "source_run": "live_openrouter",
                "actor": job["actor"],
                "actor_label": job["actor_label"],
                "task": job["task"],
                "task_label": job["task_label"],
                "domain": job.get("domain", ""),
                "domain_label": job.get("domain_label", ""),
                "pair_idx": job.get("pair_idx", ""),
                "item_id": job["item_id"],
                "item_label": job["item_label"],
                "repeat": job.get("repeat", ""),
                "framing": job.get("sample_k", ""),
                "condition_a": job["condition_a"],
                "condition_b": job["condition_b"],
                "predicted_condition": job["predicted_condition"],
                "other_condition": job["other_condition"],
                "panel_winner_condition": panel,
                "counted_winner_condition": counted,
                "panel_winner_raw": panel,
                "high_description": job.get("high_description", ""),
                "low_description": job.get("low_description", ""),
                "high_utility": job.get("high_utility", ""),
                "low_utility": job.get("low_utility", ""),
                "delta_u": job.get("delta_u", ""),
                "cause_pair_label": job.get("cause_pair_label", ""),
                "good_text": job.get("good_text", ""),
                "bad_text": job.get("bad_text", ""),
                "amount_high": job.get("amount_high", ""),
                "amount_low": job.get("amount_low", ""),
            }
        )
        for vote in pair_votes:
            vote_rows.append(
                {
                    "pair_uid": vote["pair_uid"],
                    "judge_index": vote["judge_index"],
                    "judge_model": vote["judge_model"],
                    "vote_raw": vote["vote_raw"],
                    "winner_condition": vote["winner_condition"],
                    "success": vote["success"],
                }
            )

    if not judged_rows:
        raise ValueError("No judged pairs were aggregated. Run generation and judging first.")
    write_csv_rows(JUDGED_PAIRS_CSV, judged_rows)
    write_csv_rows(JUDGE_VOTES_CSV, vote_rows)
    print(f"wrote {len(judged_rows)} judged pairs to {JUDGED_PAIRS_CSV}")
    print(f"wrote {len(vote_rows)} judge votes to {JUDGE_VOTES_CSV}")


if __name__ == "__main__":
    main()
