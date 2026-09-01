# ML1 Monitoring Plan

## Pre-score controls

Stop scoring if:

- required fields or the scoring cohort are missing
- feature data are older than the declared monthly cutoff
- duplicate customer/cohort keys exceed 0.1%
- consent or suppression controls cannot be verified
- model version, feature contract, or scoring timestamp are absent

## Data and drift monitoring

| Signal | Review threshold | Action threshold |
|---|---:|---:|
| Missingness change | +2 percentage points | +5 percentage points |
| Population Stability Index | 0.10 | 0.25 |
| Unknown category share | 0.5% | 2.0% |
| Score mean shift | 15% relative | 30% relative |
| Eligible volume shift | 15% | 30% |

Thresholds trigger investigation; they are not automatic evidence that retraining is correct.

## Delayed performance monitoring

After 14-day labels mature, report by cohort and key segment:

- response prevalence
- PR AUC and ROC AUC
- precision, recall, lift, and responders captured at actual capacity
- Brier score, log loss, and calibration bands
- realized contact volume, gross margin, offer cost, and net value
- selection rate, opt-out rate, complaint rate, and delivery failures

## Retraining and rollback

Investigate retraining when two consecutive mature cohorts show any of:

- lift at capacity below 1.70x
- PR AUC more than 20% below the reference value
- absolute calibration gap above 5 percentage points in a material score band
- a material segment’s ROC AUC below 0.60

Immediately fall back to the documented targeting rule if consent enforcement fails, scores are stale, feature schema changes without approval, or output volume exceeds the capacity contract.

## Ownership

- CRM Operations owns consent, suppression, delivery, and capacity controls.
- Marketing Analytics owns business definitions and outcome maturity.
- ML Engineering owns feature, score, latency, and model-performance monitoring.
- Model Risk approves material feature, target, threshold, or model-family changes.
