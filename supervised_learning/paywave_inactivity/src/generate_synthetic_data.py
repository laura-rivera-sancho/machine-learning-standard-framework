from pathlib import Path

import numpy as np
import pandas as pd

SEED = 126
SCORING_DATES = pd.to_datetime(
    [
        "2026-01-05",
        "2026-02-02",
        "2026-03-02",
        "2026-04-06",
        "2026-05-04",
        "2026-06-01",
        "2026-07-06",
        "2026-08-03",
    ]
)
N_CUSTOMERS = 30_000


def _sigmoid(x):
    return 1 / (1 + np.exp(-x))


def generate_clean_data(seed=SEED):
    """Generate customer-at-scoring-date synthetic history for inactivity prediction."""
    rng = np.random.default_rng(seed)
    customers = np.arange(1, N_CUSTOMERS + 1)

    # Stable customer attributes.
    country = rng.choice(["US", "MX", "CR", "BR"], size=N_CUSTOMERS, p=[0.48, 0.22, 0.10, 0.20])
    device = rng.choice(["Mobile", "Desktop"], size=N_CUSTOMERS, p=[0.72, 0.28])
    base_tenure = rng.integers(90, 1800, size=N_CUSTOMERS)
    latent_engagement = rng.normal(0, 1, size=N_CUSTOMERS)
    latent_value = rng.normal(0, 1, size=N_CUSTOMERS)

    rows = []

    for cohort_idx, scoring_date in enumerate(SCORING_DATES):
        # Mild temporal drift: slightly lower engagement and higher inactivity prevalence later.
        drift = cohort_idx * 0.08
        cohort_noise = rng.normal(0, 0.15, size=N_CUSTOMERS)
        engagement = latent_engagement - drift + cohort_noise

        tenure = base_tenure + cohort_idx * 28
        eligible = tenure >= 90

        # Recency is non-linear and tied to latent engagement.
        recency_scale = np.exp(1.85 - 0.42 * engagement + 0.06 * drift)
        days_since_last = np.clip(rng.gamma(shape=2.0, scale=recency_scale), 0, 120).astype(int)

        # Frequency features are correlated but not identical.
        txn60_lambda = np.clip(
            np.exp(1.55 + 0.38 * engagement + 0.20 * latent_value - 0.10 * drift), 0.2, 30
        )
        tx60 = rng.poisson(txn60_lambda)
        tx60 = np.maximum(tx60, 1)  # eligibility requires at least one prior-60d transaction

        recent_share = np.clip(
            0.48 + 0.10 * engagement - 0.05 * drift + rng.normal(0, 0.08, N_CUSTOMERS), 0.08, 0.85
        )
        tx30 = np.minimum(tx60, rng.binomial(tx60, recent_share))
        tx7_prob = np.clip(0.23 + 0.06 * engagement - 0.03 * drift, 0.03, 0.55)
        tx7 = np.minimum(tx30, rng.binomial(tx30, tx7_prob))

        active_days = np.minimum(
            30, np.maximum(1, tx30 - rng.poisson(np.maximum(tx30 * 0.18, 0.2)))
        )
        login_days = np.clip(
            (4 + 2.2 * engagement + 0.45 * active_days + rng.normal(0, 3, N_CUSTOMERS)).round(),
            0,
            30,
        ).astype(int)
        products_used = np.clip(
            (
                1.8 + 0.45 * engagement + 0.35 * latent_value + rng.normal(0, 0.7, N_CUSTOMERS)
            ).round(),
            1,
            6,
        ).astype(int)

        avg_value = np.clip(
            rng.lognormal(mean=np.log(55 + 14 * np.maximum(latent_value, -1.5)), sigma=0.55),
            5,
            1200,
        )
        payment_volume = np.clip(
            avg_value * np.maximum(tx30, 1) * rng.lognormal(0, 0.18, N_CUSTOMERS), 0, 25_000
        )

        # Behavioral decline relative to prior 30 days.
        prior30 = np.maximum(
            1,
            (tx30 / np.clip(0.95 + 0.12 * engagement + rng.normal(0, 0.18, N_CUSTOMERS), 0.35, 1.7))
            .round()
            .astype(int),
        )
        count_change = (tx30 - prior30) / prior30
        prior_volume = np.maximum(
            10,
            payment_volume
            / np.clip(0.96 + 0.10 * engagement + rng.normal(0, 0.20, N_CUSTOMERS), 0.35, 1.8),
        )
        volume_change = (payment_volume - prior_volume) / prior_volume

        failed = rng.poisson(
            np.clip(0.35 + 0.08 * tx30 + np.where(country == "BR", 0.15, 0), 0.05, 6)
        )
        support = rng.poisson(
            np.clip(0.22 + 0.09 * failed + np.where(engagement < -0.8, 0.20, 0), 0.02, 4)
        )
        marketing = np.clip(
            _sigmoid(
                0.9 * engagement
                + 0.18 * login_days
                - 0.10 * days_since_last
                + rng.normal(0, 0.7, N_CUSTOMERS)
            ),
            0,
            1,
        )

        value_score = 0.55 * latent_value + 0.03 * tx30 + 0.0015 * payment_volume
        value_tier = pd.cut(
            value_score, bins=[-np.inf, 0.0, 1.2, np.inf], labels=["Low", "Medium", "High"]
        ).astype(str)

        # Target risk combines recency and decline effects, engagement protection,
        # segment differences, and mild temporal drift.
        logit = -2.15
        logit += 0.055 * days_since_last
        logit += 0.62 * (count_change < -0.35)
        logit += 0.45 * (volume_change < -0.40)
        logit += -0.055 * login_days
        logit += -0.22 * products_used
        logit += -0.018 * np.minimum(tx30, 20)
        logit += 0.17 * failed
        logit += 0.12 * support
        logit += 0.22 * (country == "BR")
        logit += 0.10 * (country == "MX")
        logit += 0.20 * (tenure < 240)
        logit += 0.20 * drift
        logit += 0.45 * (days_since_last > 28)
        logit += 0.35 * ((days_since_last > 18) & (tx30 <= 2))

        inactivity_prob = np.clip(_sigmoid(logit), 0.01, 0.92)
        target = rng.binomial(1, inactivity_prob)

        # Future outcome fields are included deliberately as leakage candidates.
        future_txn_lambda = np.where(
            target == 1, 0.0, np.clip(2.0 + 0.22 * tx30 + 0.6 * engagement, 0.3, 15)
        )
        future_txn = np.where(target == 1, 0, np.maximum(1, rng.poisson(future_txn_lambda)))
        future_status = np.where(target == 1, "Inactive", "Active")
        retention_case = rng.binomial(
            1, np.clip(0.08 + 0.66 * target + 0.10 * (days_since_last > 20), 0, 0.95)
        )

        frame = pd.DataFrame(
            {
                "customer_id": [f"PW{c:06d}" for c in customers],
                "scoring_date": scoring_date.strftime("%Y-%m-%d"),
                "country": country,
                "device_type": device,
                "customer_tenure_days": tenure,
                "customer_value_tier": value_tier,
                "days_since_last_transaction": days_since_last,
                "transactions_7d": tx7,
                "transactions_30d": tx30,
                "transactions_60d": tx60,
                "active_days_30d": active_days,
                "payment_volume_30d_usd": np.round(payment_volume, 2),
                "avg_transaction_value_30d": np.round(avg_value, 2),
                "transaction_count_change_30d_vs_prior30d": np.round(count_change, 4),
                "payment_volume_change_30d_vs_prior30d": np.round(volume_change, 4),
                "failed_transactions_30d": failed,
                "support_contacts_30d": support,
                "login_days_30d": login_days,
                "products_used_60d": products_used,
                "marketing_engagement_30d": np.round(marketing, 4),
                "inactive_next_30d": target,
                "transactions_next_30d": future_txn,
                "future_inactivity_status": future_status,
                "retention_case_opened_after_score": retention_case,
            }
        )
        rows.append(frame.loc[eligible])

    return pd.concat(rows, ignore_index=True)


