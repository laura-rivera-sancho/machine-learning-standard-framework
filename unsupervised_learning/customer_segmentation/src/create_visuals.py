"""Create the ML2 executive summary visual from reference results."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import pandas as pd

MODULE = Path(__file__).resolve().parents[1]
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt  # noqa: E402

RESULTS_PATH = MODULE / "reports" / "reference_results.json"
OUTPUT_PATH = MODULE / "reports" / "ml2_executive_summary.png"

COLORS = ["#173F5F", "#20639B", "#3CAEA3", "#F6D55C"]


def create_visual(results: dict) -> None:
    profiles = pd.DataFrame(results["segment_profiles"])
    candidates = pd.DataFrame(results["candidate_comparison"])
    selected = results["selected_model"]

    fig = plt.figure(figsize=(14, 9), facecolor="#F7F8FA")
    grid = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.30)
    fig.suptitle(
        "ML2 Customer Segmentation | Decision Summary",
        x=0.06,
        y=0.97,
        ha="left",
        fontsize=20,
        fontweight="bold",
        color="#152536",
    )
    fig.text(
        0.06,
        0.925,
        f"{results['customers_segmented']:,} customers • {selected.replace('_', ' ').title()} • "
        f"temporal ARI {results['temporal_assignment_ari']:.2f}",
        fontsize=11,
        color="#526273",
    )

    ax1 = fig.add_subplot(grid[0, 0])
    profiles = profiles.sort_values("customer_share", ascending=True)
    ax1.barh(profiles["segment"], profiles["customer_share"] * 100, color=COLORS)
    for y, value in enumerate(profiles["customer_share"] * 100):
        ax1.text(value + 0.5, y, f"{value:.1f}%", va="center", fontsize=9)
    ax1.set_title("Actionable customer groups", loc="left", fontweight="bold")
    ax1.set_xlabel("Share of eligible customer base")
    ax1.set_xlim(0, max(profiles["customer_share"] * 100) + 7)

    ax2 = fig.add_subplot(grid[0, 1])
    compact = candidates[candidates["model"].str.match(r"(kmeans|gaussian_mixture)_[45]$")]
    sizes = compact["smallest_segment_share"] * 1400
    colors = ["#E45756" if name == selected else "#3CAEA3" for name in compact["model"]]
    ax2.scatter(compact["stability_ari"], compact["silhouette"], s=sizes, c=colors, alpha=0.85)
    for _, row in compact.iterrows():
        ax2.annotate(
            row["model"].replace("gaussian_mixture", "GMM"),
            (row["stability_ari"], row["silhouette"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )
    ax2.set_title("Candidate quality and stability", loc="left", fontweight="bold")
    ax2.set_xlabel("Bootstrap stability (ARI)")
    ax2.set_ylabel("Silhouette")
    ax2.grid(alpha=0.2)

    ax3 = fig.add_subplot(grid[1, 0])
    heat_features = [
        "recency_days",
        "frequency_12m",
        "monetary_12m",
        "discount_order_share",
        "email_engagement_rate",
        "digital_order_share",
    ]
    heat = profiles.set_index("segment")[heat_features]
    z = (heat - heat.mean()) / heat.std(ddof=0)
    image = ax3.imshow(z, cmap="RdYlBu", aspect="auto", vmin=-1.6, vmax=1.6)
    ax3.set_xticks(
        range(len(heat_features)),
        ["Recency", "Frequency", "Spend", "Discount", "Email", "Digital"],
        rotation=35,
        ha="right",
    )
    ax3.set_yticks(range(len(z)), z.index)
    ax3.set_title("Relative behavioral profile", loc="left", fontweight="bold")
    fig.colorbar(image, ax=ax3, fraction=0.046, pad=0.04, label="Standardized profile")

    ax4 = fig.add_subplot(grid[1, 1])
    ax4.axis("off")
    ax4.set_title("Recommended activation tests", loc="left", fontweight="bold")
    actions = [
        ("Champions", "Recognition, early access, referral test"),
        ("At Risk", "Suppression-aware win-back experiment"),
        ("Digital Growth", "Cross-sell and onboarding journey"),
        ("Deal Seekers", "Margin-safe offer and threshold test"),
    ]
    y = 0.88
    for idx, (segment, action) in enumerate(actions):
        ax4.add_patch(plt.Rectangle((0.0, y - 0.08), 0.025, 0.12, color=COLORS[idx]))
        ax4.text(0.05, y, segment, fontweight="bold", fontsize=11, va="center")
        ax4.text(0.05, y - 0.055, action, fontsize=9.5, color="#526273", va="center")
        y -= 0.21
    ax4.text(
        0,
        -0.02,
        "Use segments to design tests—not to assume causal response.\n"
        "Keep consent, suppression, fairness review, and holdouts outside the model.",
        fontsize=9.5,
        color="#7A3E00",
        bbox={"boxstyle": "round,pad=0.5", "facecolor": "#FFF4DD", "edgecolor": "#F6D55C"},
    )

    for ax in (ax1, ax2):
        ax.spines[["top", "right"]].set_visible(False)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    create_visual(results)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
