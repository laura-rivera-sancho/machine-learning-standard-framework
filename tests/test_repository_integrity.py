from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_relative_markdown_links_resolve():
    pattern = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
    broken = []
    for document in ROOT.rglob("*.md"):
        for target in pattern.findall(document.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path = target.split("#", 1)[0]
            if path and not (document.parent / path).resolve().exists():
                broken.append(f"{document.relative_to(ROOT)} -> {target}")
    assert not broken, "Broken Markdown links:\n" + "\n".join(broken)


def test_repository_has_no_challenge_notebook():
    names = [path.name.lower() for path in ROOT.rglob("*.ipynb")]
    assert not any("challenge" in name for name in names)


def test_required_portfolio_files_exist():
    required = [
        "README.md",
        "ROADMAP.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "supervised_learning/campaign_response_propensity/README.md",
        "supervised_learning/campaign_response_propensity/campaign_response_fundamentals.md",
        "supervised_learning/campaign_response_propensity/methodology.md",
        "supervised_learning/campaign_response_propensity/case_study/business_case.md",
        "supervised_learning/campaign_response_propensity/case_study/data_dictionary.md",
        "supervised_learning/campaign_response_propensity/reports/stakeholder_readout.md",
        "supervised_learning/campaign_response_propensity/model_card/model_card.md",
        "supervised_learning/campaign_response_propensity/reports/stakeholder_readout.pptx",
        "supervised_learning/paywave_inactivity/README.md",
        "supervised_learning/paywave_inactivity/paywave_inactivity_fundamentals.md",
        "supervised_learning/paywave_inactivity/methodology.md",
        "supervised_learning/paywave_inactivity/case_study/business_case.md",
        "supervised_learning/paywave_inactivity/case_study/data_dictionary.md",
        "supervised_learning/paywave_inactivity/case_study/expected_results.md",
        "supervised_learning/paywave_inactivity/case_study/monitoring_plan.md",
        "supervised_learning/paywave_inactivity/model_card/model_card.md",
        "supervised_learning/paywave_inactivity/reports/stakeholder_readout.pptx",
        "unsupervised_learning/customer_segmentation/README.md",
        "unsupervised_learning/customer_segmentation/customer_segmentation_fundamentals.md",
        "unsupervised_learning/customer_segmentation/methodology.md",
        "unsupervised_learning/customer_segmentation/case_study/business_case.md",
        "unsupervised_learning/customer_segmentation/case_study/data_dictionary.md",
        "unsupervised_learning/customer_segmentation/case_study/expected_results.md",
        "unsupervised_learning/customer_segmentation/case_study/monitoring_plan.md",
        "unsupervised_learning/customer_segmentation/reports/stakeholder_readout.md",
        "unsupervised_learning/customer_segmentation/model_card/model_card.md",
        "unsupervised_learning/customer_segmentation/reports/stakeholder_readout.pptx",
        "production_readiness/README.md",
        "production_readiness/production_readiness_fundamentals.md",
        "production_readiness/operating_model.md",
        "production_readiness/contracts/model_release_contract.md",
        "production_readiness/contracts/example_release_manifest.json",
        "production_readiness/monitoring/monitoring_and_alerting.md",
        "production_readiness/operations/retraining_and_rollback.md",
        "production_readiness/operations/incident_runbook.md",
        "production_readiness/templates/model_release_checklist.md",
        "production_readiness/reports/stakeholder_readout.md",
        "production_readiness/reports/stakeholder_readout.pptx",
        "production_readiness/src/validate_release_manifest.py",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    assert not missing, f"Missing portfolio files: {missing}"


def test_completed_ml_modules_publish_valid_powerpoint_readouts():
    decks = [
        ROOT / "supervised_learning/campaign_response_propensity/reports/stakeholder_readout.pptx",
        ROOT / "supervised_learning/paywave_inactivity/reports/stakeholder_readout.pptx",
        ROOT / "unsupervised_learning/customer_segmentation/reports/stakeholder_readout.pptx",
        ROOT / "production_readiness/reports/stakeholder_readout.pptx",
    ]
    assert all(deck.read_bytes().startswith(b"PK") for deck in decks)
