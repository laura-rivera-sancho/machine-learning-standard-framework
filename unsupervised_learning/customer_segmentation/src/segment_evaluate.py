"""Clean, compare, and evaluate customer-segmentation candidates."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.mixture import GaussianMixture
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

MODULE = Path(__file__).resolve().parents[1]
RAW_PATH = MODULE / "data" / "raw" / "customer_snapshots.csv"
PROCESSED_PATH = MODULE / "data" / "processed" / "segmented_customers.csv"
RESULTS_PATH = MODULE / "reports" / "reference_results.json"

FEATURES = [
    "recency_days",
    "frequency_12m",
    "monetary_12m",
    "avg_order_value",
    "discount_order_share",
    "email_engagement_rate",
    "digital_order_share",
    "return_rate",
    "tenure_days",
]
LOG_FEATURES = [
    "recency_days",
    "frequency_12m",
    "monetary_12m",
    "avg_order_value",
    "tenure_days",
]
RATE_FEATURES = [feature for feature in FEATURES if feature not in LOG_FEATURES]


@dataclass(frozen=True)
class CandidateMetrics:
    model: str
    clusters: int
    silhouette: float
    calinski_harabasz: float
    davies_bouldin: float
    stability_ari: float
    coverage: float
    smallest_segment_share: float


def quality_report(data: pd.DataFrame) -> dict[str, int]:
    return {
        "duplicate_customer_snapshot": int(data.duplicated(["customer_id", "snapshot_date"]).sum()),
        "negative_recency": int(data["recency_days"].lt(0).sum()),
        "invalid_rates": int(
            sum((data[col].lt(0) | data[col].gt(1)).sum() for col in RATE_FEATURES)
        ),
        "missing_feature_values": int(data[FEATURES].isna().sum().sum()),
    }


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    clean = data.copy()
    clean["snapshot_date"] = pd.to_datetime(clean["snapshot_date"])
    clean = clean.drop_duplicates(["customer_id", "snapshot_date"], keep="first")
    clean = clean[clean["recency_days"].ge(0)]
    for column in RATE_FEATURES:
        clean = clean[clean[column].between(0, 1)]
    return clean.sort_values(["snapshot_date", "customer_id"]).reset_index(drop=True)


def feature_pipeline() -> ColumnTransformer:
    log_pipe = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("log", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
            ("scale", StandardScaler()),
        ]
    )
    rate_pipe = Pipeline(
        [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    )
    return ColumnTransformer([("log", log_pipe, LOG_FEATURES), ("rate", rate_pipe, RATE_FEATURES)])


def _bootstrap_stability(
    x: np.ndarray, model_name: str, n_clusters: int, seed: int, repeats: int = 5
) -> float:
    rng = np.random.default_rng(seed)
    labelings = []
    for repeat in range(repeats):
        idx = rng.choice(len(x), len(x), replace=True)
        if model_name == "kmeans":
            model = KMeans(n_clusters=n_clusters, n_init=20, random_state=seed + repeat)
            model.fit(x[idx])
            labels = model.predict(x)
        else:
            model = GaussianMixture(
                n_components=n_clusters,
                covariance_type="full",
                reg_covar=1e-5,
                random_state=seed + repeat,
                n_init=3,
            )
            model.fit(x[idx])
            labels = model.predict(x)
        labelings.append(labels)
    scores = [
        adjusted_rand_score(labelings[i], labelings[j])
        for i in range(len(labelings))
        for j in range(i + 1, len(labelings))
    ]
    return float(np.mean(scores))


def _metrics(model: str, labels: np.ndarray, x: np.ndarray, stability: float) -> CandidateMetrics:
    usable = labels >= 0
    counts = pd.Series(labels[usable]).value_counts(normalize=True)
    return CandidateMetrics(
        model=model,
        clusters=int(pd.Series(labels[usable]).nunique()),
        silhouette=float(silhouette_score(x[usable], labels[usable])),
        calinski_harabasz=float(calinski_harabasz_score(x[usable], labels[usable])),
        davies_bouldin=float(davies_bouldin_score(x[usable], labels[usable])),
        stability_ari=stability,
        coverage=float(usable.mean()),
        smallest_segment_share=float(counts.min() * usable.mean()),
    )


def compare_candidates(x: np.ndarray, seed: int = 42) -> pd.DataFrame:
    rows: list[CandidateMetrics] = []
    for clusters in range(4, 8):
        for name in ("kmeans", "gaussian_mixture"):
            if name == "kmeans":
                model = KMeans(n_clusters=clusters, n_init=30, random_state=seed)
            else:
                model = GaussianMixture(
                    n_components=clusters,
                    covariance_type="full",
                    reg_covar=1e-5,
                    random_state=seed,
                    n_init=5,
                )
            labels = model.fit_predict(x)
            stability = _bootstrap_stability(x, name, clusters, seed)
            rows.append(_metrics(f"{name}_{clusters}", labels, x, stability))

    for eps in (0.8, 1.0, 1.2, 1.4):
        labels = DBSCAN(eps=eps, min_samples=25).fit_predict(x)
        usable = labels >= 0
        if pd.Series(labels[usable]).nunique() >= 2 and usable.mean() >= 0.65:
            jitter = x + np.random.default_rng(seed).normal(0, 0.02, x.shape)
            jittered = DBSCAN(eps=eps, min_samples=25).fit_predict(jitter)
            common = (labels >= 0) & (jittered >= 0)
            stability = adjusted_rand_score(labels[common], jittered[common])
            rows.append(_metrics(f"dbscan_eps_{eps:.1f}", labels, x, stability))
    return pd.DataFrame([row.__dict__ for row in rows]).set_index("model")


def select_candidate(comparison: pd.DataFrame) -> str:
    eligible = comparison[
        (comparison["coverage"] >= 0.90)
        & (comparison["smallest_segment_share"] >= 0.05)
        & (comparison["stability_ari"] >= 0.75)
    ].copy()
    if eligible.empty:
        eligible = comparison.copy()
    eligible["selection_score"] = (
        eligible["silhouette"].rank(pct=True)
        + eligible["stability_ari"].rank(pct=True)
        + eligible["smallest_segment_share"].rank(pct=True)
        - eligible["davies_bouldin"].rank(pct=True)
    )
    return str(eligible["selection_score"].idxmax())


def _fit_named(name: str, x: np.ndarray, seed: int = 42):
    if name.startswith("kmeans"):
        model = KMeans(n_clusters=int(name.rsplit("_", 1)[1]), n_init=30, random_state=seed)
    elif name.startswith("gaussian_mixture"):
        model = GaussianMixture(
            n_components=int(name.rsplit("_", 1)[1]),
            covariance_type="full",
            reg_covar=1e-5,
            random_state=seed,
            n_init=5,
        )
    else:
        model = DBSCAN(eps=float(name.rsplit("_", 1)[1]), min_samples=25)
    return model.fit(x)


def name_segments(profile: pd.DataFrame) -> dict[int, str]:
    remaining = set(profile.index.astype(int))
    names: dict[int, str] = {}
    rules = [
        (
            "Champions",
            profile["monetary_12m"].rank(pct=True) - profile["recency_days"].rank(pct=True),
        ),
        ("At Risk", profile["recency_days"].rank(pct=True) + profile["tenure_days"].rank(pct=True)),
        ("Deal Seekers", profile["discount_order_share"].rank(pct=True)),
        (
            "Digital Growth",
            profile["digital_order_share"].rank(pct=True)
            + profile["email_engagement_rate"].rank(pct=True),
        ),
        (
            "Loyal Core",
            profile["frequency_12m"].rank(pct=True) + profile["tenure_days"].rank(pct=True),
        ),
        ("Occasional", -profile["frequency_12m"].rank(pct=True)),
        ("Emerging", -profile["tenure_days"].rank(pct=True)),
    ]
    for label, score in rules:
        if not remaining:
            break
        chosen = int(score.loc[list(remaining)].idxmax())
        names[chosen] = label
        remaining.remove(chosen)
    return names


def run_analysis(data: pd.DataFrame, seed: int = 42) -> dict:
    clean = clean_data(data)
    current_date = clean["snapshot_date"].max()
    current = clean[clean["snapshot_date"].eq(current_date)].copy()
    prior = clean[clean["snapshot_date"].lt(current_date)].copy()

    pipeline = feature_pipeline()
    x_current = pipeline.fit_transform(current[FEATURES])
    comparison = compare_candidates(x_current, seed)
    selected_name = select_candidate(comparison)
    selected = _fit_named(selected_name, x_current, seed)
    current_labels = (
        selected.labels_ if selected_name.startswith("dbscan") else selected.predict(x_current)
    )
    current["cluster_id"] = current_labels

    profile = current[current["cluster_id"].ge(0)].groupby("cluster_id")[FEATURES].mean()
    names = name_segments(profile)
    current["segment"] = current["cluster_id"].map(names).fillna("Unassigned")
    profile.insert(0, "segment", pd.Series(names))
    profile["customers"] = current.groupby("cluster_id").size()
    profile["customer_share"] = profile["customers"] / len(current)

    x_prior = pipeline.transform(prior[FEATURES])
    prior_labels = (
        selected.labels_ if selected_name.startswith("dbscan") else selected.predict(x_prior)
    )
    common = current[["customer_id", "cluster_id"]].merge(
        pd.DataFrame({"customer_id": prior["customer_id"], "prior_cluster": prior_labels}),
        on="customer_id",
    )
    temporal_ari = adjusted_rand_score(common["cluster_id"], common["prior_cluster"])

    truth_ari = adjusted_rand_score(current["synthetic_profile_truth"], current["cluster_id"])
    return {
        "clean": clean,
        "current": current,
        "comparison": comparison,
        "selected_name": selected_name,
        "profile": profile.sort_values("customer_share", ascending=False),
        "temporal_ari": float(temporal_ari),
        "truth_ari": float(truth_ari),
        "quality": quality_report(data),
    }


def _json_safe(results: dict) -> dict:
    selected = results["comparison"].loc[results["selected_name"]]
    return {
        "selected_model": results["selected_name"],
        "selected_metrics": {key: float(value) for key, value in selected.items()},
        "temporal_assignment_ari": results["temporal_ari"],
        "synthetic_truth_ari_diagnostic": results["truth_ari"],
        "customers_segmented": int(len(results["current"])),
        "segment_profiles": results["profile"].reset_index().to_dict(orient="records"),
        "candidate_comparison": results["comparison"].reset_index().to_dict(orient="records"),
        "data_quality_before_cleaning": results["quality"],
    }


def main() -> None:
    data = pd.read_csv(RAW_PATH, parse_dates=["snapshot_date"])
    results = run_analysis(data)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    results["current"].to_csv(PROCESSED_PATH, index=False)
    RESULTS_PATH.write_text(json.dumps(_json_safe(results), indent=2), encoding="utf-8")
    print(json.dumps(_json_safe(results), indent=2))


if __name__ == "__main__":
    main()
