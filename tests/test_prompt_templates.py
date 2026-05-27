from utility_behavior_gap.prompts import (
    AMOUNT_PREFIX,
    MORAL_NO_LABEL_PREFIX,
    NON_ESSAY_SUCCESS_PREFIX,
    build_amount_prompt,
    build_essay_judge_prompt,
    build_essay_prompt,
    build_grant_prompt,
    build_incident_prompt,
    build_moral_no_label_prompt,
    build_pairwise_judge_prompt,
    build_translation_prompt,
)


def test_non_essay_prompts_attach_success_contingent_consequence():
    outcome = "100 people receive emergency medical care"
    prompts = [
        build_grant_prompt("offline-first appointment reminders", outcome),
        build_incident_prompt("a deployment caused stale account balances", outcome),
        build_translation_prompt("Sample source sentence.", outcome),
    ]

    for prompt in prompts:
        assert NON_ESSAY_SUCCESS_PREFIX.format(outcome=outcome) in prompt
        assert outcome in prompt
        assert "judged better" in prompt


def test_essay_prompt_blinds_the_consequence_instructions():
    prompt = build_essay_prompt(
        "Public transit should be expanded",
        "100 people receive emergency medical care",
    )

    assert "$1,000 will be donated" in prompt
    assert "Do not mention the prize, donation" in prompt


def test_moral_and_amount_prefixes_match_reported_conditions():
    moral = build_moral_no_label_prompt("Write the abstract.", "Ban conversion therapy.")
    amount = build_amount_prompt("Write the abstract.", "1,000,000")

    assert MORAL_NO_LABEL_PREFIX.format(cause="Ban conversion therapy.") in moral
    assert AMOUNT_PREFIX.format(amount="1,000,000") in amount


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
    assert "donated" not in prompt.lower()


def test_essay_judge_prompt_uses_x_y_tie_format():
    prompt = build_essay_judge_prompt(
        topic="Public transit should be expanded",
        response_x="Essay X",
        response_y="Essay Y",
    )

    assert "Response X" in prompt
    assert "Response Y" in prompt
    assert "Answer: TIE" in prompt
