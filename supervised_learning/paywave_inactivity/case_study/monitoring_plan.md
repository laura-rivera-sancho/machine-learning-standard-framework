# Monitoring Plan — PayWave Inactivity

## Pre-score controls

- Validate schema, unique customer-scoring keys, feature ranges, and scoring-date cutoffs.
- Stop scoring if leakage fields enter the feature contract.
- Confirm population eligibility and the 5,000-customer operational capacity.

## Monitoring thresholds

| Signal | Review threshold | Response |
|---|---:|---|
| Missingness | >2 percentage-point increase for any model feature | Investigate source; pause if material |
| Population size | >15% change vs. recent cohorts | Validate eligibility and pipeline coverage |
| Score distribution | PSI >0.20 | Review drift and calibration before activation |
| PR AUC | >15% relative decline after labels mature | Investigate, recalibrate, or retrain |
| Precision at 5,000 | <70% | Suspend model-led activation and use fallback rule |
| Lift at 5,000 | <2.0x | Reassess value and candidate selection |
| Segment precision gap | >15 percentage points with sufficient sample | Review feature, policy, and allocation risks |

## Outcome and causal monitoring

Track incremental retention, contribution margin, outreach cost, opt-outs, complaints, and repeated-contact exposure using a randomized holdout. Model discrimination alone is not evidence that the intervention works.

## Rollback

Retain the governed recency rule as the operational fallback. Roll back when data integrity fails, performance crosses a stop threshold, approval is withdrawn, or customer-experience guardrails deteriorate.
