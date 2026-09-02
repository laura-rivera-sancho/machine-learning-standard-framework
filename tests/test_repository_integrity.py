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
        "unsupervised_learning/customer_segmentation/README.md",
        "unsupervised_learning/customer_segmentation/customer_segmentation_fundamentals.md",
        "unsupervised_learning/customer_segmentation/methodology.md",
        "unsupervised_learning/customer_segmentation/case_study/business_case.md",
        "unsupervised_learning/customer_segmentation/case_study/data_dictionary.md",
        "unsupervised_learning/customer_segmentation/case_study/expected_results.md",
        "unsupervised_learning/customer_segmentation/case_study/monitoring_plan.md",
        "unsupervised_learning/customer_segmentation/reports/stakeholder_readout.md",
        "unsupervised_learning/customer_segmentation/model_card/model_card.md",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    assert not missing, f"Missing portfolio files: {missing}"
