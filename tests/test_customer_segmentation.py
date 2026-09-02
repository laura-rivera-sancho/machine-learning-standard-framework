from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "unsupervised_learning" / "customer_segmentation" / "src"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, MODULE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


generator = _load("generate_synthetic_data")
segmentation = _load("segment_evaluate")


def test_generator_is_deterministic():
    first = generator.generate_clean_data(seed=7, n_customers=120)
    second = generator.generate_clean_data(seed=7, n_customers=120)
    assert first.equals(second)
    assert len(first) == 240
    assert first["snapshot_date"].nunique() == 2


def test_quality_controls_remove_controlled_defects():
    raw = generator.generate_raw_data(seed=8, n_customers=180)
    report = segmentation.quality_report(raw)
    clean = segmentation.clean_data(raw)
    assert report["duplicate_customer_snapshot"] >= 8
    assert report["negative_recency"] >= 2
    assert report["invalid_rates"] >= 2
    assert report["missing_feature_values"] > 0
    assert not clean.duplicated(["customer_id", "snapshot_date"]).any()
    assert clean["recency_days"].ge(0).all()


def test_feature_contract_excludes_truth_and_non_behavioral_fields():
    assert "synthetic_profile_truth" not in segmentation.FEATURES
    assert "region" not in segmentation.FEATURES
    assert "marketing_consent" not in segmentation.FEATURES
    assert set(segmentation.LOG_FEATURES + segmentation.RATE_FEATURES) == set(segmentation.FEATURES)


def test_candidate_comparison_and_selection_are_valid():
    raw = generator.generate_raw_data(seed=9, n_customers=600)
    clean = segmentation.clean_data(raw)
    current = clean[clean["snapshot_date"].eq(clean["snapshot_date"].max())]
    x = segmentation.feature_pipeline().fit_transform(current[segmentation.FEATURES])
    table = segmentation.compare_candidates(x, seed=9)
    selected = segmentation.select_candidate(table)
    assert selected in table.index
    assert any(name.startswith("kmeans") for name in table.index)
    assert any(name.startswith("gaussian_mixture") for name in table.index)
    assert np.isfinite(table["silhouette"]).all()
    assert table["coverage"].between(0, 1).all()


def test_end_to_end_segmentation_produces_actionable_profiles():
    raw = generator.generate_raw_data(seed=10, n_customers=700)
    results = segmentation.run_analysis(raw, seed=10)
    current = results["current"]
    assert current["segment"].nunique() >= 4
    assert current["segment"].ne("Unassigned").mean() >= 0.90
    assert results["profile"]["customer_share"].sum() >= 0.90
    assert -1 <= results["temporal_ari"] <= 1
