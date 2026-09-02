# Predictive Analytics Methodology

## Purpose

Use this framework when the business needs to estimate a future outcome before it occurs and can take a meaningful action based on that prediction.

The methodology is designed for practical business modeling rather than model-building in isolation.

---

## 1. Frame the business decision

Document the decision the model is intended to improve.

Required questions:
- What decision will the prediction support?
- Who will use the prediction?
- What action will be taken?
- How often will scoring occur?
- What operational capacity or budget constraints exist?
- What happens if the model is wrong?

Do not begin with model selection.

---

## 2. Define the prediction target

Specify the target precisely.

Include:
- event definition
- observation window
- prediction horizon
- eligible scoring population
- label-availability delay

Example:

> Among active PayWave customers on a weekly scoring date, predict whether the customer will record zero qualifying payment transactions during the following 30 days, using only information available up to the scoring date.

Avoid target definitions that cannot be reproduced consistently.

---

## 3. Define the unit of analysis

Possible units:
- customer
- account
- transaction
- merchant
- session
- product
- day/week/month

The unit must align with the action. If the retention team contacts customers, the modeling unit should normally be customer-level rather than transaction-level.

---

## 4. Build a leakage-safe analytical dataset

For every feature ask:

> Was this information available before the prediction cutoff?

Document:
- source tables
- event-time logic
- feature cutoff
- target window
- duplicate handling
- late-arriving data

Exclude leakage even if it improves performance.

---

## 5. Define evaluation criteria before training

For binary classification, choose metrics based on the decision.

Recommended evaluation set:
- target prevalence
- ROC AUC
- PR AUC
- precision
- recall
- F1 when useful
- confusion matrix
- calibration
- lift / gain
- precision@k and recall@k for capacity-constrained actions

Also define a business metric such as expected retained value or cost avoided.

---

## 6. Split data to reflect deployment

Prefer temporal validation when the model will predict the future from historical data.

Example:
- Train: oldest months
- Validation: later month(s)
- Test: most recent held-out month

Do not allow future observations from the same customer to leak into earlier scoring periods through feature construction.

A random split may be acceptable for stable, non-temporal problems, but the rationale should be explicit.

---

## 7. Validate data quality

Check at minimum:
- unique analytical units at each scoring date
- missingness
- invalid categories
- implausible numeric values
- duplicate records
- target consistency
- feature availability by time period
- class prevalence by split
- large temporal distribution shifts

Compare distributions across Train, Validation, and Test.

---

## 8. Establish baselines

Create at least one simple baseline before complex modeling.

Recommended baselines:
- majority class
- simple business rule
- logistic regression

The selected model should create measurable incremental value over the baseline.

---

## 9. Build a reproducible preprocessing pipeline

Preprocessing may include:
- missing-value imputation
- categorical encoding
- scaling where required
- feature transformations

Fit preprocessing only on the training data.

Package preprocessing with the model so training and production use the same logic.

---

## 10. Engineer business-relevant features

Features should reflect information available before scoring.

For customer inactivity prediction, useful feature families can include:

### Recency
- days since last transaction
- days since last app/session activity

### Frequency
- transactions in last 7/30/60 days
- active days in last 30 days

### Monetary
- payment volume
- average transaction value

### Behavioral change
- transaction-count trend
- decline from personal baseline
- recent failed-payment increase

### Customer relationship
- tenure
- product usage breadth
- support contacts

Document every feature definition.

---

## 11. Train candidate models

Use a deliberate model ladder rather than immediately selecting the most complex algorithm.

Example:
1. Logistic regression baseline
2. Random forest
3. Gradient boosting

Compare:
- predictive performance
- calibration
- stability
- interpretability
- runtime
- maintenance complexity

A small metric improvement may not justify major operational complexity.

---

## 12. Tune models without contaminating the test set

Use only Train/Validation data for:
- hyperparameter selection
- feature-selection decisions
- probability calibration selection
- threshold decisions

Reserve the Test set for final unbiased evaluation.

---

## 13. Evaluate discrimination

For classification, report at minimum:
- ROC AUC
- PR AUC

For imbalanced targets, emphasize PR AUC and ranking metrics rather than accuracy alone.

Also inspect whether performance is materially better than the baseline.

---

## 14. Evaluate probability calibration

Assess whether predicted risk corresponds to observed frequency.

Use:
- calibration curve
- Brier score
- decile-level observed vs predicted rates

If business decisions use probabilities directly, calibration can be as important as ranking quality.

---

## 15. Select an operational threshold or capacity policy

Do not default to 0.50.

Possible decision policies:

### Fixed threshold
Act when predicted probability exceeds a chosen threshold.

### Capacity-based
Rank scores and act on the top N or top X%.

### Value-based
Act when expected benefit exceeds expected action cost.

Threshold selection should use Validation data and reflect real operational constraints.

---

## 16. Evaluate business performance at the chosen policy

Report:
- customers selected
- precision
- recall
- lift
- false positives
- false negatives
- expected intervention cost
- expected benefit

Example:

If Retention can contact 5,000 customers weekly, evaluate model performance specifically at the top 5,000 scores.

---

## 17. Analyze segments

Evaluate important groups separately.

Examples:
- country
- device
- tenure
- customer-value tier

For each segment inspect:
- prevalence
- score distribution
- AUC / PR AUC
- precision/recall at policy threshold
- calibration

Large segment differences should influence deployment and monitoring.

---

## 18. Interpret model behavior

Use methods appropriate to the model:
- coefficients
- permutation importance
- feature importance
- SHAP values

Separate:
- **model driver:** feature strongly influences prediction
- **business lever:** intervention on the feature would change the outcome

The first does not prove the second.

---

## 19. Estimate business value

Build an explicit value model.

For retention:

`Expected value = selected customers × precision × intervention success rate × retained customer value − outreach cost`

Test multiple assumptions when intervention success or value is uncertain.

Use sensitivity analysis instead of false precision.

---

## 20. Final test evaluation

After model and policy choices are frozen, evaluate on the held-out Test set.

Report:
- target prevalence
- discrimination metrics
- calibration
- policy performance
- segment performance
- business-value estimate

Do not keep tuning after seeing Test results unless the Test set is retired and a new final holdout is created.

---

## 21. Deployment readiness

Before deployment confirm:
- every feature is available in production
- scoring latency meets requirements
- missing-value behavior is defined
- model and preprocessing are versioned
- scoring population is reproducible
- threshold/capacity logic is documented
- ownership is assigned

---

## 22. Monitoring and governance

Monitor:
- data quality
- missingness
- feature drift
- score distribution
- target prevalence
- calibration
- ROC/PR AUC when labels arrive
- precision/recall/lift at the operational policy
- segment performance
- business outcomes

Define warning and retraining thresholds before problems occur.

---

## 23. Recommendation framework

### Deploy
Use when model performance exceeds baseline, policy economics are favorable, segment behavior is acceptable, and deployment requirements are satisfied.

### Pilot
Use when model is promising but real-world intervention effectiveness or operational workflow still needs validation.

### Iterate
Use when model performance is insufficient, calibration is poor, features are unstable, or segment performance requires improvement.

### Do not deploy
Use when the model cannot outperform a simple baseline, leakage/label problems invalidate evaluation, business economics are unfavorable, or the prediction cannot support a useful action.

---

## Executive communication standard

Lead with:
1. business decision
2. target and scoring population
3. model performance versus baseline
4. who the model identifies at the proposed operating policy
5. expected business value
6. key limitations / risks
7. deployment recommendation

Technical model details should support the decision rather than dominate the main stakeholder story.