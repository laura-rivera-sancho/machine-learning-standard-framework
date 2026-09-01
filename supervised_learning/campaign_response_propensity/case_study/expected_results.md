# ML1 Expected Results

These results are deterministic for seed `731` and the pinned dependencies.

## Data validation

- Raw rows: 72,060
- Duplicate customer/cohort rows detected: 60
- Negative recency rows: 15
- Invalid tenure rows: 15
- Missing model-feature cells: 4,322
- Explicit leakage/generator columns detected: 4
- Clean modeling rows: 71,970

## Temporal split

| Split | Cohorts | Rows |
|---|---|---:|
| Train | Sep 2025–Apr 2026 | 47,983 |
| Validation | May–Jun 2026 | 11,994 |
| Test | Jul–Aug 2026 | 11,993 |

The latest two cohorts are not used for model-family selection.

## Validation selection

| Model | ROC AUC | PR AUC | Response rate |
|---|---:|---:|---:|
| Logistic Regression | 0.7187 | 0.2409 | 8.85% |
| Decision Tree | 0.7097 | 0.2165 | 8.85% |
| HistGradientBoosting | **0.7254** | **0.2470** | 8.85% |

HistGradientBoosting is selected on Validation PR AUC. The stronger model earns selection by capturing nonlinear value/recency, discount, and campaign-fatigue relationships that the additive baseline cannot fully represent.

## Held-out Test comparison

Capacity is 2,399 customers, or 20% of the 11,993-row Test population. Test response prevalence is 8.01%.

| Metric | Selected model | Current rule |
|---|---:|---:|
| ROC AUC | 0.7108 | 0.6719 |
| PR AUC | 0.2201 | 0.1827 |
| Precision at capacity | 18.30% | 16.34% |
| Recall at capacity | 45.68% | 40.79% |
| Lift at capacity | 2.28x | 2.04x |
| Responders captured | 439 | 392 |

The model identifies 47 additional responders, a 12.0% increase over the rule at identical capacity. This passes the business acceptance threshold.

## Calibration

- Brier score: 0.0693
- Log loss: 0.2566
- Highest score band: 28.81% mean predicted response versus 24.17% observed

Ranking is useful, but upper score bands modestly overpredict. Shadow scoring and pilot monitoring should include calibration review and possible recalibration.

## Segment findings

- PR AUC ranges from 0.1354 for Standard loyalty to 0.3250 for Premium, partly reflecting different base rates.
- Regional ROC AUC ranges from 0.6780 in South to 0.7268 in Midwest.
- No segment result supports automatic exclusion or differential treatment; weaker segments require monitoring and diagnostic review.

## Influential inputs

Permutation importance identifies historical click rate, discount share, prior campaign responses, campaign spacing, loyalty tier, recency, and spend as the strongest predictive inputs. Importance is not causal evidence.

## Illustrative economics

| Measure | Selected model | Current rule |
|---|---:|---:|
| Gross margin | $15,413.54 | $13,230.81 |
| Offer cost | $3,056.17 | $2,581.85 |
| Contact cost | $839.65 | $839.65 |
| Net value | **$11,517.72** | **$9,809.31** |

The $1,708.41 difference is retrospective and synthetic. A randomized pilot is required before attributing incremental value to the targeting policy.
