from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "supervised_learning" / "paywave_inactivity" / "src"
SAMPLE = ROOT / "supervised_learning/paywave_inactivity/data/raw/paywave_inactivity_sample.csv"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, MODULE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


generator = _load("generate_synthetic_data")
modeling = _load("train_evaluate_models")


def test_sample_quality_leakage_and_cleaning():
    raw = pd.read_csv(SAMPLE)
    report = modeling.quality_report(raw)
    assert len(raw) == 2_500
    assert report["duplicate_customer_scoring_date"] == 30
    assert report["leakage_columns_present"] == 3
    clean = modeling.clean_data(raw)
    assert not clean.duplicated(["customer_id", "scoring_date"]).any()
    assert clean["days_since_last_transaction"].ge(0).all()
    assert clean["transactions_30d"].ge(0).all()


def test_uncalibrated_rule_does_not_report_brier():
    clean = modeling.clean_data(pd.read_csv(SAMPLE))
    metrics = modeling.evaluate_predictions(
        clean[modeling.TARGET],
        modeling.business_rule_scores(clean),
        k=500,
        probability_scores=False,
    )
    assert np.isnan(metrics.brier)
    assert metrics.k == 500


def test_small_temporal_workflow():
    original = generator.N_CUSTOMERS
    generator.N_CUSTOMERS = 800
    try:
        clean = modeling.clean_data(generator.generate_raw_data(seed=126))
    finally:
        generator.N_CUSTOMERS = original
    train, validation, test = modeling.temporal_split(clean)
    assert train["scoring_date"].max() < validation["scoring_date"].min()
    assert validation["scoring_date"].max() < test["scoring_date"].min()
    models = modeling.build_models(random_state=42)
    models["random_forest"].set_params(model__n_estimators=20, model__n_jobs=1)
    models["gradient_boosting"].set_params(model__max_iter=30)
    results = modeling.fit_and_score(models, train, validation, test)
    assert results["selected_name"] in models
    assert 0 <= results["test_metrics"].pr_auc <= 1
