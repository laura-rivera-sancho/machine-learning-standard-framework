from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "production_readiness/contracts/example_release_manifest.json"
MODULE_PATH = ROOT / "production_readiness/src/validate_release_manifest.py"

spec = importlib.util.spec_from_file_location("release_manifest_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)
validate_manifest = validator.validate_manifest


def load_example() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_example_release_manifest_is_valid():
    assert validate_manifest(load_example()) == []


def test_unapproved_model_is_blocked():
    manifest = copy.deepcopy(load_example())
    manifest["model"]["lifecycle_state"] = "candidate"
    assert "model.lifecycle_state must be approved before release" in validate_manifest(manifest)


def test_below_threshold_candidate_is_blocked():
    manifest = copy.deepcopy(load_example())
    manifest["evaluation"]["observed_value"] = 1.0
    assert "evaluation observed_value is below the release_threshold" in validate_manifest(manifest)


def test_missing_output_contract_field_is_blocked():
    manifest = copy.deepcopy(load_example())
    manifest["serving"]["output_contract"].remove("model_version")
    assert "output contract is missing: model_version" in validate_manifest(manifest)


def test_unrehearsed_rollback_is_blocked():
    manifest = copy.deepcopy(load_example())
    manifest["rollback"]["rehearsal_status"] = "not_run"
    assert "rollback.rehearsal_status must be passed before release" in validate_manifest(manifest)
