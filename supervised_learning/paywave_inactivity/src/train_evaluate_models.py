from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

TARGET = "inactive_next_30d"
LEAKAGE_COLUMNS = [
    "transactions_next_30d",
    "future_inactivity_status",
    "retention_case_opened_after_score",
]
ID_COLUMNS = ["customer_id", "scoring_date"]
CATEGORICAL_COLUMNS = ["country", "device_type", "customer_value_tier"]
NUMERIC_COLUMNS = [
    "customer_tenure_days",
    "days_since_last_transaction",
    "transactions_7d",
    "transactions_30d",
    "transactions_60d",
    "active_days_30d",
    "payment_volume_30d_usd",
    "avg_transaction_value_30d",
    "transaction_count_change_30d_vs_prior30d",
    "payment_volume_change_30d_vs_prior30d",
    "failed_transactions_30d",
    "support_contacts_30d",
    "login_days_30d",
    "products_used_60d",
    "marketing_engagement_30d",
]
FEATURE_COLUMNS = CATEGORICAL_COLUMNS + NUMERIC_COLUMNS
OUTREACH_CAPACITY = 5_000


@dataclass
class RankingMetrics:
    roc_auc: float
    pr_auc: float
    brier: float
    precision_at_k: float
    recall_at_k: float
    lift_at_k: float
    captured_positives: int
    k: int


def quality_report(df):
    dates = pd.to_datetime(df["scoring_date"], errors="coerce")
    report = {
        "rows": len(df),
        "duplicate_customer_scoring_date": int(
            df.duplicated(["customer_id", "scoring_date"]).sum()
        ),
        "missing_scoring_date": int(dates.isna().sum()),
        "invalid_target": int((~df[TARGET].isin([0, 1]) & df[TARGET].notna()).sum()),
        "lowercase_country_values": int(df["country"].astype(str).str.fullmatch(r"[a-z]{2}").sum()),
        "negative_recency": int(
            (pd.to_numeric(df["days_since_last_transaction"], errors="coerce") < 0).sum()
        ),
        "negative_txn30": int((pd.to_numeric(df["transactions_30d"], errors="coerce") < 0).sum()),
        "negative_tenure": int(
            (pd.to_numeric(df["customer_tenure_days"], errors="coerce") < 0).sum()
        ),
        "leakage_columns_present": sum(col in df.columns for col in LEAKAGE_COLUMNS),
    }
    return report


def clean_data(df):
    out = df.copy()
    out["scoring_date"] = pd.to_datetime(out["scoring_date"], errors="coerce")
    out = out.dropna(subset=["customer_id", "scoring_date", TARGET]).copy()
    out = out.drop_duplicates(["customer_id", "scoring_date"], keep="first")
    out["country"] = out["country"].astype(str).str.upper()

    # Exclude impossible values rather than silently treating them as real behavior.
    valid = (
        out["days_since_last_transaction"].ge(0)
        & out["transactions_30d"].ge(0)
        & out["transactions_60d"].ge(1)
        & out["customer_tenure_days"].ge(90)
    )
    out = out.loc[valid].copy()
    return out.sort_values(["scoring_date", "customer_id"]).reset_index(drop=True)


def temporal_split(df):
    """Train on Jan-May, validate on Jun-Jul, test on Aug."""
    train = df[df["scoring_date"] <= pd.Timestamp("2026-05-04")].copy()
    validation = df[
        df["scoring_date"].between(pd.Timestamp("2026-06-01"), pd.Timestamp("2026-07-06"))
    ].copy()
    test = df[df["scoring_date"] >= pd.Timestamp("2026-08-03")].copy()
    return train, validation, test


def _linear_preprocessor():
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        [
            ("num", numeric, NUMERIC_COLUMNS),
            ("cat", categorical, CATEGORICAL_COLUMNS),
        ]
    )


