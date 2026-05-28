#!/usr/bin/env python3
"""Run actor generations through OpenRouter."""

from __future__ import annotations

import argparse
import time
from typing import Any

from utility_behavior_gap.io_utils import append_jsonl, read_jsonl
from utility_behavior_gap.job_builder import read_generation_jobs
from utility_behavior_gap.openrouter import OpenRouterClient, actor_model_id, response_text
from utility_behavior_gap.paths import OUTPUT_API


GENERATIONS = OUTPUT_API / "generations.jsonl"


def messages(system_prompt: str, user_prompt: str) -> list[dict[str, str]]:
    rows = []
    if system_prompt:
        rows.append({"role": "system", "content": system_prompt})
    rows.append({"role": "user", "content": user_prompt})
    return rows


def existing_output_ids() -> set[str]:
    if not GENERATIONS.exists():
        return set()
    return {row["output_id"] for row in read_jsonl(GENERATIONS)}


def output_requests(job: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "output_id": f"{job['pair_uid']}::a",
            "pair_uid": job["pair_uid"],
            "condition": job["condition_a"],
            "system_prompt": job.get("system_prompt_a", ""),
            "prompt": job["prompt_a"],
        },
        {
            "output_id": f"{job['pair_uid']}::b",
            "pair_uid": job["pair_uid"],
            "condition": job["condition_b"],
            "system_prompt": job.get("system_prompt_b", ""),
            "prompt": job["prompt_b"],
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="Maximum new generations to run.")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--dry-run", action="store_true", help="Write deterministic placeholder outputs without API calls.")
    args = parser.parse_args()

    jobs = read_generation_jobs()
    done = existing_output_ids()
    client = None if args.dry_run else OpenRouterClient()
    written = 0
    for job in jobs:
        model = "dry-run-model" if args.dry_run else actor_model_id(job["actor"])
        for request in output_requests(job):
            if request["output_id"] in done:
                continue
            if args.limit is not None and written >= args.limit:
                print(f"wrote {written} new generations to {GENERATIONS}")
                return
            started = time.time()
            if args.dry_run:
                text = f"[dry run] {job['comparison']} {request['condition']} output for {job['actor']}"
                raw_response: dict[str, Any] = {}
            else:
                assert client is not None
                raw_response = client.chat_completion(
                    model=model,
                    messages=messages(request["system_prompt"], request["prompt"]),
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                )
                text = response_text(raw_response)
            append_jsonl(
                GENERATIONS,
                {
                    "output_id": request["output_id"],
                    "pair_uid": request["pair_uid"],
                    "actor": job["actor"],
                    "model": model,
                    "condition": request["condition"],
                    "output_text": text,
                    "success": True,
                    "latency_s": round(time.time() - started, 3),
                    "usage": raw_response.get("usage", {}),
                },
            )
            written += 1
    print(f"wrote {written} new generations to {GENERATIONS}")


if __name__ == "__main__":
    main()
