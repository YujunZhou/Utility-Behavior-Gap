#!/usr/bin/env python3
"""Run blind pairwise judging through OpenRouter."""

from __future__ import annotations

import argparse
import random
import re
import time
from typing import Any

from utility_behavior_gap.io_utils import append_jsonl, read_jsonl
from utility_behavior_gap.job_builder import read_generation_jobs
from utility_behavior_gap.openrouter import OpenRouterClient, judge_model_ids, response_text
from utility_behavior_gap.paths import OUTPUT_API
from utility_behavior_gap.prompts import build_pairwise_judge_prompt


GENERATIONS = OUTPUT_API / "generations.jsonl"
JUDGE_VOTES = OUTPUT_API / "judge_votes.jsonl"


def parse_winner(text: str) -> str:
    match = re.search(r"winner\s*:\s*(A|B|tie)\b", text, flags=re.IGNORECASE)
    if match:
        return match.group(1).lower()
    match = re.search(r"answer\s*:\s*(A|B|X|Y|tie)\b", text, flags=re.IGNORECASE)
    if match:
        value = match.group(1).lower()
        return {"x": "a", "y": "b"}.get(value, value)
    return "unresolved"


def generation_map() -> dict[str, dict[str, Any]]:
    return {row["output_id"]: row for row in read_jsonl(GENERATIONS)}


def existing_vote_keys() -> set[tuple[str, str]]:
    if not JUDGE_VOTES.exists():
        return set()
    return {(row["pair_uid"], row["judge_model"]) for row in read_jsonl(JUDGE_VOTES)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="Maximum new judge votes to run.")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=120)
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--dry-run", action="store_true", help="Write deterministic placeholder votes without API calls.")
    args = parser.parse_args()

    jobs = read_generation_jobs()
    generations = generation_map()
    done = existing_vote_keys()
    judges = ["dry-run-judge-a", "dry-run-judge-b", "dry-run-judge-c"] if args.dry_run else judge_model_ids()
    client = None if args.dry_run else OpenRouterClient()
    rng = random.Random(args.seed)
    written = 0

    for job in jobs:
        out_a = generations.get(f"{job['pair_uid']}::a")
        out_b = generations.get(f"{job['pair_uid']}::b")
        if out_a is None or out_b is None:
            continue
        for judge_idx, judge_model in enumerate(judges):
            if (job["pair_uid"], judge_model) in done:
                continue
            if args.limit is not None and written >= args.limit:
                print(f"wrote {written} new judge votes to {JUDGE_VOTES}")
                return

            flip = rng.random() < 0.5
            output_a = out_b if flip else out_a
            output_b = out_a if flip else out_b
            prompt = build_pairwise_judge_prompt(
                axis=job["axis"],
                axis_def=job["axis_definition"],
                base_prompt=job["base_prompt"],
                output_a=output_a["output_text"],
                output_b=output_b["output_text"],
            )
            started = time.time()
            if args.dry_run:
                raw_text = "winner: tie\nreason: dry run"
            else:
                assert client is not None
                response = client.chat_completion(
                    model=judge_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                )
                raw_text = response_text(response)
            parsed = parse_winner(raw_text)
            if parsed == "a":
                winner_condition = output_a["condition"]
            elif parsed == "b":
                winner_condition = output_b["condition"]
            elif parsed == "tie":
                winner_condition = "tie"
            else:
                winner_condition = "unresolved"
            append_jsonl(
                JUDGE_VOTES,
                {
                    "pair_uid": job["pair_uid"],
                    "judge_index": judge_idx + 1,
                    "judge_model": judge_model,
                    "flipped": flip,
                    "vote_raw": raw_text,
                    "winner_condition": winner_condition,
                    "success": True,
                    "latency_s": round(time.time() - started, 3),
                },
            )
            written += 1
    print(f"wrote {written} new judge votes to {JUDGE_VOTES}")


if __name__ == "__main__":
    main()
