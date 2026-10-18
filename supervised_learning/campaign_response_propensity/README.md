# Campaign Response Prioritization

**A leakage-safe, temporally validated decision workflow for allocating limited retention-campaign capacity.**

[Read the stakeholder recommendation](reports/stakeholder_readout.md) · [Open the executive visual](reports/ml1_executive_summary.png) · [Review the model card](model_card/model_card.md) · [Contact Laura](mailto:laura.riverasancho33@gmail.com)

## The decision this supports

Which consented customers should be prioritized when a CRM team can contact only a fixed share of the eligible monthly audience?

The workflow estimates the probability of response within 14 days after a standardized retention campaign. It supports ranking and capacity allocation; it does not estimate causal treatment effects, override consent or suppression rules, or authorize automated contact.

## Pilot at a glance

| Item | Typical scope |
|---|---|
| **Best for** | Retention, CRM, growth, and customer teams with limited contact capacity and an existing campaign history |
| **Duration** | About 4 weeks |
| **Inputs** | Point-in-time customer features, campaign history, response definition, eligibility and consent rules, capacity constraint, contact economics, and decision owners |
| **Week 1** | Confirm target definition, prediction horizon, feature timing, baseline, capacity rule, exclusions, and acceptance criteria |
| **Weeks 2–3** | Validate data, train and compare candidates, test temporal stability, calibration, ranking value, segments, and leakage controls |
| **Week 4** | Deliver the scoring workflow, validation report, model card, executive recommendation, and shadow-pilot plan |
| **Buyer receives** | Baseline comparison, reproducible scoring workflow, prioritized eligible population, validation report, model card, monitoring plan, and pilot design |
| **Not included** | Automated outreach, causal lift claims, production CRM integration, protected-class targeting, or broad rollout without an operational test |

## Demonstration evidence

The held-out July–August 2026 reference set contains 11,993 eligible customer-campaign rows and an 8.01% response rate. At 20% capacity, the selected HistGradientBoosting model identifies 439 responders versus 392 for the current rule—47 additional responders without increasing contact volume.

| Metric | Selected model | Current rule |
|---|---:|---:|
| PR AUC | 0.2201 | 0.1827 |
| ROC AUC | 0.7108 | 0.6719 |
| Precision at capacity | 18.30% | 16.34% |
| Recall at capacity | 45.68% | 40.79% |
| Lift at capacity | 2.28x | 2.04x |
| Responders captured | 439 | 392 |
| Illustrative net value | $11,517.72 | $9,809.31 |

These figures come from deterministic synthetic data. They demonstrate the evaluation and decision workflow, not observed customer behavior or guaranteed campaign value.

## Recommended next decision

Advance the workflow to shadow scoring and then a randomized operational pilot. Keep consent and suppression checks outside the model, compare against the current allocation rule, monitor calibration and selection rates by cohort and segment, and measure incremental campaign impact separately before scaling.

## Pilot acceptance criteria

Exact thresholds should be agreed after the data-readiness review. At minimum:

- training, validation, and test populations reconcile to documented point-in-time rules;
- no post-outcome or operationally unavailable features enter scoring;
- the selected approach is compared with the current rule at the actual capacity constraint;
- calibration, ranking value, segment behavior, and failure cases are reported together;
- consent, suppression, human review, and rollback controls remain visible; and
- the final readout names the go, iterate, or stop decision and the evidence required next.

## Delivery evidence

| Resource | What it demonstrates |
|---|---|
| [Stakeholder readout](reports/stakeholder_readout.md) | Decision, results, limitations, and pilot recommendation |
| [Executive PowerPoint](reports/stakeholder_readout.pptx) | Five-slide, non-technical decision narrative |
| [Executive visual](reports/ml1_executive_summary.png) | Baseline comparison, calibration, drivers, and economics |
| [Business case](case_study/business_case.md) | Audience, target contract, capacity, and acceptance criteria |
| [Data dictionary](case_study/data_dictionary.md) | Feature timing, definitions, and leakage classifications |
| [Reference findings](case_study/expected_results.md) | Reproducible validation and held-out evidence |
| [Model card](model_card/model_card.md) | Intended use, exclusions, risks, and operating controls |
| [Monitoring plan](case_study/monitoring_plan.md) | Data, drift, calibration, performance, and rollback thresholds |
| [Reference implementation](src) | Deterministic generation, training, evaluation, and visual output |
| [Method notes](campaign_response_fundamentals.md) | Supervised-learning concepts and interpretation boundaries |
| [Delivery methodology](methodology.md) | Source-to-decision modeling lifecycle |

## Technical reproduction

```bash
python supervised_learning/campaign_response_propensity/src/generate_synthetic_data.py
python supervised_learning/campaign_response_propensity/src/train_evaluate.py
python supervised_learning/campaign_response_propensity/src/create_visuals.py
pytest
```

The full generated dataset and processed tables are intentionally excluded from version control. A compact synthetic review sample is committed at `data/raw/campaign_response_sample.csv`.

## Start a scope discussion

[Email Laura](mailto:laura.riverasancho33@gmail.com) with the decision you need to make, the available campaign history and decision systems, the monthly capacity constraint, and the target timeline.
