# PayWave Customer Inactivity Prediction — Predictive Analytics Case Study

## Company

**PayWave** is a fictional digital-payments company.

## Business context

PayWave has a large active customer base, but a subset of customers gradually reduce usage and then become inactive. The Retention team currently relies on broad campaigns and simple recency rules, which means outreach is often too late or directed to customers who were unlikely to disengage.

The business wants to prioritize customers who are genuinely at elevated risk before inactivity occurs.

## Business question

> Which currently active PayWave customers are most likely to become inactive during the next 30 days, and how should the Retention team prioritize limited weekly outreach capacity?

## Prediction target

At each scoring date, predict whether an eligible active customer will record **zero qualifying payment transactions during the following 30 days**.

### Positive class
`inactive_next_30d = 1`

The customer has zero qualifying payment transactions in the 30-day prediction horizon.

### Negative class
`inactive_next_30d = 0`

The customer records at least one qualifying payment transaction in the prediction horizon.

## Observation window

Features will be calculated using only information available before the scoring date.

Primary observation window:
- previous 60 days of customer behavior

Additional recency windows:
- previous 7 days
- previous 30 days

## Prediction horizon

- Next 30 days after the scoring date

## Analytical unit

One row represents one **eligible customer at a scoring date**.

The same synthetic customer may appear at multiple historical scoring dates, so temporal splitting and leakage controls are required.

## Eligible scoring population

A customer is eligible when:
- the account is open
- the customer has at least 90 days of tenure
- the customer has at least one qualifying transaction during the prior 60 days
- the customer is not already classified as inactive
- required feature history is available

## Business action

The Retention team can contact a maximum of approximately **5,000 customers per weekly scoring cycle**.

The operational decision is therefore not simply:

> Is predicted probability above 0.50?

Instead, the model should support a ranked outreach list based on expected inactivity risk and business value.

## Why prediction creates value

If the model works well, PayWave can:
- reach at-risk customers before they disengage
- reduce low-value retention contacts
- prioritize retention capacity
- improve campaign economics
- identify behavioral patterns associated with disengagement

The model itself does not prove which retention intervention will prevent inactivity. Intervention effectiveness would need separate experimental or causal evaluation.

## Success framework

### Model-quality metrics
- ROC AUC
- Precision-Recall AUC
- probability calibration / Brier score

### Operational metrics
At the top 5,000 highest-risk customers:
- precision@5,000
- recall@5,000
- lift@5,000
- expected inactive customers captured

### Business metric
Illustrative expected value of the outreach strategy using assumptions for:
- successful intervention rate
- retained customer value
- contact cost

## Baselines

Candidate models should be compared with:
1. simple recency-based business rule
2. logistic regression baseline

A more complex model should demonstrate meaningful incremental value.

## Model candidates

The case compares:
- Logistic Regression
- Random Forest
- Gradient Boosting

The objective is not to force the most complex model to win. Selection should consider performance, calibration, interpretability, stability, and deployment complexity.

## Temporal validation design

The synthetic history covers multiple monthly scoring cohorts.

Reference split:
- **Training:** earlier scoring months
- **Validation:** subsequent scoring month(s)
- **Test:** most recent held-out scoring period

This mirrors the production question: can a model trained on past behavior predict future customer inactivity?

## Intentional analytical challenges

The synthetic case includes realistic modeling complications.

### 1. Class imbalance
Only a minority of eligible customers become inactive during the prediction horizon, making accuracy misleading.

### 2. Temporal drift
Customer behavior and target prevalence will shift modestly over time.

### 3. Repeated customers
Customers may appear in more than one scoring cohort, requiring careful feature construction and temporal evaluation.

### 4. Leakage candidates
The raw training dataset includes fields that appear highly predictive but are not valid at scoring time. The analyst must identify and exclude them.

### 5. Missing values
Some behavioral features will contain realistic missingness that must be handled reproducibly.

### 6. Non-linear risk
Inactivity risk will rise non-linearly with recency and recent behavioral decline.

### 7. Segment differences
Newer-vs-longer-tenure customers and selected markets will have different baseline risk and potentially different model performance.

### 8. Calibration
The strongest-ranking model will not necessarily be the best-calibrated model.

### 9. Capacity constraint
The Retention team can act on only a small fraction of the scored population, so top-k performance matters more than a generic 0.50 threshold.

## Expected analytical tasks

The analyst should:

1. frame the prediction target and scoring policy
2. validate data quality
3. identify and remove leakage
4. inspect class prevalence and temporal drift
5. create a temporal Train/Validation/Test split
6. build a simple business-rule baseline
7. build a reproducible preprocessing pipeline
8. train logistic-regression, random-forest, and gradient-boosting candidates
9. compare ROC AUC and PR AUC
10. assess probability calibration
11. evaluate precision, recall, and lift at the outreach capacity
12. inspect confusion-matrix trade-offs
13. evaluate important segments
14. interpret model drivers cautiously
15. estimate business value using explicit assumptions
16. select a model and operational policy
17. define monitoring and retraining requirements
18. provide a stakeholder recommendation

## Decision framework

### Deploy / Pilot
Use when the selected model materially improves targeting over the baseline, provides acceptable calibration/stability, and has favorable operational economics.

### Iterate
Use when ranking is promising but calibration, segment performance, feature reliability, or business value is insufficient.

### Do not deploy
Use when results rely on leakage, the model does not outperform the baseline meaningfully, or the Retention action does not create enough expected value.

## Portfolio objective

This case is designed to demonstrate the difference between:

> **Building a model with good predictive metrics**

and

> **Designing a predictive decision system that can be used responsibly in the business.**

The portfolio should show target design, leakage prevention, temporal validation, model comparison, calibration, operational thresholding, business impact, and monitoring — not only model training.

## Disclaimer

PayWave, its customers, data, model results, retention workflow, and business assumptions are entirely fictional and synthetic. The case is designed for education and portfolio demonstration only.
