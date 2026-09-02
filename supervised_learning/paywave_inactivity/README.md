# ML1 Transfer — PayWave Inactivity

> **Status: Complete.** A migrated supervised-learning transfer case that tests whether the repository's decision framework generalizes from campaign response to inactivity-risk prioritization.

## Decision

Which active PayWave customers should receive retention outreach when the team can contact only 5,000 customers per scoring cycle?

The selected Gradient Boosting model predicts inactivity within 30 days. It supports a ranked, capacity-constrained shortlist; it does not establish that outreach prevents inactivity.

## Executive result

On the 29,999-customer held-out Test cohort, the model identifies **3,853 future-inactive customers** within the 5,000-customer capacity—**552 more** than the recency rule. Precision is **77.06%**, recall is **42.99%**, and lift is **2.58x**.

[Download the five-slide executive PowerPoint](reports/stakeholder_readout.pptx) or review the [stakeholder memo](reports/stakeholder_readout.md).

![PayWave executive summary comparing the model and current rule](reports/executive_summary.png)

## Review path

| Resource | Purpose |
|---|---|
| [Executive PowerPoint](reports/stakeholder_readout.pptx) | Non-technical recommendation, evidence, limitations, and pilot plan |
| [Stakeholder readout](reports/stakeholder_readout.md) | Decision memo and detailed findings |
| [Fundamentals](paywave_inactivity_fundamentals.md) | Predictive-modeling concepts and interpretation |
| [Methodology](methodology.md) | End-to-end supervised workflow |
| [Business case](case_study/business_case.md) | Decision, population, horizon, capacity, and success criteria |
| [Data dictionary](case_study/data_dictionary.md) | Feature definitions and leakage controls |
| [Expected results](case_study/expected_results.md) | Deterministic reference evidence |
| [Model card](model_card/model_card.md) | Intended use, limitations, controls, and approval boundary |
| [Monitoring plan](case_study/monitoring_plan.md) | Data, drift, performance, and rollback thresholds |
| [Source](src) | Synthetic generator and model-comparison workflow |

## Reproduce

From the repository root:

```bash
python supervised_learning/paywave_inactivity/src/generate_synthetic_data.py
python supervised_learning/paywave_inactivity/src/train_evaluate_models.py
pytest
```

The full generated data and processed outputs are ignored. A deterministic review sample is versioned. No challenge notebook is included.

## Migration note

This case was originally developed in `analytics-standard-framework/04_predictive_analytics`. The Machine Learning repository is now its canonical home because its primary evidence is supervised modeling, temporal evaluation, calibration, capacity-aware selection, and model operations.