def generate_raw_data(seed=SEED):
    """Add deliberate data-quality defects and realistic missingness."""
    rng = np.random.default_rng(seed + 1)
    clean = generate_clean_data(seed)
    raw = clean.copy()

    # Missing values in selected valid features.
    for col, frac in {
        "marketing_engagement_30d": 0.035,
        "payment_volume_change_30d_vs_prior30d": 0.020,
        "avg_transaction_value_30d": 0.012,
    }.items():
        idx = rng.choice(raw.index, size=int(len(raw) * frac), replace=False)
        raw.loc[idx, col] = np.nan

    # Duplicates.
    dupes = raw.sample(45, random_state=seed)
    raw = pd.concat([raw, dupes], ignore_index=True)

    # Casing defects.
    idx = rng.choice(raw.index, size=40, replace=False)
    raw.loc[idx, "country"] = raw.loc[idx, "country"].str.lower()

    # Impossible values in a small number of rows.
    idx = rng.choice(raw.index, size=18, replace=False)
    raw.loc[idx[:6], "days_since_last_transaction"] = -3
    raw.loc[idx[6:12], "transactions_30d"] = -1
    raw.loc[idx[12:], "customer_tenure_days"] = -20

    return raw.sample(frac=1, random_state=seed + 2).reset_index(drop=True)


def build_training_sample(raw, n=2500, seed=SEED):
    """Create a compact portfolio sample preserving the main learning features."""
    base = (
        raw.drop_duplicates(["customer_id", "scoring_date"])
        .sample(n=n - 30, random_state=seed)
        .copy()
    )
    duplicates = base.sample(10, random_state=seed + 1)
    casing = base.sample(10, random_state=seed + 2).copy()
    casing["country"] = casing["country"].astype(str).str.lower()
    anomalies = base.sample(10, random_state=seed + 3).copy()
    anomalies.loc[anomalies.index[:4], "days_since_last_transaction"] = -4
    anomalies.loc[anomalies.index[4:7], "transactions_30d"] = -1
    anomalies.loc[anomalies.index[7:], "customer_tenure_days"] = -10
    sample = pd.concat([base, duplicates, casing, anomalies], ignore_index=True)
    return sample.sample(frac=1, random_state=seed + 4).reset_index(drop=True)


def main():
    module_root = Path(__file__).resolve().parents[1]
    raw_dir = module_root / "data" / "raw"
    processed_dir = module_root / "data" / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    clean = generate_clean_data()
    raw = generate_raw_data()
    sample = build_training_sample(raw)

    clean.to_csv(processed_dir / "paywave_inactivity_clean_reference.csv", index=False)
    raw.to_csv(raw_dir / "paywave_inactivity_full.csv", index=False)
    sample.to_csv(raw_dir / "paywave_inactivity_sample.csv", index=False)

    print(f"Clean reference rows: {len(clean):,}")
    print(f"Raw training rows: {len(raw):,}")
    print(f"Portfolio sample rows: {len(sample):,}")
    print("Target prevalence by cohort:")
    print(clean.groupby("scoring_date")["inactive_next_30d"].mean().round(4))


if __name__ == "__main__":
    main()
