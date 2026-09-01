"""Train, select, and evaluate the ML1 campaign-response propensity models."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

TARGET = "responded_within_14d"
ID_COLUMNS = ["customer_id", "scoring_date", "campaign_id"]
LEAKAGE_COLUMNS = [
    "response_order_value_14d",
    "opened_current_campaign",
    "clicked_current_campaign",
    "response_probability_generator_only",
]
NUMERIC_FEATURES = [
    "customer_tenure_days",
    "recency_days",
    "orders_180d",
    "spend_180d",
    "average_order_value_180d",
    "email_open_rate_90d",
    "email_click_rate_90d",
    "site_sessions_30d",
    "prior_campaigns_12m",
    "prior_campaign_responses_12m",
    "days_since_last_campaign",
    "discount_share_180d",
    "margin_rate_180d",
]
CATEGORICAL_FEATURES = ["region", "preferred_channel", "loyalty_tier"]
MODEL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
PROTECTED_OR_SENSITIVE_FEATURES = {
    "age",
    "date_of_birth",
    "gender",
    "race",
    "ethnicity",
    "religion",
    "disability",
}


@dataclass(frozen=True)
class ModelMetrics:
    roc_auc: float
    pr_auc: float
    brier: float
    log_loss: float
    precision_at_capacity: float
    recall_at_capacity: float
    lift_at_capacity: float
    captured_responders: int
    capacity: int
    population: int
    response_rate: float


def quality_report(raw: pd.DataFrame) -> dict[str, int]:
    """Summarize critical data-quality, eligibility, and leakage checks."""
    return {
        "rows": len(raw),
        "duplicate_customer_scoring_date": int(
            raw.duplicated(["customer_id", "scoring_date"]).sum()
        ),
        "negative_recency": int((pd.to_numeric(raw["recency_days"], errors="coerce") < 0).sum()),
        "invalid_tenure": int(
            (pd.to_numeric(raw["customer_tenure_days"], errors="coerce") < 30).sum()
        ),
        "missing_model_values": int(raw[MODEL_FEATURES].isna().sum().sum()),
        "ineligible_consent_rows": int((raw["marketing_consent"] != 1).sum()),
        "suppressed_rows": int((raw["contact_suppressed"] != 0).sum()),
        "leakage_columns_present": sum(column in raw.columns for column in LEAKAGE_COLUMNS),
    }


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Apply the scoring-population and feature-availability contract."""
    required = set(
        ID_COLUMNS + MODEL_FEATURES + [TARGET, "marketing_consent", "contact_suppressed"]
    )
    missing = sorted(required.difference(raw.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    clean = raw.copy()
    clean["scoring_date"] = pd.to_datetime(clean["scoring_date"], errors="coerce")
    for column in CATEGORICAL_FEATURES:
        clean[column] = clean[column].astype("string").str.strip().str.upper()
    for column in NUMERIC_FEATURES + [TARGET, "marketing_consent", "contact_suppressed"]:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")

    clean = clean.drop_duplicates(["customer_id", "scoring_date"], keep="first")
    valid = clean["scoring_date"].notna()
    valid &= clean["marketing_consent"].eq(1) & clean["contact_suppressed"].eq(0)
    valid &= clean[TARGET].isin([0, 1])
    valid &= clean["customer_tenure_days"].ge(30)
    valid &= clean["recency_days"].ge(0)
    valid &= clean["orders_180d"].ge(0)
    valid &= clean["spend_180d"].ge(0)
    valid &= clean["site_sessions_30d"].ge(0)
    clean = clean.loc[valid].sort_values(["scoring_date", "customer_id"]).reset_index(drop=True)

    if clean.empty:
        raise ValueError("No valid rows remain after applying the scoring-population contract")
    return clean


def temporal_split(clean: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Reserve the final two cohorts for test and preceding two for validation."""
    cohorts = np.array(sorted(pd.to_datetime(clean["scoring_date"]).unique()))
    if len(cohorts) < 6:
        raise ValueError("At least six scoring cohorts are required for temporal validation")
    validation_dates = set(cohorts[-4:-2])
    test_dates = set(cohorts[-2:])
    train = clean.loc[~clean["scoring_date"].isin(validation_dates | test_dates)].copy()
    validation = clean.loc[clean["scoring_date"].isin(validation_dates)].copy()
    test = clean.loc[clean["scoring_date"].isin(test_dates)].copy()
    return train, validation, test


def _preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric, NUMERIC_FEATURES),
            ("categorical", categorical, CATEGORICAL_FEATURES),
        ],
        sparse_threshold=0,
    )


def build_models(random_state: int = 42) -> dict[str, Pipeline]:
    """Return an interpretable baseline, simple tree, and stronger tree-based candidate."""
    return {
        "logistic_regression": Pipeline(
            [
                ("preprocess", _preprocessor()),
                ("model", LogisticRegression(max_iter=1_000, C=0.8, random_state=random_state)),
            ]
        ),
        "decision_tree": Pipeline(
            [
                ("preprocess", _preprocessor()),
                (
                    "model",
                    DecisionTreeClassifier(
                        max_depth=5,
                        min_samples_leaf=180,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
        "hist_gradient_boosting": Pipeline(
            [
                ("preprocess", _preprocessor()),
                (
                    "model",
                    HistGradientBoostingClassifier(
                        learning_rate=0.06,
                        max_iter=180,
                        max_leaf_nodes=15,
                        min_samples_leaf=80,
                        l2_regularization=1.2,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
    }


def business_rule_scores(frame: pd.DataFrame) -> np.ndarray:
    """Return a transparent ranking rule representing the current targeting baseline."""
    response_rate = frame["prior_campaign_responses_12m"] / frame["prior_campaigns_12m"].clip(1)
    recency_rank = 1 - frame["recency_days"].rank(pct=True)
    sessions_rank = frame["site_sessions_30d"].rank(pct=True)
    return (
        0.30 * recency_rank
        + 0.28 * frame["email_click_rate_90d"].fillna(0)
        + 0.12 * frame["email_open_rate_90d"].fillna(0)
        + 0.20 * response_rate
        + 0.10 * sessions_rank
    ).to_numpy()


def evaluate_predictions(
    target: pd.Series,
    scores: np.ndarray,
    capacity_rate: float = 0.20,
    probability_scores: bool = True,
) -> ModelMetrics:
    """Evaluate discrimination, calibration, and limited-capacity decision quality."""
    y = np.asarray(target, dtype=int)
    values = np.asarray(scores, dtype=float)
    capacity = max(1, min(len(y), int(round(len(y) * capacity_rate))))
    selected = np.argsort(-values, kind="stable")[:capacity]
    captured = int(y[selected].sum())
    positives = int(y.sum())
    response_rate = float(y.mean())
    precision = captured / capacity
    recall = captured / positives if positives else 0.0
    lift = precision / response_rate if response_rate else 0.0

    return ModelMetrics(
        roc_auc=float(roc_auc_score(y, values)),
        pr_auc=float(average_precision_score(y, values)),
        brier=float(brier_score_loss(y, values)) if probability_scores else float("nan"),
        log_loss=float(log_loss(y, values, labels=[0, 1])) if probability_scores else float("nan"),
        precision_at_capacity=float(precision),
        recall_at_capacity=float(recall),
        lift_at_capacity=float(lift),
        captured_responders=captured,
        capacity=capacity,
        population=len(y),
        response_rate=response_rate,
    )


def calibration_table(target: pd.Series, probabilities: np.ndarray) -> pd.DataFrame:
    """Summarize predicted and observed response by equal-frequency score band."""
    table = pd.DataFrame({"target": target.to_numpy(), "probability": probabilities})
    table["score_band"] = pd.qcut(table["probability"], q=10, labels=False, duplicates="drop")
    result = (
        table.groupby("score_band", observed=True)
        .agg(
            customers=("target", "size"),
            predicted_response_rate=("probability", "mean"),
            observed_response_rate=("target", "mean"),
        )
        .reset_index()
    )
    result["calibration_gap"] = result["predicted_response_rate"] - result["observed_response_rate"]
    return result


def segment_metrics(frame: pd.DataFrame, probabilities: np.ndarray, segment: str) -> pd.DataFrame:
    """Measure performance by a declared operational segment."""
    scored = frame[[segment, TARGET]].copy()
    scored["probability"] = probabilities
    rows: list[dict[str, Any]] = []
    for value, group in scored.groupby(segment, dropna=False):
        if len(group) < 200 or group[TARGET].nunique() < 2:
            continue
        rows.append(
            {
                "segment": segment,
                "value": str(value),
                "customers": len(group),
                "response_rate": group[TARGET].mean(),
                "roc_auc": roc_auc_score(group[TARGET], group["probability"]),
                "pr_auc": average_precision_score(group[TARGET], group["probability"]),
                "brier": brier_score_loss(group[TARGET], group["probability"]),
            }
        )
    return pd.DataFrame(rows)


def realized_value(
    frame: pd.DataFrame,
    scores: np.ndarray,
    capacity_rate: float = 0.20,
    contact_cost: float = 0.35,
    offer_cost_rate: float = 0.08,
) -> dict[str, float]:
    """Estimate retrospective campaign value for the selected capacity."""
    capacity = max(1, min(len(frame), int(round(len(frame) * capacity_rate))))
    selected = frame.iloc[np.argsort(-np.asarray(scores), kind="stable")[:capacity]]
    gross_margin = (selected["response_order_value_14d"] * selected["margin_rate_180d"]).sum()
    offer_cost = (selected["response_order_value_14d"] * offer_cost_rate).sum()
    net_value = gross_margin - offer_cost - capacity * contact_cost
    return {
        "capacity": capacity,
        "gross_margin_usd": float(gross_margin),
        "offer_cost_usd": float(offer_cost),
        "contact_cost_usd": float(capacity * contact_cost),
        "net_value_usd": float(net_value),
    }


def fit_and_evaluate(
    models: dict[str, Pipeline],
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
    capacity_rate: float = 0.20,
) -> dict[str, Any]:
    """Select on validation, refit without test leakage, then evaluate once on test."""
    fitted: dict[str, Pipeline] = {}
    validation_rows: list[dict[str, Any]] = []
    for name, model in models.items():
        candidate = clone(model)
        candidate.fit(train[MODEL_FEATURES], train[TARGET])
        probabilities = candidate.predict_proba(validation[MODEL_FEATURES])[:, 1]
        metrics = evaluate_predictions(
            validation[TARGET], probabilities, capacity_rate=capacity_rate
        )
        fitted[name] = candidate
        validation_rows.append({"model": name, **asdict(metrics)})

    validation_table = pd.DataFrame(validation_rows).set_index("model")
    selected_name = validation_table.sort_values(
        ["pr_auc", "brier"], ascending=[False, True]
    ).index[0]
    development = pd.concat([train, validation], ignore_index=True)
    champion = clone(models[selected_name])
    champion.fit(development[MODEL_FEATURES], development[TARGET])
    test_probabilities = champion.predict_proba(test[MODEL_FEATURES])[:, 1]
    test_metrics = evaluate_predictions(
        test[TARGET], test_probabilities, capacity_rate=capacity_rate
    )
    rule_scores = business_rule_scores(test)
    rule_metrics = evaluate_predictions(
        test[TARGET], rule_scores, capacity_rate=capacity_rate, probability_scores=False
    )

    importance_sample = test.sample(min(4_000, len(test)), random_state=42)
    importance = permutation_importance(
        champion,
        importance_sample[MODEL_FEATURES],
        importance_sample[TARGET],
        scoring="average_precision",
        n_repeats=4,
        random_state=42,
        n_jobs=1,
    )
    importance_table = pd.DataFrame(
        {
            "feature": MODEL_FEATURES,
            "importance_mean": importance.importances_mean,
            "importance_std": importance.importances_std,
        }
    ).sort_values("importance_mean", ascending=False)

    return {
        "selected_name": selected_name,
        "champion": champion,
        "validation_table": validation_table,
        "test_probabilities": test_probabilities,
        "test_metrics": test_metrics,
        "rule_scores": rule_scores,
        "rule_metrics": rule_metrics,
        "calibration_table": calibration_table(test[TARGET], test_probabilities),
        "segment_table": pd.concat(
            [
                segment_metrics(test, test_probabilities, "loyalty_tier"),
                segment_metrics(test, test_probabilities, "region"),
            ],
            ignore_index=True,
        ),
        "importance_table": importance_table,
        "champion_value": realized_value(test, test_probabilities, capacity_rate),
        "rule_value": realized_value(test, rule_scores, capacity_rate),
    }


def run_workflow(raw: pd.DataFrame) -> dict[str, Any]:
    """Run the complete quality, split, model-selection, and evaluation workflow."""
    report = quality_report(raw)
    clean = clean_data(raw)
    train, validation, test = temporal_split(clean)
    results = fit_and_evaluate(build_models(), train, validation, test)
    results.update(
        {
            "quality_report": report,
            "clean_rows": len(clean),
            "train_rows": len(train),
            "validation_rows": len(validation),
            "test_rows": len(test),
            "train_cohorts": sorted(train["scoring_date"].dt.strftime("%Y-%m-%d").unique()),
            "validation_cohorts": sorted(
                validation["scoring_date"].dt.strftime("%Y-%m-%d").unique()
            ),
            "test_cohorts": sorted(test["scoring_date"].dt.strftime("%Y-%m-%d").unique()),
        }
    )
    return results


def _json_ready(results: dict[str, Any]) -> dict[str, Any]:
    def metric_dict(metrics: ModelMetrics) -> dict[str, Any]:
        return {
            key: None if isinstance(value, float) and np.isnan(value) else value
            for key, value in asdict(metrics).items()
        }

    return {
        "selected_model": results["selected_name"],
        "quality_report": results["quality_report"],
        "rows": {
            "clean": results["clean_rows"],
            "train": results["train_rows"],
            "validation": results["validation_rows"],
            "test": results["test_rows"],
        },
        "cohorts": {
            "train": results["train_cohorts"],
            "validation": results["validation_cohorts"],
            "test": results["test_cohorts"],
        },
        "test_metrics": metric_dict(results["test_metrics"]),
        "rule_test_metrics": metric_dict(results["rule_metrics"]),
        "champion_value": results["champion_value"],
        "rule_value": results["rule_value"],
    }


def main() -> None:
    module_root = Path(__file__).resolve().parents[1]
    raw_path = module_root / "data" / "raw" / "campaign_response_full.csv"
    output_dir = module_root / "data" / "processed"
    report_dir = module_root / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    if not raw_path.exists():
        raise FileNotFoundError(
            f"{raw_path} does not exist. Run src/generate_synthetic_data.py first."
        )

    results = run_workflow(pd.read_csv(raw_path))
    results["validation_table"].to_csv(output_dir / "validation_model_comparison.csv")
    results["calibration_table"].to_csv(output_dir / "test_calibration.csv", index=False)
    results["segment_table"].to_csv(output_dir / "test_segment_metrics.csv", index=False)
    results["importance_table"].to_csv(output_dir / "permutation_importance.csv", index=False)
    (report_dir / "reference_results.json").write_text(
        json.dumps(_json_ready(results), indent=2, allow_nan=False), encoding="utf-8"
    )

    print(f"Selected model: {results['selected_name']}")
    print(results["validation_table"].round(4))
    print("Test metrics:")
    print(json.dumps(asdict(results["test_metrics"]), indent=2))
    print("Rule baseline metrics:")
    print(json.dumps(asdict(results["rule_metrics"]), indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
