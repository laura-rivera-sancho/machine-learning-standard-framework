# Campaign Response Modeling Methodology

## 1. Frame the decision

Document the campaign owner, eligible population, contact capacity, action, target horizon, costs, and acceptance criteria before examining model results.

## 2. Define the prediction contract

- Unit: customer at monthly scoring date
- Target: response within 14 days after a standardized campaign
- Observation cutoff: strictly before campaign assignment
- Population: marketable customers who pass consent and suppression controls
- Output: probability plus capacity-based rank

## 3. Establish the data contract

Classify every column as identifier, eligible feature, target, post-outcome field, or generator-only field. Validate schema, dates, ranges, duplicates, categories, missingness, and feature availability.

## 4. Preserve temporal order

Use early cohorts for training, later cohorts for selection, and the latest cohorts for testing. Keep Test isolated until the champion is selected.

## 5. Establish realistic baselines

Evaluate the current targeting rule alongside Logistic Regression. The rule represents current decision quality; Logistic Regression shows how far a transparent additive model can go.

## 6. Compare candidate models

Train the same leakage-safe feature set with a simple Decision Tree and a stronger tree ensemble. Select the champion on Validation PR AUC, with calibration as the tie-breaker.

## 7. Evaluate the held-out decision

Report ROC AUC, PR AUC, Brier score, log loss, precision, recall, lift, responders captured, and illustrative value at the declared capacity. Do not tune after Test results are visible.

## 8. Inspect calibration, segments, and drivers

Compare predicted and observed response across score bands. Review performance by loyalty tier and region. Use permutation importance as predictive—not causal—evidence.

## 9. Translate scores into operations

Apply consent, suppression, freshness, and capacity controls outside the model. Produce a versioned score with model version, scoring timestamp, and reason codes suitable for review.

## 10. Pilot and monitor

Run shadow scoring before customer contact. Then use a randomized pilot to measure incremental campaign impact. Monitor quality, drift, calibration, segments, value, opt-outs, and complaints; preserve a rule-based rollback.
