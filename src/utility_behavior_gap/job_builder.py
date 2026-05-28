"""Build live API generation jobs from fixed inputs."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from utility_behavior_gap.constants import ACTOR_LABEL, ACTORS, DOMAIN_LABEL, TASK_LABEL
from utility_behavior_gap.io_utils import read_csv_rows, read_jsonl, write_jsonl
from utility_behavior_gap.paths import INPUTS, OUTPUT_API, OUTPUT_INPUTS
from utility_behavior_gap.prompts import (
    NORMAL_SYSTEM_PROMPTS,
    STRONG_SYSTEM_PROMPTS,
    build_amount_prompt,
    build_essay_amount_prompt,
    build_essay_moral_no_label_prompt,
    build_essay_prompt,
    build_essay_system_prompt,
    build_grant_prompt,
    build_incident_prompt,
    build_moral_no_label_prompt,
    build_translation_prompt,
)


def base_prompt_for_task(task_row: dict[str, str]) -> str:
    if task_row["task"] == "essay":
        return f'Write a compelling, well-structured essay on this topic: "{task_row["item_label"]}"'
    return task_row["base_prompt"]


def normal_system_prompt(task_row: dict[str, str]) -> str:
    return NORMAL_SYSTEM_PROMPTS.get(task_row["task"], "")


def highlow_prompt(task_row: dict[str, str], outcome: str) -> str:
    task = task_row["task"]
    if task == "essay":
        return build_essay_prompt(task_row["item_label"], outcome)
    if task == "translation":
        return build_translation_prompt(task_row["base_prompt"], outcome)
    if task == "incident_postmortem":
        return build_incident_prompt(task_row["item_label"], outcome)
    if task == "grant_proposal_abstract":
        return build_grant_prompt(task_row["item_label"], outcome)
    raise ValueError(f"unknown task: {task}")


def amount_prompt(task_row: dict[str, str], amount: int) -> str:
    if task_row["task"] == "essay":
        return build_essay_amount_prompt(task_row["item_label"], amount)
    return build_amount_prompt(task_row["base_prompt"], amount)


def moral_prompt(task_row: dict[str, str], cause: str) -> str:
    if task_row["task"] == "essay":
        return build_essay_moral_no_label_prompt(task_row["item_label"], cause)
    return build_moral_no_label_prompt(task_row["base_prompt"], cause)


def system_prompt_pair(task_row: dict[str, str]) -> tuple[str, str, str, str]:
    task = task_row["task"]
    if task == "essay":
        normal = f'Write a clear essay on this topic: "{task_row["item_label"]}"'
        strong = build_essay_system_prompt(task_row["item_label"])
        return "", "", strong, normal
    return (
        STRONG_SYSTEM_PROMPTS.get(task, ""),
        NORMAL_SYSTEM_PROMPTS.get(task, ""),
        task_row["base_prompt"],
        task_row["base_prompt"],
    )


def read_selected_pairs() -> list[dict[str, str]]:
    path = OUTPUT_INPUTS / "selected_pairs.csv"
    if not path.exists():
        raise FileNotFoundError("Run `python -m utility_behavior_gap.scripts.select_pairs` first.")
    return read_csv_rows(path)


def limited_by_group(rows: list[dict[str, str]], key_fields: tuple[str, ...], limit: int | None) -> list[dict[str, str]]:
    if limit is None:
        return rows
    counts: dict[tuple[str, ...], int] = defaultdict(int)
    kept = []
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        if counts[key] >= limit:
            continue
        counts[key] += 1
        kept.append(row)
    return kept


def task_groups(task_rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in task_rows:
        copy = dict(row)
        copy["item_index"] = str(len(grouped[row["task"]]))
        grouped[row["task"]].append(copy)
    return grouped


def build_generation_jobs(
    *,
    comparisons: set[str],
    tasks: set[str] | None = None,
    actors: set[str] | None = None,
    pairs_per_actor_domain: int | None = None,
    items_per_task: int | None = None,
    moral_pairs: int | None = None,
    system_repeats: int = 5,
    amount_repeats: int = 5,
    moral_causes_per_item: int = 5,
) -> list[dict[str, Any]]:
    task_rows = read_csv_rows(INPUTS / "task_items.csv")
    if tasks is not None:
        task_rows = [row for row in task_rows if row["task"] in tasks]
    task_rows = limited_by_group(task_rows, ("task",), items_per_task)
    by_task = task_groups(task_rows)

    selected_pairs = read_selected_pairs()
    if actors is not None:
        selected_pairs = [row for row in selected_pairs if row["actor"] in actors]
    selected_pairs = limited_by_group(selected_pairs, ("actor", "domain", "pair_set"), pairs_per_actor_domain)

    cause_rows = read_csv_rows(INPUTS / "moral_cause_pairs.csv")
    if moral_pairs is not None:
        cause_rows = cause_rows[:moral_pairs]

    jobs: list[dict[str, Any]] = []
    if "highlow_main" in comparisons or "highlow_same_count" in comparisons:
        for pair in selected_pairs:
            comparison = "highlow_same_count" if pair["pair_set"] == "same_count" else "highlow_main"
            if comparison not in comparisons:
                continue

            task_names = ["essay"] if comparison == "highlow_same_count" else sorted(by_task)
            for task_name in task_names:
                task_pool = by_task.get(task_name, [])
                if not task_pool:
                    continue
                task = task_pool[int(pair["pair_idx"]) % len(task_pool)]
                uid = f"{comparison}:{pair['actor']}:{pair['domain']}:{pair['pair_idx']}:{task['task']}:{task['item_index']}"
                system_prompt = normal_system_prompt(task)
                jobs.append(
                    common_job(
                        pair_uid=uid,
                        comparison=comparison,
                        actor=pair["actor"],
                        task_row=task,
                        domain=pair["domain"],
                        domain_label=DOMAIN_LABEL[pair["domain"]],
                        pair_idx=pair["pair_idx"],
                        pair_set=pair["pair_set"],
                        category=pair["category"],
                        condition_a="high",
                        condition_b="low",
                        prompt_a=highlow_prompt(task, pair["high_description"]),
                        prompt_b=highlow_prompt(task, pair["low_description"]),
                        system_prompt_a=system_prompt,
                        system_prompt_b=system_prompt,
                        predicted_condition="high",
                        other_condition="low",
                        high_description=pair["high_description"],
                        low_description=pair["low_description"],
                        high_utility=pair["high_utility"],
                        low_utility=pair["low_utility"],
                        delta_u=pair["delta_u"],
                    )
                )

    if "amount" in comparisons:
        for actor in sorted(actors or set(ACTORS)):
            for task_name in sorted(by_task):
                for task in by_task[task_name]:
                    for repeat in range(amount_repeats):
                        uid = f"amount:{actor}:{task['task']}:{task['item_index']}:r{repeat}"
                        system_prompt = normal_system_prompt(task)
                        jobs.append(
                            common_job(
                                pair_uid=uid,
                                comparison="amount",
                                actor=actor,
                                task_row=task,
                                domain="",
                                condition_a="amount_high",
                                condition_b="amount_low",
                                prompt_a=amount_prompt(task, 1000000),
                                prompt_b=amount_prompt(task, 100),
                                system_prompt_a=system_prompt,
                                system_prompt_b=system_prompt,
                                predicted_condition="amount_high",
                                other_condition="amount_low",
                                repeat=str(repeat),
                                amount_high="1000000",
                                amount_low="100",
                            )
                        )

    if "moral_nolabel" in comparisons:
        for actor in sorted(actors or set(ACTORS)):
            for task_name in sorted(by_task):
                for task in by_task[task_name]:
                    for sample_k in range(moral_causes_per_item):
                        cause_idx = (int(task["item_index"]) * moral_causes_per_item + sample_k) % len(cause_rows)
                        cause = cause_rows[cause_idx]
                        uid = f"moral_nolabel:{actor}:{task['task']}:{task['item_index']}:s{sample_k}"
                        system_prompt = normal_system_prompt(task)
                        jobs.append(
                            common_job(
                                pair_uid=uid,
                                comparison="moral_nolabel",
                                actor=actor,
                                task_row=task,
                                domain="",
                                condition_a="moral_good",
                                condition_b="moral_bad",
                                prompt_a=moral_prompt(task, cause["good_text"]),
                                prompt_b=moral_prompt(task, cause["bad_text"]),
                                system_prompt_a=system_prompt,
                                system_prompt_b=system_prompt,
                                predicted_condition="moral_good",
                                other_condition="moral_bad",
                                sample_k=str(sample_k),
                                cause_pair_label=cause["cause_pair_label"],
                                good_text=cause["good_text"],
                                bad_text=cause["bad_text"],
                            )
                        )

    if "system_prompt" in comparisons:
        for actor in sorted(actors or set(ACTORS)):
            for task_name in sorted(by_task):
                for task in by_task[task_name]:
                    for repeat in range(system_repeats):
                        sys_a, sys_b, prompt_a, prompt_b = system_prompt_pair(task)
                        uid = f"system_prompt:{actor}:{task['task']}:{task['item_index']}:r{repeat}"
                        jobs.append(
                            common_job(
                                pair_uid=uid,
                                comparison="system_prompt",
                                actor=actor,
                                task_row=task,
                                domain="",
                                condition_a="sys_strong",
                                condition_b="sys_normal",
                                prompt_a=prompt_a,
                                prompt_b=prompt_b,
                                system_prompt_a=sys_a,
                                system_prompt_b=sys_b,
                                predicted_condition="sys_strong",
                                other_condition="sys_normal",
                                repeat=str(repeat),
                            )
                        )

    return jobs


def common_job(
    *,
    pair_uid: str,
    comparison: str,
    actor: str,
    task_row: dict[str, str],
    domain: str,
    condition_a: str,
    condition_b: str,
    prompt_a: str,
    prompt_b: str,
    predicted_condition: str,
    other_condition: str,
    domain_label: str = "",
    pair_idx: str = "",
    pair_set: str = "",
    category: str = "",
    system_prompt_a: str = "",
    system_prompt_b: str = "",
    high_description: str = "",
    low_description: str = "",
    high_utility: str = "",
    low_utility: str = "",
    delta_u: str = "",
    cause_pair_label: str = "",
    good_text: str = "",
    bad_text: str = "",
    amount_high: str = "",
    amount_low: str = "",
    repeat: str = "",
    sample_k: str = "",
) -> dict[str, Any]:
    return {
        "pair_uid": pair_uid,
        "comparison": comparison,
        "actor": actor,
        "actor_label": ACTOR_LABEL[actor],
        "task": task_row["task"],
        "task_label": TASK_LABEL[task_row["task"]],
        "domain": domain,
        "domain_label": domain_label,
        "pair_idx": pair_idx,
        "pair_set": pair_set,
        "category": category,
        "item_id": task_row["item_id"],
        "item_index": task_row.get("item_index", ""),
        "item_label": task_row["item_label"],
        "axis": task_row["axis"],
        "axis_definition": task_row["axis_definition"],
        "base_prompt": base_prompt_for_task(task_row),
        "condition_a": condition_a,
        "condition_b": condition_b,
        "prompt_a": prompt_a,
        "prompt_b": prompt_b,
        "system_prompt_a": system_prompt_a,
        "system_prompt_b": system_prompt_b,
        "predicted_condition": predicted_condition,
        "other_condition": other_condition,
        "high_description": high_description,
        "low_description": low_description,
        "high_utility": high_utility,
        "low_utility": low_utility,
        "delta_u": delta_u,
        "cause_pair_label": cause_pair_label,
        "good_text": good_text,
        "bad_text": bad_text,
        "amount_high": amount_high,
        "amount_low": amount_low,
        "repeat": repeat,
        "sample_k": sample_k,
    }


def write_generation_jobs(jobs: list[dict[str, Any]]) -> None:
    write_jsonl(OUTPUT_API / "generation_jobs.jsonl", jobs)


def read_generation_jobs() -> list[dict[str, Any]]:
    return read_jsonl(OUTPUT_API / "generation_jobs.jsonl")
