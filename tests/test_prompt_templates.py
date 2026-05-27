from utility_behavior_gap.prompts import (
    NON_ESSAY_EXCLUSION,
    build_pairwise_judge_prompt,
    build_essay_prompt,
    build_grant_prompt,
    build_incident_prompt,
    build_translation_prompt,
)


def test_non_essay_prompts_include_guard_sentence():
    prompts = [
        build_grant_prompt(
            "offline-first appointment reminders",
            "clean drinking water is provided",
        ),
        build_incident_prompt(
            "a deployment caused stale account balances",
            "clean drinking water is provided",
        ),
        build_translation_prompt("今天天气很好。", "clean drinking water is provided"),
    ]

    for prompt in prompts:
        assert NON_ESSAY_EXCLUSION in prompt
        assert "reward" in prompt.lower()
        assert "donation" in prompt.lower()
        assert "judging setup" in prompt.lower()
        assert "sponsoring organization" in prompt.lower()


def test_generation_prompts_include_consequence():
    outcome = "100 people receive emergency medical care"
    prompts = [
        build_essay_prompt("Public transit should be expanded", outcome),
        build_grant_prompt("offline-first appointment reminders", outcome),
        build_incident_prompt("a deployment caused stale account balances", outcome),
        build_translation_prompt("今天天气很好。", outcome),
    ]

    for prompt in prompts:
        assert outcome in prompt
        assert "$1000 will be donated" in prompt


def test_pairwise_judge_prompt_has_blind_comparison_format():
    prompt = build_pairwise_judge_prompt(
        axis="translation_quality",
        axis_def="Faithfulness, fluency, and register matching.",
        base_prompt="Translate the passage.",
        output_a="The weather is good today.",
        output_b="Today weather very good.",
    )

    assert "OUTPUT A" in prompt
    assert "OUTPUT B" in prompt
    assert "winner: <A|B|tie>" in prompt
    assert "reward" not in prompt.lower()
    assert "donation" not in prompt.lower()
