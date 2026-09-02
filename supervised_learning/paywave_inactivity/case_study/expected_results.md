# PayWave Expected Reference Results

These reference values are produced by `src/generate_synthetic_data.py` with `SEED = 126` and evaluated by `src/train_evaluate_models.py`. They provide a reproducibility check for the guided analysis and should not be treated as real customer or company results.

## Data-quality findings

The generated raw dataset contains 240,045 rows and deliberately includes:

| Check | Expected count |
|---|---:|
| Duplicate customer/scoring-date rows | 45 |
| Lowercase country values | 40 |
| Negative recency values | 6 |
| Negative 30-day transaction counts | 6 |
| Negative tenure values | 6 |
| Leakage columns present | 3 |

After removing duplicates and impossible values, the analytical population contains 239,982 customer-scoring-date rows.

## Temporal validation design

| Split | Rows | Scoring dates | Target prevalence |
|---|---:|---|---:|
| Train | 149,984 | January-May 2026 | 22.63% |
| Validation | 59,999 | June-July 2026 | 27.06% |
| Test | 29,999 | August 2026 | 29.87% |

The increasing prevalence is intentional temporal drift. Model selection uses Validation only; Test remains untouched until the model and outreach policy are frozen.

## Validation model comparison

Validation covers two scoring cycles, so the operational evaluation aggregates two cycles of 5,000-contact capacity (`k = 10,000`).

| Candidate | ROC AUC | PR AUC | Inactive customers captured at capacity |
|---|---:|---:|---:|
| Gradient Boosting | 0.8013 | 0.6525 | 7,209 |
| Logistic Regression | 0.7995 | 0.6507 | 7,171 |
| Random Forest | 0.7990 | 0.6489 | 7,169 |
| Recency business rule | 0.7575 | 0.5693 | 5,839 |

Gradient Boosting is selected on Validation PR AUC. Its advantage over Logistic Regression is small, so interpretability and deployment complexity should be considered before production use.

The recency rule produces an uncalibrated ranking score rather than a probability. ROC AUC, PR AUC, and top-k metrics are valid for the rule; Brier loss is intentionally reported as not applicable.

## Held-out Test results

The final Test cohort contains 29,999 customers. Retention can contact 5,000 of them.

| Metric | Selected Gradient Boosting | Recency business rule |
|---|---:|---:|
| ROC AUC | 0.8125 | 0.7674 |
| PR AUC | 0.6943 | 0.6122 |
| Brier score | 0.1478 | Not applicable |
| Precision@5,000 | 77.06% | 66.02% |
| Recall@5,000 | 42.99% | 36.83% |
| Lift@5,000 | 2.58x | 2.21x |
| Inactive customers captured | 3,853 | 3,301 |

The selected model captures **552 more future-inactive customers** than the business rule within the same outreach capacity, a 16.7% increase over the rule baseline.

## Segment review

| Segment | Rows | Prevalence | ROC AUC | PR AUC | Brier |
|---|---:|---:|---:|---:|---:|
| BR | 6,016 | 32.83% | 0.8091 | 0.7157 | 0.1563 |
| CR | 2,939 | 28.79% | 0.8157 | 0.6924 | 0.1437 |
| MX | 6,635 | 29.98% | 0.8166 | 0.6934 | 0.1472 |
| US | 14,409 | 28.82% | 0.8102 | 0.6853 | 0.1452 |
| Desktop | 8,442 | 29.53% | 0.8154 | 0.6950 | 0.1457 |
| Mobile | 21,557 | 30.01% | 0.8113 | 0.6941 | 0.1486 |
| High value | 2,493 | 17.69% | 0.7970 | 0.5722 | 0.1085 |
| Medium value | 16,389 | 28.94% | 0.8091 | 0.6821 | 0.1462 |
| Low value | 11,117 | 33.98% | 0.8089 | 0.7210 | 0.1588 |

Performance is directionally stable across markets and devices. Differences in PR AUC partly reflect different target prevalence, so segment conclusions should consider prevalence, discrimination, calibration, sample size, and business impact together.

## Illustrative business value

The reference scenario assumes:

- 18% of correctly identified inactive customers are successfully retained
- each retained customer is worth $85
- each outreach contact costs $2.50

| Business estimate | Value |
|---|---:|
| Customers targeted | 5,000 |
| Expected inactive customers captured | 3,853 |
| Expected successful saves | 693.54 |
| Expected retained value | $58,950.90 |
| Outreach cost | $12,500.00 |
| Illustrative net value | **$46,450.90** |

This is a sensitivity-model input, not a forecast or realized return. Intervention effectiveness must be validated separately, ideally through a randomized retention experiment.

## Expected recommendation

Proceed to a controlled operational pilot rather than automatic full deployment.

The model materially improves capacity-constrained targeting over the existing rule, performs consistently across major segments, and produces favorable illustrative economics. Before wider deployment, PayWave should validate intervention lift, review calibration, confirm production feature availability, monitor segment outcomes, and define drift and retraining thresholds.
