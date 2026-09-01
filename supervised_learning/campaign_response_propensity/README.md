# ML1 — Campaign Response Propensity

> **Status: Complete.** A leakage-safe, temporally validated propensity model for allocating limited retention-campaign capacity.

## Decision

Which consented Harbor & Pine customers should be prioritized when the CRM team can contact only 20% of the eligible monthly audience?

The model estimates the probability of response within 14 days after a standardized retention campaign. It supports ranking and capacity allocation; it does not estimate causal treatment effects or authorize automated contact.

## Review path

| Resource | Purpose |
|---|---|
| [Stakeholder readout](reports/stakeholder_readout.md) | Decision, results, limitations, and pilot recommendation |
| [Executive visual](reports/ml1_executive_summary.png) | Baseline comparison, calibration, drivers, and economics |
| [Fundamentals](campaign_response_fundamentals.md) | Key supervised-learning concepts and interpretation guidance |
| [Methodology](methodology.md) | Reusable source-to-decision modeling lifecycle |
| [Business case](case_study/business_case.md) | Audience, target contract, capacity, and acceptance criteria |
| [Data dictionary](case_study/data_dictionary.md) | Feature timing, definitions, and leakage classifications |
| [Expected results](case_study/expected_results.md) | Reproducible validation and test evidence |
| [Model card](model_card/model_card.md) | Intended use, exclusions, risks, and operating controls |
| [Monitoring plan](case_study/monitoring_plan.md) | Data, drift, calibration, performance, and rollback thresholds |
| [Reference implementation](src) | Deterministic generation, training, evaluation, and visual output |

## Held-out result

The July–August 2026 test set contains 11,993 eligible customer-campaign rows and an 8.01% response rate. At 20% capacity, the selected HistGradientBoosting model identifies 439 responders versus 392 for the current rule—47 additional responders without increasing contact volume.

| Metric | Selected model | Current rule |
|---|---:|---:|
| PR AUC | 0.2201 | 0.1827 |
| ROC AUC | 0.7108 | 0.6719 |
| Precision at capacity | 18.30% | 16.34% |
| Recall at capacity | 45.68% | 40.79% |
| Lift at capacity | 2.28x | 2.04x |
| Responders captured | 439 | 392 |
| Illustrative net value | $11,517.72 | $9,809.31 |

## Recommendation

Advance the model to shadow scoring and then a randomized operational pilot. Retain consent and suppression checks outside the model, monitor calibration by cohort and segment, and measure incremental campaign impact separately before scaling.

## Reproduce

From the repository root:

```bash
python supervised_learning/campaign_response_propensity/src/generate_synthetic_data.py
python supervised_learning/campaign_response_propensity/src/train_evaluate.py
python supervised_learning/campaign_response_propensity/src/create_visuals.py
pytest
```

The full generated dataset and processed tables are intentionally excluded from version control. A compact synthetic review sample is committed at `data/raw/campaign_response_sample.csv`.
