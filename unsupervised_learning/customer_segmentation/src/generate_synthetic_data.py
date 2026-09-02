"""Generate deterministic synthetic customer snapshots for ML2."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

MODULE = Path(__file__).resolve().parents[1]
RAW_PATH = MODULE / "data" / "raw" / "customer_snapshots.csv"
SAMPLE_PATH = MODULE / "data" / "raw" / "customer_snapshots_sample.csv"

PROFILE_NAMES = np.array(["champions", "loyal", "growth", "deal_seekers", "at_risk", "dormant"])


def _snapshot(
    seed: int, n_customers: int, date: str, drift: float, profile: np.ndarray | None = None
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    weights = np.array([0.13, 0.20, 0.19, 0.18, 0.17, 0.13])
    if profile is None:
        profile = rng.choice(len(PROFILE_NAMES), n_customers, p=weights)

    recency_base = np.array([9, 25, 48, 34, 105, 220])
    frequency_base = np.array([18, 12, 7, 11, 4, 1.5])
    order_base = np.array([145, 105, 78, 61, 92, 54])
    discount_base = np.array([0.11, 0.18, 0.24, 0.58, 0.27, 0.35])
    email_base = np.array([0.68, 0.52, 0.40, 0.48, 0.22, 0.10])
    digital_base = np.array([0.74, 0.58, 0.82, 0.70, 0.46, 0.35])
    return_base = np.array([0.04, 0.05, 0.07, 0.09, 0.08, 0.06])
    tenure_base = np.array([1450, 1280, 520, 760, 1180, 940])

    recency = rng.gamma(2.2, recency_base[profile] / 2.2) * (1 + drift)
    frequency = rng.poisson(frequency_base[profile] * (1 - 0.25 * drift)).clip(0)
    avg_order = rng.lognormal(np.log(order_base[profile]), 0.28)
    monetary = frequency * avg_order * rng.lognormal(0, 0.12, n_customers)
    discount = rng.beta(
        np.maximum(discount_base[profile] * 18, 0.5),
        np.maximum((1 - discount_base[profile]) * 18, 0.5),
    )
    email = rng.beta(
        np.maximum(email_base[profile] * 15, 0.5),
        np.maximum((1 - email_base[profile]) * 15, 0.5),
    )
    digital = rng.beta(
        np.maximum(digital_base[profile] * 16, 0.5),
        np.maximum((1 - digital_base[profile]) * 16, 0.5),
    )
    returns = rng.beta(
        np.maximum(return_base[profile] * 28, 0.5),
        np.maximum((1 - return_base[profile]) * 28, 0.5),
    )
    tenure = rng.gamma(5, tenure_base[profile] / 5)

    return pd.DataFrame(
        {
            "customer_id": [f"C{i:06d}" for i in range(1, n_customers + 1)],
            "snapshot_date": pd.Timestamp(date),
            "recency_days": np.round(recency).astype(int),
            "frequency_12m": frequency.astype(int),
            "monetary_12m": monetary.round(2),
            "avg_order_value": avg_order.round(2),
            "discount_order_share": discount.round(4),
            "email_engagement_rate": email.round(4),
            "digital_order_share": digital.round(4),
            "return_rate": returns.round(4),
            "tenure_days": np.round(tenure).astype(int),
            "synthetic_profile_truth": PROFILE_NAMES[profile],
            "marketing_consent": rng.binomial(1, 0.91, n_customers),
            "region": rng.choice(["NORTHEAST", "SOUTH", "MIDWEST", "WEST"], n_customers),
        }
    )


def generate_clean_data(seed: int = 42, n_customers: int = 6000) -> pd.DataFrame:
    """Return two comparable customer snapshots."""
    weights = np.array([0.13, 0.20, 0.19, 0.18, 0.17, 0.13])
    profile = np.random.default_rng(seed).choice(len(PROFILE_NAMES), n_customers, p=weights)
    prior = _snapshot(seed + 1, n_customers, "2026-06-30", drift=0.00, profile=profile)
    current = _snapshot(seed + 2, n_customers, "2026-08-31", drift=0.04, profile=profile)
    return pd.concat([prior, current], ignore_index=True)


def generate_raw_data(seed: int = 42, n_customers: int = 6000) -> pd.DataFrame:
    """Add controlled defects so data-quality controls are testable."""
    data = generate_clean_data(seed, n_customers)
    rng = np.random.default_rng(seed + 99)
    current_idx = data.index[data["snapshot_date"].eq(data["snapshot_date"].max())]
    for column in ["monetary_12m", "email_engagement_rate"]:
        missing = rng.choice(current_idx, max(2, n_customers // 200), replace=False)
        data.loc[missing, column] = np.nan
    data.loc[current_idx[:2], "recency_days"] = -3
    data.loc[current_idx[2:4], "discount_order_share"] = 1.4
    duplicates = data.loc[current_idx[:8]].copy()
    return pd.concat([data, duplicates], ignore_index=True)


def main() -> None:
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw = generate_raw_data()
    raw.to_csv(RAW_PATH, index=False)
    sample = raw.groupby("snapshot_date", group_keys=False).head(250)
    sample.to_csv(SAMPLE_PATH, index=False)
    print(f"Wrote {len(raw):,} rows to {RAW_PATH}")


if __name__ == "__main__":
    main()
