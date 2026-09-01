from __future__ import annotations

import numpy as np
import pandas as pd


def small_cohorts() -> pd.DatetimeIndex:
    return pd.date_range("2025-01-01", periods=8, freq="MS")


def test_generator_is_deterministic(generator):
    first = generator.generate_clean_data(seed=11, n_customers=80, cohort_dates=small_cohorts())
    second = generator.generate_clean_data(seed=11, n_customers=80, cohort_dates=small_cohorts())
    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 640
    assert first["responded_within_14d"].isin([0, 1]).all()


def test_raw_data_contains_controlled_quality_defects(generator, modeling):
    raw = generator.generate_raw_data(seed=12, n_customers=120, cohort_dates=small_cohorts())
    report = modeling.quality_report(raw)
    assert report["duplicate_customer_scoring_date"] >= 4
    assert report["negative_recency"] >= 1
    assert report["invalid_tenure"] >= 1
    assert report["missing_model_values"] > 0
    assert report["leakage_columns_present"] == 4


def test_cleaning_applies_population_and_integrity_contract(generator, modeling):
    raw = generator.generate_raw_data(seed=13, n_customers=150, cohort_dates=small_cohorts())
    clean = modeling.clean_data(raw)
    assert not clean.duplicated(["customer_id", "scoring_date"]).any()
    assert clean["recency_days"].ge(0).all()
    assert clean["customer_tenure_days"].ge(30).all()
    assert clean["marketing_consent"].eq(1).all()
    assert clean["contact_suppressed"].eq(0).all()
    assert set(clean["region"].unique()).issubset({"NORTHEAST", "SOUTH", "MIDWEST", "WEST"})


def test_temporal_split_preserves_future_holdout(generator, modeling):
    raw = generator.generate_raw_data(seed=14, n_customers=100, cohort_dates=small_cohorts())
    train, validation, test = modeling.temporal_split(modeling.clean_data(raw))
    assert train["scoring_date"].max() < validation["scoring_date"].min()
    assert validation["scoring_date"].max() < test["scoring_date"].min()
    assert validation["scoring_date"].nunique() == 2
    assert test["scoring_date"].nunique() == 2


def test_model_contract_excludes_leakage_and_sensitive_features(modeling):
    assert not set(modeling.LEAKAGE_COLUMNS).intersection(modeling.MODEL_FEATURES)
    assert not modeling.PROTECTED_OR_SENSITIVE_FEATURES.intersection(modeling.MODEL_FEATURES)
    assert modeling.TARGET not in modeling.MODEL_FEATURES


def test_rule_ranking_does_not_claim_probability_calibration(generator, modeling):
    clean = generator.generate_clean_data(seed=15, n_customers=100, cohort_dates=small_cohorts())
    scores = modeling.business_rule_scores(clean)
    metrics = modeling.evaluate_predictions(
        clean[modeling.TARGET], scores, probability_scores=False
    )
    assert np.isnan(metrics.brier)
    assert np.isnan(metrics.log_loss)
    assert 0 <= metrics.precision_at_capacity <= 1
    assert metrics.capacity == round(len(clean) * 0.20)


def test_small_end_to_end_model_selection(generator, modeling):
    raw = generator.generate_raw_data(seed=16, n_customers=240, cohort_dates=small_cohorts())
    clean = modeling.clean_data(raw)
    train, validation, test = modeling.temporal_split(clean)
    models = modeling.build_models(random_state=16)
    models["hist_gradient_boosting"].set_params(model__max_iter=25)
    results = modeling.fit_and_evaluate(models, train, validation, test)
    assert results["selected_name"] in models
    assert set(models).issubset(results["validation_table"].index)
    assert 0 <= results["test_metrics"].pr_auc <= 1
    assert 0 <= results["test_metrics"].brier <= 1
    assert len(results["calibration_table"]) >= 5
    assert not results["importance_table"].empty
