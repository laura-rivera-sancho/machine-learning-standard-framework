# Campaign Response Propensity Fundamentals

This reference explains the concepts needed to design, evaluate, interpret, and operate a campaign-response propensity model.

## What propensity means

A response propensity is an estimated probability that an eligible customer will complete a defined outcome within a defined period. The unit is typically one customer at one scoring date; the response definition and horizon must be set for each decision.

The definition is incomplete unless it specifies:

- who is eligible to be scored
- the exact outcome that counts as a response
- the observation cutoff for every feature
- the prediction horizon
- the action taken from the score
- the capacity and cost of that action

## Propensity is not uplift

Propensity asks, “Who is likely to respond?” Uplift asks, “Whose response is caused by receiving the campaign?”

A high-propensity customer may purchase without contact. A low-propensity customer may still have a large incremental response to treatment. Propensity is appropriate for ranking likely responders when historical labels reflect a consistent campaign policy. Incremental targeting requires randomized treatment/control data and uplift or causal-effect methods.

## Leakage and feature timing

Leakage occurs when training data contain information unavailable at the scoring moment or information produced by the outcome itself. It creates unrealistic validation performance.

Examples of features that would leak information are:

- whether the current campaign was opened or clicked
- the response order value
- a response timestamp or fulfillment status
- a synthetic-data generator's hidden probability, if it would not exist at scoring time

Historical open and click rates are valid because they are calculated before the scoring date. Similar names do not imply similar availability; timing must be documented for each field.

## Why chronological validation matters

Randomly splitting repeated customer-campaign rows can place future observations from the same customer into training while earlier observations appear in testing. It also ignores seasonality, changing behavior, campaign fatigue, and policy drift.

Use earlier cohorts for training, later cohorts for model selection, and the latest representative cohort for a one-time test. Keep the test set untouched until the model family is selected. For a worked split, see the [case methodology](methodology.md).

## Baselines and candidates

A credible modeling case begins with the actual current decision rule, not with a weak dummy classifier.

Useful comparisons include:

- **Targeting rule:** transparent ranking based on recency, historical engagement, prior response, and sessions
- **Logistic Regression:** interpretable additive probability baseline
- **Decision Tree:** simple nonlinear model that exposes split-based logic
- **HistGradientBoosting:** stronger tree ensemble that can learn interactions and nonlinear thresholds

The most complex model should win only when validation evidence justifies it.

## Metrics and their interpretation

### ROC AUC

ROC AUC measures how often a randomly selected responder receives a higher score than a randomly selected non-responder. It evaluates ranking over all thresholds but can look optimistic when the positive class is uncommon.

### Precision–Recall AUC

PR AUC emphasizes performance on responders. Its naive baseline is the response prevalence, so it should always be interpreted relative to that prevalence.

### Precision at capacity

If only the top 20% can be contacted, precision at capacity is the share of selected customers who respond:

`responders in selected group / selected customers`

### Recall at capacity

Recall at capacity is the share of all responders captured within the contact limit:

`responders in selected group / all responders`

### Lift at capacity

Lift compares selected precision with the population response rate:

`precision at capacity / population response rate`

A lift of 2 means the selected group responds at twice the overall rate. This is a ranking comparison, not an estimate of the campaign's causal effect.

### Brier score and log loss

Ranking metrics do not prove that probabilities are reliable. Brier score measures squared probability error; log loss penalizes confident mistakes more strongly. Lower is better for both.

## Calibration

A calibrated score of 0.20 should correspond to roughly a 20% response rate across comparable observations. Calibration matters for forecasting volume, computing expected value, setting probability thresholds, and communicating uncertainty.

Review calibration overall, through time, and by operational segment. A model can rank well while systematically overpredicting. Check calibration before using scores for probability-based forecasts or automated decisions.

## Threshold and capacity design

The operating point should be derived from business constraints rather than defaulting to 0.50. Common policies include:

- top `K` customers under fixed capacity
- every customer with positive expected value
- a probability threshold subject to channel and consent constraints
- separate capacity allocations by channel or region

Eligibility and suppression rules should remain deterministic controls outside the model.

## Model interpretation

Permutation importance measures how much evaluation performance falls when a feature is disrupted. It helps identify influential inputs but does not show causality or the direction of effect. Correlated features can share or mask importance.

Inputs such as historical engagement, campaign spacing, and recency may help prediction. Their importance does not prove that changing them will cause a response.

## Segment evaluation and responsible use

Performance should be checked across relevant operational groups such as region, channel, and loyalty tier. Differences can arise from sample size, base rates, data quality, customer experience, or policy history.

Excluding protected or sensitive attributes does not guarantee fairness because other variables can act as proxies. Review selection rates, errors, customer impact, and complaint or opt-out outcomes across relevant groups where lawful and appropriate.

## Drift and monitoring

Monitor four layers:

1. **Data quality:** schema, freshness, missingness, ranges, duplicates, and consent controls
2. **Feature and score drift:** distribution changes and population stability
3. **Model quality:** PR AUC, lift, calibration, segment behavior, and realized value after labels mature
4. **Operations:** volume, delivery failures, opt-outs, complaints, and latency

Retraining should be triggered by evidence—not by an arbitrary calendar alone. Roll back to the documented rule if eligibility controls fail, scores are stale, or model quality breaches agreed thresholds.

## Practical analytical questions

- Is the target defined at the same point in time as the real scoring decision?
- Are all features available before campaign assignment?
- Does the split reproduce future deployment conditions?
- Does the model beat the current rule at the actual contact capacity?
- Are probabilities calibrated well enough for value calculations?
- Which segments have weaker performance or higher customer risk?
- Would an uplift design be more appropriate than propensity?
- What happens when data are stale, labels are delayed, or capacity changes?
