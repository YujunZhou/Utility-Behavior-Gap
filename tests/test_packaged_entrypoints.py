import importlib
from pathlib import Path


ENTRYPOINT_MODULES = [
    "utility_behavior_gap.scripts.aggregate_results",
    "utility_behavior_gap.scripts.analyze_amount_pooled",
    "utility_behavior_gap.scripts.analyze_utility_gap_dose_response",
    "utility_behavior_gap.scripts.plot_highlow_main",
    "utility_behavior_gap.scripts.plot_highlow_within_count",
    "utility_behavior_gap.scripts.plot_incentive_amount_main",
    "utility_behavior_gap.scripts.plot_moral_nolabel_main",
    "utility_behavior_gap.scripts.plot_sys_prompt_main",
    "utility_behavior_gap.scripts.plot_utility_top_bottom",
    "utility_behavior_gap.scripts.reproduce_all",
    "utility_behavior_gap.scripts.summarize_paper_tables",
    "utility_behavior_gap.scripts.validate_release_inputs",
]


def test_reproduction_entrypoints_live_under_source_package():
    for module_name in ENTRYPOINT_MODULES:
        importlib.import_module(module_name)

    repo_root = Path(__file__).resolve().parents[1]
    assert not (repo_root / "scripts").exists()
