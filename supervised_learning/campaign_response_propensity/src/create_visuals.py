"""Create the ML1 executive summary visual from validated reference outputs."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    module_root = Path(__file__).resolve().parents[1]
    results = json.loads((module_root / "reports" / "reference_results.json").read_text())
    calibration = pd.read_csv(module_root / "data" / "processed" / "test_calibration.csv")
    importance = pd.read_csv(
        module_root / "data" / "processed" / "permutation_importance.csv"
    ).head(7)

    champion = results["test_metrics"]
    rule = results["rule_test_metrics"]
    colors = {"champion": "#235789", "rule": "#9AA6B2", "accent": "#F4A261"}

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 8.2))
    fig.suptitle(
        "ML1 · Campaign Response Propensity — Held-out Decision Evidence",
        fontsize=18,
        fontweight="bold",
        x=0.06,
        ha="left",
    )

    labels = ["PR AUC", "Precision @ capacity", "Lift @ capacity"]
    champion_actual = [
        champion["pr_auc"],
        champion["precision_at_capacity"],
        champion["lift_at_capacity"],
    ]
    rule_actual = [rule["pr_auc"], rule["precision_at_capacity"], rule["lift_at_capacity"]]
    champion_values = [
        selected / baseline for selected, baseline in zip(champion_actual, rule_actual, strict=True)
    ]
    rule_values = [1.0, 1.0, 1.0]
    positions = range(len(labels))
    width = 0.36
    selected_bars = axes[0, 0].bar(
        [position - width / 2 for position in positions],
        champion_values,
        width,
        label="Selected model",
        color=colors["champion"],
    )
    baseline_bars = axes[0, 0].bar(
        [position + width / 2 for position in positions],
        rule_values,
        width,
        label="Current rule",
        color=colors["rule"],
    )
    axes[0, 0].set_xticks(list(positions), labels, rotation=10)
    axes[0, 0].set_title("Model vs. current targeting rule")
    axes[0, 0].set_ylabel("Index (current rule = 1.0)")
    axes[0, 0].set_ylim(0, max(champion_values) + 0.18)
    axes[0, 0].legend(frameon=False)
    for bar, value in zip(selected_bars, champion_values, strict=True):
        axes[0, 0].text(
            bar.get_x() + bar.get_width() / 2,
            value,
            f"{value:.2f}x",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )
    for bar in baseline_bars:
        axes[0, 0].text(
            bar.get_x() + bar.get_width() / 2,
            1.0,
            "1.00x",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    axes[0, 1].plot(
        calibration["predicted_response_rate"],
        calibration["observed_response_rate"],
        marker="o",
        color=colors["champion"],
        linewidth=2,
    )
    limit = max(
        calibration["predicted_response_rate"].max(),
        calibration["observed_response_rate"].max(),
    )
    axes[0, 1].plot([0, limit], [0, limit], "--", color=colors["rule"], linewidth=1.5)
    axes[0, 1].set_xlabel("Mean predicted response")
    axes[0, 1].set_ylabel("Observed response")
    axes[0, 1].set_title("Calibration by score band")

    importance_plot = importance.sort_values("importance_mean")
    axes[1, 0].barh(
        importance_plot["feature"].str.replace("_", " "),
        importance_plot["importance_mean"],
        color=colors["accent"],
    )
    axes[1, 0].set_xlabel("Decrease in PR AUC when permuted")
    axes[1, 0].set_title("Most influential model inputs")

    value_labels = ["Current rule", "Selected model"]
    values = [results["rule_value"]["net_value_usd"], results["champion_value"]["net_value_usd"]]
    bars = axes[1, 1].bar(value_labels, values, color=[colors["rule"], colors["champion"]])
    axes[1, 1].set_title("Illustrative realized net value")
    axes[1, 1].set_ylabel("USD per held-out two-cohort period")
    for bar, value in zip(bars, values, strict=True):
        axes[1, 1].text(
            bar.get_x() + bar.get_width() / 2,
            value,
            f"${value:,.0f}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    fig.text(
        0.06,
        0.015,
        "Synthetic data. Propensity predicts response, not incremental campaign lift. "
        "Holdout: Jul–Aug 2026; capacity: 20%.",
        fontsize=9.5,
        color="#4B5563",
    )
    fig.tight_layout(rect=[0.04, 0.05, 0.98, 0.93])
    output = module_root / "reports" / "ml1_executive_summary.png"
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(output)


if __name__ == "__main__":
    main()
