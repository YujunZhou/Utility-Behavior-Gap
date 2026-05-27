#!/usr/bin/env python3
"""Recompute the utility-gap dose-response appendix analysis.

Input:
  outputs/analysis/utility_gap_dose_response_trials.csv

Outputs:
  outputs/analysis/utility_gap_dose_response_bins.csv
  outputs/analysis/utility_gap_dose_response_regression.csv
  outputs/figures/utility_gap_dose_response.pdf
  outputs/figures/utility_gap_dose_response.png
"""

from __future__ import annotations

import csv
import math
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from utility_behavior_gap.paths import ANALYSIS, FIGURES

ANA = ANALYSIS
FIG = FIGURES
TRIALS_CSV = ANA / "utility_gap_dose_response_trials.csv"
BINS_CSV = ANA / "utility_gap_dose_response_bins.csv"
REG_CSV = ANA / "utility_gap_dose_response_regression.csv"
PDF_PATH = FIG / "utility_gap_dose_response.pdf"
PNG_PATH = FIG / "utility_gap_dose_response.png"

TASK_ORDER = ["essay", "translation", "incident_postmortem", "grant_proposal_abstract"]
DOMAIN_ORDER = ["religions", "animals", "countries", "political"]


def wilson(wins: int, total: int, z: float = 1.96) -> tuple[float, float, float]:
    if total == 0:
        return (float("nan"),) * 3
    p = wins / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return p, max(0.0, center - half), min(1.0, center + half)


def load_non_tied_trials() -> pd.DataFrame:
    df = pd.read_csv(TRIALS_CSV)
    df = df[df["high_win"].notna()].copy()
    df["high_win"] = df["high_win"].astype(int)
    df["delta_u"] = df["delta_u"].astype(float)
    return df


def write_bins(df: pd.DataFrame) -> list[dict]:
    delta = df["delta_u"].to_numpy()
    edges = np.quantile(delta, np.linspace(0, 1, 11))
    edges[-1] += 1e-9

    rows: list[dict] = []
    for i in range(10):
        lo = float(edges[i])
        hi = float(edges[i + 1])
        sub = df[(df["delta_u"] >= lo) & (df["delta_u"] < hi)]
        wins = int(sub["high_win"].sum())
        n = int(len(sub))
        rate, ci_lo, ci_hi = wilson(wins, n)
        rows.append(
            {
                "bin": i + 1,
                "du_lo": lo,
                "du_hi": hi,
                "du_mid": float(sub["delta_u"].mean()),
                "n": n,
                "high_wins": wins,
                "low_wins": n - wins,
                "high_win_rate": rate,
                "ci_lo": ci_lo,
                "ci_hi": ci_hi,
            }
        )

    with BINS_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {key: (round(value, 5) if isinstance(value, float) else value) for key, value in row.items()}
            )
    return rows


def write_regressions(df: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []

    def add_logit(name: str, formula: str, data: pd.DataFrame, term: str = "delta_u") -> None:
        model = smf.logit(formula, data=data).fit(disp=0)
        coef = float(model.params[term])
        se = float(model.bse[term])
        p_value = float(model.pvalues[term])
        ci = model.conf_int().loc[term]
        rows.append(
            {
                "model": name,
                "n": int(model.nobs),
                "term": term,
                "coef": coef,
                "se": se,
                "p_value": p_value,
                "odds_ratio": math.exp(coef),
                "or_ci_lo": math.exp(float(ci[0])),
                "or_ci_hi": math.exp(float(ci[1])),
            }
        )

    add_logit("uncontrolled: high_win ~ delta_u", "high_win ~ delta_u", df)
    add_logit(
        "controlled: + actor + task + domain FE",
        "high_win ~ delta_u + C(actor) + C(task) + C(domain)",
        df,
    )
    for task in TASK_ORDER:
        sub = df[df["task"] == task]
        if len(sub) > 30:
            add_logit(f"task={task}: high_win ~ delta_u", "high_win ~ delta_u", sub)
    for domain in DOMAIN_ORDER:
        sub = df[df["domain"] == domain]
        if len(sub) > 30:
            add_logit(f"domain={domain}: high_win ~ delta_u", "high_win ~ delta_u", sub)

    with REG_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {key: (round(value, 6) if isinstance(value, float) else value) for key, value in row.items()}
            )
    return rows


def write_figure(df: pd.DataFrame, bins: list[dict]) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42, "figure.dpi": 200})
    fig, ax = plt.subplots(figsize=(7.2, 4.6))

    mids = [row["du_mid"] for row in bins]
    rates = [row["high_win_rate"] for row in bins]
    lo_err = [row["high_win_rate"] - row["ci_lo"] for row in bins]
    hi_err = [row["ci_hi"] - row["high_win_rate"] for row in bins]

    ax.axhline(0.5, color="#9CA3AF", ls=(0, (4, 3)), lw=1.2, zorder=1)
    ax.errorbar(
        mids,
        rates,
        yerr=[lo_err, hi_err],
        fmt="o",
        color="#2A8C9E",
        ecolor="#9DBFC7",
        capsize=3,
        ms=7,
        zorder=3,
        label="decile bins (Wilson 95% CI)",
    )

    model = smf.logit("high_win ~ delta_u", data=df).fit(disp=0)
    xs = np.linspace(float(df["delta_u"].min()), float(df["delta_u"].max()), 100)
    ys = 1 / (1 + np.exp(-(model.params["Intercept"] + model.params["delta_u"] * xs)))
    ax.plot(xs, ys, color="#C2304A", lw=2, zorder=2, label="logistic fit")

    ax.set_xlabel("Fitted utility gap  delta_u = u_high - u_low")
    ax.set_ylabel("High-utility-side win rate (non-tied)")
    ax.set_ylim(0.30, 0.70)
    ax.set_title("Utility-gap dose-response (main high-low experiment)", fontsize=12)
    ax.legend(frameon=False, fontsize=9)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    fig.tight_layout()
    fig.savefig(PDF_PATH, bbox_inches="tight")
    fig.savefig(PNG_PATH, dpi=300, bbox_inches="tight")


def main() -> None:
    ANA.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    df = load_non_tied_trials()
    bins = write_bins(df)
    regressions = write_regressions(df)
    write_figure(df, bins)

    print(f"non-tied pairs: {len(df)}")
    print(f"wrote {BINS_CSV}")
    print(f"wrote {REG_CSV}")
    print(f"wrote {PDF_PATH}")
    print(f"wrote {PNG_PATH}")
    for row in regressions[:2]:
        print(
            f"{row['model']}: coef={row['coef']:.4f}, p={row['p_value']:.3g}, "
            f"OR={row['odds_ratio']:.3f}"
        )


if __name__ == "__main__":
    main()
