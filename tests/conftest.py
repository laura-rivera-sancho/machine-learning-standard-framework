from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_ROOT = ROOT / "supervised_learning" / "campaign_response_propensity"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def generator():
    return _load("campaign_generator", MODULE_ROOT / "src" / "generate_synthetic_data.py")


@pytest.fixture(scope="session")
def modeling():
    return _load("campaign_modeling", MODULE_ROOT / "src" / "train_evaluate.py")