def _tree_preprocessor():
    numeric = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
        ]
    )
    return ColumnTransformer(
        [
            ("num", numeric, NUMERIC_COLUMNS),
            ("cat", categorical, CATEGORICAL_COLUMNS),
        ]
    )


def build_models(random_state=42):
    return {
        "logistic_regression": Pipeline(
            [
                ("prep", _linear_preprocessor()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=1500, class_weight="balanced", random_state=random_state
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("prep", _tree_preprocessor()),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=250,
                        max_depth=12,
                        min_samples_leaf=20,
                        class_weight="balanced_subsample",
                        n_jobs=-1,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
        "gradient_boosting": Pipeline(
            [
                ("prep", _tree_preprocessor()),
                (
                    "model",
                    HistGradientBoostingClassifier(
                        learning_rate=0.07,
                        max_iter=220,
                        max_leaf_nodes=24,
                        l2_regularization=1.0,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
    }


def top_k_metrics(y_true, scores, k=OUTREACH_CAPACITY):
    y = np.asarray(y_true)
    scores = np.asarray(scores)
    k = min(k, len(y))
    order = np.argsort(-scores)[:k]
    selected = y[order]
    prevalence = y.mean()
    precision_k = selected.mean() if k else np.nan
    recall_k = selected.sum() / y.sum() if y.sum() else np.nan
    lift_k = precision_k / prevalence if prevalence else np.nan
    return precision_k, recall_k, lift_k, int(selected.sum()), k


def evaluate_predictions(y_true, scores, k=OUTREACH_CAPACITY, probability_scores=True):
    precision_k, recall_k, lift_k, captured, actual_k = top_k_metrics(y_true, scores, k)
    return RankingMetrics(
        roc_auc=float(roc_auc_score(y_true, scores)),
        pr_auc=float(average_precision_score(y_true, scores)),
        # Brier loss is defined only for probability estimates in [0, 1].
        # The business-rule baseline is an uncalibrated ranking score, so its
        # calibration is intentionally reported as not applicable.
        brier=float(brier_score_loss(y_true, scores)) if probability_scores else np.nan,
        precision_at_k=float(precision_k),
        recall_at_k=float(recall_k),
        lift_at_k=float(lift_k),
        captured_positives=captured,
        k=actual_k,
    )


def business_rule_scores(df):
    """Simple recency/decline rule used as an operational baseline."""
    recency = np.clip(df["days_since_last_transaction"].to_numpy() / 60, 0, 2)
    decline = np.clip(-df["transaction_count_change_30d_vs_prior30d"].fillna(0).to_numpy(), 0, 2)
    low_frequency = 1 / (1 + df["transactions_30d"].to_numpy())
    return recency + 0.6 * decline + 0.5 * low_frequency


def fit_and_score(models, train, validation, test):
    x_train, y_train = train[FEATURE_COLUMNS], train[TARGET]
    x_val, y_val = validation[FEATURE_COLUMNS], validation[TARGET]
    x_test, y_test = test[FEATURE_COLUMNS], test[TARGET]

    validation_rows = []
    # Validation spans two scoring cycles. Aggregate the capacity available in
    # both cycles so its top-k policy is comparable with 5,000 contacts per cycle.
    validation_k = OUTREACH_CAPACITY * validation["scoring_date"].nunique()
    fitted = {}
    for name, model in models.items():
        model.fit(x_train, y_train)
        fitted[name] = model
        scores = model.predict_proba(x_val)[:, 1]
        metrics = evaluate_predictions(y_val, scores, k=validation_k)
        validation_rows.append({"model": name, **metrics.__dict__})

    rule_metrics = evaluate_predictions(
        y_val,
        business_rule_scores(validation),
        k=validation_k,
        probability_scores=False,
    )
    validation_rows.append({"model": "recency_business_rule", **rule_metrics.__dict__})
    validation_table = (
        pd.DataFrame(validation_rows).set_index("model").sort_values("pr_auc", ascending=False)
    )

    # Select model using validation PR AUC, with top-k lift and calibration reviewed alongside it.
    candidate_names = [name for name in validation_table.index if name in fitted]
    selected_name = validation_table.loc[candidate_names, "pr_auc"].idxmax()
    selected = fitted[selected_name]

    test_scores = selected.predict_proba(x_test)[:, 1]
    test_metrics = evaluate_predictions(y_test, test_scores)
    rule_test = evaluate_predictions(
        y_test,
        business_rule_scores(test),
        probability_scores=False,
    )

    return {
        "models": fitted,
        "selected_name": selected_name,
        "selected_model": selected,
        "validation_table": validation_table,
        "test_scores": test_scores,
        "test_metrics": test_metrics,
        "rule_test_metrics": rule_test,
    }


def segment_metrics(df, scores, segment):
    work = df[[segment, TARGET]].copy()
    work["score"] = scores
    rows = []
    for value, group in work.groupby(segment, dropna=False):
        if group[TARGET].nunique() < 2:
            continue
        rows.append(
            {
                "segment": value,
                "n": len(group),
                "prevalence": group[TARGET].mean(),
                "roc_auc": roc_auc_score(group[TARGET], group["score"]),
                "pr_auc": average_precision_score(group[TARGET], group["score"]),
                "brier": brier_score_loss(group[TARGET], group["score"]),
            }
        )
    return pd.DataFrame(rows).set_index("segment")


def threshold_metrics(y_true, scores, threshold):
    pred = (np.asarray(scores) >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
    return {
        "threshold": threshold,
        "precision": precision_score(y_true, pred, zero_division=0),
        "recall": recall_score(y_true, pred, zero_division=0),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def estimate_business_value(
    metrics, intervention_success_rate=0.18, retained_value=85.0, contact_cost=2.5
):
    """Illustrative economics for the selected top-k outreach list."""
    expected_saves = metrics.captured_positives * intervention_success_rate
    retained_value_total = expected_saves * retained_value
    outreach_cost = metrics.k * contact_cost
    return {
        "targeted_customers": metrics.k,
        "expected_inactive_captured": metrics.captured_positives,
        "expected_successful_saves": expected_saves,
        "expected_retained_value_usd": retained_value_total,
        "outreach_cost_usd": outreach_cost,
        "illustrative_net_value_usd": retained_value_total - outreach_cost,
    }


def main():
    module_root = Path(__file__).resolve().parents[1]
    path = module_root / "data" / "raw" / "paywave_inactivity_full.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist. Run src/generate_synthetic_data.py first.")

    raw = pd.read_csv(path)
    print("DATA QUALITY")
    print(pd.Series(quality_report(raw)))

    df = clean_data(raw)
    train, validation, test = temporal_split(df)

    print("\nTEMPORAL SPLIT")
    for name, part in [("Train", train), ("Validation", validation), ("Test", test)]:
        print(
            name,
            len(part),
            part.scoring_date.min().date(),
            part.scoring_date.max().date(),
            "prevalence",
            round(part[TARGET].mean(), 4),
        )

    results = fit_and_score(build_models(), train, validation, test)
    print("\nVALIDATION MODEL COMPARISON")
    print(results["validation_table"].round(4).to_string())
    print("\nSELECTED MODEL:", results["selected_name"])

    print("\nTEST METRICS")
    print(pd.Series(results["test_metrics"].__dict__).round(4))
    print("\nTEST BUSINESS-RULE BASELINE")
    print(pd.Series(results["rule_test_metrics"].__dict__).round(4))

    print("\nSEGMENT PERFORMANCE")
    for segment in ["country", "device_type", "customer_value_tier"]:
        print(f"\n{segment}")
        print(segment_metrics(test, results["test_scores"], segment).round(4).to_string())

    print("\nILLUSTRATIVE BUSINESS VALUE")
    print(pd.Series(estimate_business_value(results["test_metrics"])).round(2))


if __name__ == "__main__":
    main()
