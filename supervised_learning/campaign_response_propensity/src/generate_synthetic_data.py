"""Generate deterministic campaign-response data for the ML1 portfolio case."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 731
N_CUSTOMERS = 6_000
COHORT_DATES = pd.date_range("2025-09-01", periods=12, freq="MS")


def _sigmoid(values: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-values))


def generate_clean_data(
    seed: int = SEED,
    n_customers: int = N_CUSTOMERS,
    cohort_dates: pd.DatetimeIndex = COHORT_DATES,
) -> pd.DataFrame:
    """Return customer-at-campaign-cohort observations with realistic temporal drift."""
    rng = np.random.default_rng(seed)
    customers = np.arange(1, n_customers + 1)

    region = rng.choice(["NORTHEAST", "SOUTH", "MIDWEST", "WEST"], n_customers)
    preferred_channel = rng.choice(["EMAIL", "SMS", "PUSH"], n_customers, p=[0.58, 0.24, 0.18])
    latent_engagement = rng.normal(0, 1, n_customers)
    latent_value = rng.normal(0, 1, n_customers)
    discount_affinity = rng.normal(0, 1, n_customers)
    base_tenure = rng.integers(60, 2_000, n_customers)
    loyalty_score = 0.70 * latent_value + 0.35 * latent_engagement + rng.normal(0, 0.5, n_customers)
    loyalty_tier = pd.cut(
        loyalty_score,
        bins=[-np.inf, -0.35, 0.75, np.inf],
        labels=["STANDARD", "PLUS", "PREMIUM"],
    ).astype(str)

    rows: list[pd.DataFrame] = []
    for cohort_index, scoring_date in enumerate(cohort_dates):
        drift = cohort_index / max(len(cohort_dates) - 1, 1)
        seasonal = 0.24 if scoring_date.month in {11, 12} else 0.0
        engagement = latent_engagement - 0.16 * drift + rng.normal(0, 0.18, n_customers)

        recency_scale = np.exp(2.45 - 0.42 * engagement - 0.12 * latent_value)
        recency_days = np.clip(rng.gamma(2.0, recency_scale), 0, 180).round().astype(int)
        orders_lambda = np.clip(
            np.exp(0.92 + 0.38 * engagement + 0.27 * latent_value - 0.10 * drift),
            0.08,
            28,
        )
        orders_180d = rng.poisson(orders_lambda)
        average_order_value = np.clip(rng.lognormal(4.15 + 0.22 * latent_value, 0.38), 12, 650)
        spend_180d = np.clip(
            orders_180d * average_order_value * rng.lognormal(0, 0.12, n_customers),
            0,
            20_000,
        )

        email_open_rate = np.clip(
            _sigmoid(-0.55 + 1.05 * engagement + rng.normal(0, 0.7, n_customers)),
            0,
            1,
        )
        email_click_rate = np.clip(
            email_open_rate * _sigmoid(-0.95 + 0.72 * engagement + 0.22 * discount_affinity),
            0,
            1,
        )
        site_sessions_30d = rng.poisson(
            np.clip(np.exp(0.72 + 0.46 * engagement + 0.08 * seasonal), 0.05, 35)
        )
        prior_campaigns_12m = rng.integers(2, 13, n_customers)
        historical_response_probability = np.clip(
            _sigmoid(-2.05 + 0.78 * engagement + 0.44 * discount_affinity), 0.01, 0.80
        )
        prior_campaign_responses_12m = rng.binomial(
            prior_campaigns_12m, historical_response_probability
        )
        days_since_last_campaign = (
            np.clip(rng.gamma(2.2, 18 + 5 * drift, n_customers), 3, 180).round().astype(int)
        )
        discount_share_180d = np.clip(
            _sigmoid(-0.38 + 0.92 * discount_affinity + rng.normal(0, 0.55, n_customers)),
            0,
            1,
        )
        margin_rate_180d = np.clip(
            0.49 - 0.16 * discount_share_180d + rng.normal(0, 0.025, n_customers),
            0.20,
            0.62,
        )

        tenure_days = base_tenure + cohort_index * 30
        logit = -3.25
        logit += -0.010 * recency_days
        logit += 0.055 * np.minimum(orders_180d, 18)
        logit += 0.82 * email_click_rate
        logit += 0.32 * email_open_rate
        logit += 0.115 * np.sqrt(site_sessions_30d)
        logit += 0.95 * (prior_campaign_responses_12m / prior_campaigns_12m)
        logit += 0.34 * discount_share_180d
        logit += 0.24 * (loyalty_tier == "PREMIUM")
        logit += 0.12 * (preferred_channel == "EMAIL")
        logit += seasonal - 0.14 * drift
        logit += 0.22 * ((recency_days <= 21) & (email_click_rate >= 0.15))
        # Non-linear business mechanisms that a purely additive model cannot fully represent.
        logit += 0.72 * ((loyalty_tier == "PREMIUM") & (spend_180d >= 550) & (recency_days <= 45))
        logit += 0.68 * ((discount_share_180d >= 0.64) & (days_since_last_campaign >= 32))
        logit += -0.78 * ((days_since_last_campaign <= 16) & (prior_campaigns_12m >= 9))
        logit += 0.42 * ((region == "WEST") & np.isin(scoring_date.month, [11, 12]))
        response_probability = np.clip(_sigmoid(logit), 0.005, 0.80)
        responded = rng.binomial(1, response_probability)

        response_order_value = np.where(
            responded == 1,
            np.clip(average_order_value * rng.lognormal(0.05, 0.28, n_customers), 8, 900),
            0,
        )
        opened_current_campaign = rng.binomial(
            1, np.clip(0.08 + 0.82 * email_open_rate + 0.08 * responded, 0, 0.98)
        )
        clicked_current_campaign = np.where(
            opened_current_campaign == 1,
            rng.binomial(1, np.clip(0.03 + 0.70 * email_click_rate + 0.18 * responded, 0, 0.95)),
            0,
        )

        rows.append(
            pd.DataFrame(
                {
                    "customer_id": [f"HP{customer:06d}" for customer in customers],
                    "scoring_date": scoring_date.strftime("%Y-%m-%d"),
                    "campaign_id": f"RET-{scoring_date:%Y%m}",
                    "region": region,
                    "preferred_channel": preferred_channel,
                    "loyalty_tier": loyalty_tier,
                    "customer_tenure_days": tenure_days,
                    "recency_days": recency_days,
                    "orders_180d": orders_180d,
                    "spend_180d": np.round(spend_180d, 2),
                    "average_order_value_180d": np.round(average_order_value, 2),
                    "email_open_rate_90d": np.round(email_open_rate, 4),
                    "email_click_rate_90d": np.round(email_click_rate, 4),
                    "site_sessions_30d": site_sessions_30d,
                    "prior_campaigns_12m": prior_campaigns_12m,
                    "prior_campaign_responses_12m": prior_campaign_responses_12m,
                    "days_since_last_campaign": days_since_last_campaign,
                    "discount_share_180d": np.round(discount_share_180d, 4),
                    "margin_rate_180d": np.round(margin_rate_180d, 4),
                    "marketing_consent": 1,
                    "contact_suppressed": 0,
                    "responded_within_14d": responded,
                    "response_order_value_14d": np.round(response_order_value, 2),
                    "opened_current_campaign": opened_current_campaign,
                    "clicked_current_campaign": clicked_current_campaign,
                    "response_probability_generator_only": np.round(response_probability, 6),
                }
            )
        )

    return pd.concat(rows, ignore_index=True)


def generate_raw_data(
    seed: int = SEED,
    n_customers: int = N_CUSTOMERS,
    cohort_dates: pd.DatetimeIndex = COHORT_DATES,
) -> pd.DataFrame:
    """Add controlled quality defects and missingness to the clean reference data."""
    rng = np.random.default_rng(seed + 1)
    raw = generate_clean_data(seed, n_customers, cohort_dates).copy()

    for column, fraction in {
        "email_open_rate_90d": 0.025,
        "email_click_rate_90d": 0.020,
        "average_order_value_180d": 0.015,
    }.items():
        indices = rng.choice(raw.index, size=max(1, int(len(raw) * fraction)), replace=False)
        raw.loc[indices, column] = np.nan

    duplicate_count = max(4, min(60, len(raw) // 250))
    duplicates = raw.sample(duplicate_count, random_state=seed)
    raw = pd.concat([raw, duplicates], ignore_index=True)

    defect_count = max(6, min(45, len(raw) // 300))
    defect_indices = rng.choice(raw.index, size=defect_count, replace=False)
    thirds = np.array_split(defect_indices, 3)
    raw.loc[thirds[0], "region"] = raw.loc[thirds[0], "region"].str.lower()
    raw.loc[thirds[1], "recency_days"] = -3
    raw.loc[thirds[2], "customer_tenure_days"] = -10

    return raw.sample(frac=1, random_state=seed + 2).reset_index(drop=True)


def build_portfolio_sample(raw: pd.DataFrame, n: int = 3_000, seed: int = SEED) -> pd.DataFrame:
    """Return a compact review sample that retains representative quality defects."""
    if len(raw) <= n:
        return raw.copy()
    cleanish = raw.drop_duplicates(["customer_id", "scoring_date"])
    base = cleanish.sample(n=n - 30, random_state=seed).copy()
    duplicates = base.sample(10, random_state=seed + 1)
    casing = base.sample(10, random_state=seed + 2).copy()
    casing["region"] = casing["region"].str.lower()
    anomalies = base.sample(10, random_state=seed + 3).copy()
    anomalies.loc[anomalies.index[:5], "recency_days"] = -4
    anomalies.loc[anomalies.index[5:], "customer_tenure_days"] = -20
    sample = pd.concat([base, duplicates, casing, anomalies], ignore_index=True)
    return sample.sample(frac=1, random_state=seed + 4).reset_index(drop=True)


def main() -> None:
    module_root = Path(__file__).resolve().parents[1]
    raw_dir = module_root / "data" / "raw"
    processed_dir = module_root / "data" / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    clean = generate_clean_data()
    raw = generate_raw_data()
    sample = build_portfolio_sample(raw)

    clean.to_csv(processed_dir / "campaign_response_clean_reference.csv", index=False)
    raw.to_csv(raw_dir / "campaign_response_full.csv", index=False)
    sample.to_csv(raw_dir / "campaign_response_sample.csv", index=False)

    prevalence = clean.groupby("scoring_date")["responded_within_14d"].mean()
    print(f"Clean reference rows: {len(clean):,}")
    print(f"Raw rows: {len(raw):,}")
    print(f"Portfolio sample rows: {len(sample):,}")
    print(f"Response-rate range: {prevalence.min():.2%} to {prevalence.max():.2%}")


if __name__ == "__main__":
    main()
