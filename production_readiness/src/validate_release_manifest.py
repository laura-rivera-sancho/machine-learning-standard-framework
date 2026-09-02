from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_SECTIONS = {
    "model",
    "provenance",
    "decision",
    "evaluation",
    "serving",
    "monitoring",
    "rollback",
    "approvals",
}
SUPPORTED_TASK_TYPES = {"supervised_binary", "supervised_regression", "unsupervised"}
SUPPORTED_SERVING_MODES = {"batch", "online"}
SUPPORTED_ROLLOUTS = {"shadow", "limited", "parallel", "full_approved_scope"}
REQUIRED_OUTPUT_FIELDS = {
    "entity_id",
    "model_id",
    "model_version",
    "scored_at",
    "prediction",
    "decision_context",
}


def _require_text(container: dict[str, Any], field: str, context: str, errors: list[str]) -> None:
    value = container.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context}.{field} must be a non-empty string")


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return human-readable validation errors for a release manifest."""
    errors: list[str] = []
    missing_sections = sorted(REQUIRED_SECTIONS - manifest.keys())
    if missing_sections:
        errors.append(f"missing required sections: {', '.join(missing_sections)}")
        return errors

    model = manifest["model"]
    provenance = manifest["provenance"]
    decision = manifest["decision"]
    evaluation = manifest["evaluation"]
    serving = manifest["serving"]
    monitoring = manifest["monitoring"]
    rollback = manifest["rollback"]
    approvals = manifest["approvals"]

    for section_name, section in (
        ("model", model),
        ("provenance", provenance),
        ("decision", decision),
        ("evaluation", evaluation),
        ("serving", serving),
        ("monitoring", monitoring),
        ("rollback", rollback),
        ("approvals", approvals),
    ):
        if not isinstance(section, dict):
            errors.append(f"{section_name} must be an object")
    if errors:
        return errors

    for field in ("id", "version", "artifact_checksum"):
        _require_text(model, field, "model", errors)
    if model.get("task_type") not in SUPPORTED_TASK_TYPES:
        errors.append("model.task_type is unsupported")
    if model.get("lifecycle_state") != "approved":
        errors.append("model.lifecycle_state must be approved before release")

    for field in ("source_revision", "training_data_reference", "training_cutoff"):
        _require_text(provenance, field, "provenance", errors)
    for field in (
        "name",
        "intended_use",
        "prohibited_use",
        "business_owner",
        "model_owner",
    ):
        _require_text(decision, field, "decision", errors)

    for field in ("window", "primary_metric"):
        _require_text(evaluation, field, "evaluation", errors)
    observed = evaluation.get("observed_value")
    threshold = evaluation.get("release_threshold")
    if not isinstance(observed, (int, float)) or not isinstance(threshold, (int, float)):
        errors.append("evaluation observed_value and release_threshold must be numeric")
    elif observed < threshold:
        errors.append("evaluation observed_value is below the release_threshold")

    if serving.get("mode") not in SUPPORTED_SERVING_MODES:
        errors.append("serving.mode is unsupported")
    if serving.get("rollout") not in SUPPORTED_ROLLOUTS:
        errors.append("serving.rollout is unsupported")
    output_fields = serving.get("output_contract")
    if not isinstance(output_fields, list):
        errors.append("serving.output_contract must be a list")
    else:
        missing_outputs = sorted(REQUIRED_OUTPUT_FIELDS - set(output_fields))
        if missing_outputs:
            errors.append(f"output contract is missing: {', '.join(missing_outputs)}")

    _require_text(monitoring, "review_cadence", "monitoring", errors)
    _require_text(monitoring, "operations_owner", "monitoring", errors)
    if not monitoring.get("rollback_triggers"):
        errors.append("monitoring.rollback_triggers must contain at least one trigger")

    for field in ("fallback", "owner", "rehearsal_status"):
        _require_text(rollback, field, "rollback", errors)
    if rollback.get("rehearsal_status") != "passed":
        errors.append("rollback.rehearsal_status must be passed before release")

    for field in ("technical_approver", "business_approver", "approved_on"):
        _require_text(approvals, field, "approvals", errors)
    return errors


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an ML release manifest.")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    errors = validate_manifest(load_manifest(args.manifest))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"VALID: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
