# Predictive Analytics Fundamentals

## What is predictive analytics?

Predictive analytics uses historical and current data to estimate the probability or expected value of a future outcome.

Examples:
- Which customers are likely to become inactive in the next 30 days?
- Which transactions are likely to be fraudulent?
- How much demand should we expect next week?
- Which leads are most likely to convert?

The objective is not simply to build a model. The objective is to improve a decision made before the outcome occurs.

---

## Prediction vs explanation vs causation

These are different analytical goals.

### Prediction
Who or what is likely to experience an outcome?

### Explanation
Which variables are associated with the outcome?

### Causation
What would happen if the business changed something?

A variable can be highly predictive without being causal. Feature importance should therefore not be interpreted automatically as a lever that will change the outcome.

---

## Common predictive problem types

### Binary classification
Predict one of two outcomes.

Examples:
- churn / no churn
- fraud / legitimate
- convert / not convert

Typical outputs are probabilities between 0 and 1.

### Multiclass classification
Predict one of several categories.

Examples:
- likely next product
- reason for contact
- risk tier

### Regression
Predict a continuous numeric value.

Examples:
- transaction amount
- customer lifetime value
- handling time

### Time-series forecasting
Predict future values over time.

Examples:
- daily contacts
- weekly revenue
- staffing demand

### Ranking / propensity scoring
Order entities by expected likelihood or value.

Examples:
- customers most likely to respond to an offer
- accounts most likely to require intervention

---

## Target definition

The target is the outcome the model is designed to predict.

A good target definition specifies:
- what the event is
- when it is measured
- the observation window used for features
- the prediction horizon
- who is eligible to be scored

Example:

> Predict whether an active PayWave customer will have **zero qualifying transactions during the next 30 days**, using only information available up to the scoring date.

Small changes in the target definition can create a very different modeling problem.

---

## Observation window and prediction horizon

The **observation window** is the historical period used to construct features.

The **prediction horizon** is the future period in which the target is measured.

Example:
- Previous 60 days = observation window
- Next 30 days = prediction horizon

There must be a clear cutoff between what the model knows and what it is trying to predict.

---

## Data leakage

Leakage occurs when model features contain information that would not actually be available at prediction time or that directly reveals the future target.

Examples:
- using a cancellation status recorded after the prediction date to predict cancellation
- using a support case opened after churn already occurred
- computing a 30-day future transaction count and including it as a feature

Leakage can produce extremely strong validation results that collapse in production.

A core validation question is:

> Could this feature have been known at the moment the prediction would have been made?

---

## Train, validation, and test sets

### Training set
Used to fit model parameters.

### Validation set
Used to compare models, tune hyperparameters, or select thresholds.

### Test set
Held back until the modeling decisions are largely complete and used for final performance estimation.

For time-dependent business problems, a temporal split is often more realistic than a purely random split because production always predicts the future from the past.

---

## Why a baseline model matters

A complex model should outperform a simple reference.

Possible baselines:
- majority-class prediction
- historical average
- simple business rule
- logistic regression
- previous production model

Without a baseline, it is difficult to know whether additional model complexity creates meaningful value.

---

## Class imbalance

Many useful business outcomes are uncommon.

Examples:
- fraud rate = 0.5%
- churn rate = 8%
- default rate = 3%

A model predicting the majority class every time could have high accuracy and still be useless.

Therefore, accuracy is often not an appropriate primary metric for imbalanced classification.

---

## Confusion matrix

For binary classification:

| | Actual Positive | Actual Negative |
|---|---:|---:|
| Predicted Positive | True Positive (TP) | False Positive (FP) |
| Predicted Negative | False Negative (FN) | True Negative (TN) |

These four outcomes define most classification metrics.

---

## Precision and recall

### Precision
Of the cases we flagged, how many were truly positive?

`Precision = TP / (TP + FP)`

Use when false positives are costly or operational capacity is limited.

### Recall / Sensitivity
Of all true positive cases, how many did we identify?

`Recall = TP / (TP + FN)`

Use when missing a positive case is costly.

There is usually a trade-off between precision and recall.

---

## Specificity

Of all actual negative cases, how many were correctly identified as negative?

`Specificity = TN / (TN + FP)`

This can matter when false alarms create customer friction or operational cost.

---

## F1 score

The F1 score is the harmonic mean of precision and recall.

It is useful when both false positives and false negatives matter, but it should not replace a business-specific cost analysis.

---

## ROC AUC

ROC AUC measures how well the model ranks positive cases above negative cases across thresholds.

Interpretation:
- 0.5 ≈ random ranking
- 1.0 = perfect discrimination

ROC AUC is useful for overall ranking quality but can look strong even when the positive class is very rare.

---

## Precision-Recall AUC

Precision-Recall AUC focuses on performance for the positive class and is often more informative than ROC AUC for strongly imbalanced problems.

Always compare PR AUC with the base positive rate because a rare target naturally creates a low baseline precision.

---

## Probability calibration

A model is calibrated when predicted probabilities correspond to observed outcome rates.

Example:

Among customers assigned a risk probability near 0.70, approximately 70% should eventually experience the target outcome.

Calibration matters when probabilities are used for:
- risk tiers
- expected-value calculations
- resource planning
- threshold decisions

A model can rank customers well but still produce poorly calibrated probabilities.

---

## Threshold selection

Most classifiers output probabilities, not business decisions.

A threshold converts probability into an action.

Example:
- score >= 0.60 → send to retention team
- score < 0.60 → no intervention

The best threshold depends on:
- outreach capacity
- cost of intervention
- value of preventing the outcome
- false-positive cost
- required recall or precision

The default 0.50 threshold is rarely automatically the best business threshold.

---

## Top-k / capacity-based targeting

Many businesses cannot act on everyone above a fixed probability threshold.

If the team can contact only 10,000 customers per week, the operational policy may simply be:

> Rank eligible customers by predicted risk and contact the top 10,000.

Useful evaluation measures then include:
- precision at k
- recall at k
- lift at k
- gain charts

---

## Lift

Lift compares the target rate in a selected high-risk group with the overall population rate.

Example:
- Overall inactivity rate = 10%
- In top 10% model-risk group = 30%
- Lift at 10% = 3.0x

Lift is often easier for stakeholders to understand than abstract model metrics.

---

## Feature engineering

Feature engineering converts raw data into predictive signals.

Common customer-risk features include:
- recency
- frequency
- monetary value
- trend in activity
- failed transactions
- support contacts
- tenure
- product usage
- payment-method mix
- behavioral change relative to the customer's own baseline

Features must be reproducible and available at scoring time.

---

## Missing values

Missingness may be:
- random
- operationally meaningful
- caused by tracking/data defects

A missing value can itself contain signal, but the treatment must be consistent between training and production.

Document:
- imputation rules
- missing indicators
- fields excluded due to unreliable coverage

---

## Categorical variables

Common handling approaches include:
- one-hot encoding
- ordinal encoding when a real order exists
- native categorical handling in some tree models

Avoid creating an artificial numeric order when categories are nominal.

---

## Scaling

Some models such as logistic regression with regularization, distance-based methods, and neural networks often benefit from feature scaling.

Tree-based models generally do not require standardized numeric features.

The preprocessing pipeline must be learned from the training data only.

---

## Common model families

### Logistic regression
Strengths:
- interpretable
- fast
- strong baseline
- naturally outputs probabilities

### Decision tree
Strengths:
- intuitive rules
- non-linear relationships

Weakness:
- can overfit easily

### Random forest
Strengths:
- captures non-linearities and interactions
- robust general-purpose model

### Gradient boosting
Examples include XGBoost, LightGBM, and CatBoost.

Strengths:
- often excellent performance on structured/tabular data

Trade-off:
- greater tuning and interpretation complexity

### Neural networks
Powerful for some problems, especially large or unstructured datasets, but not automatically superior for ordinary tabular business data.

Model selection should be driven by the problem, data, performance, interpretability, operational constraints, and governance requirements.

---

## Overfitting

Overfitting occurs when a model learns patterns specific to the training data that do not generalize.

Warning signs:
- excellent training performance but weak validation performance
- very complex model relative to available data
- unstable segment results
- extreme sensitivity to small data changes

Controls include:
- validation/test splits
- cross-validation when appropriate
- regularization
- simpler models
- early stopping
- feature reduction

---

## Hyperparameter tuning

Hyperparameters control model behavior before training.

Examples:
- tree depth
- learning rate
- number of trees
- regularization strength

Tuning must happen using training/validation data, not the final test set.

---

## Model interpretability

Interpretability helps answer:
- Why is the model scoring cases this way?
- Which features drive predictions overall?
- What factors contribute to an individual score?

Possible tools:
- logistic regression coefficients
- feature importance
- permutation importance
- partial dependence
- SHAP values

Interpretability explains model behavior, not necessarily causal effects.

---

## Segment performance

A model can perform well overall but poorly for specific groups.

Evaluate important segments such as:
- geography
- tenure
- product type
- acquisition channel
- customer value tier

Compare metrics such as:
- target prevalence
- AUC
- precision/recall at operational threshold
- calibration
- score distribution

This is important for both business effectiveness and model governance.

---

## Temporal stability and drift

Production data changes.

### Data drift
Feature distributions change.

### Concept drift
The relationship between features and target changes.

### Performance drift
Model effectiveness declines over time.

Monitoring can include:
- score distribution
- feature distributions
- missingness
- target prevalence
- calibration
- discrimination
- precision/recall at the business threshold

---

## Retraining

Retraining may be triggered by:
- scheduled cadence
- sufficient new labeled data
- material feature drift
- performance deterioration
- major product/process changes

Retraining should be governed rather than automatic without validation.

---

## Business value

A model should eventually connect to value.

For a retention model, value may depend on:

`Customers contacted × precision × intervention success rate × retained value − outreach cost`

Model evaluation therefore needs both statistical metrics and an operational value framework.

---

## When predictive modeling is not appropriate

Do not build a predictive model simply because data exist.

A model may not be appropriate when:
- there is no clear future target
- the outcome cannot be acted upon
- data available at prediction time are insufficient
- the target is too rare for reliable learning
- labels are unreliable
- a simple deterministic business rule already solves the problem
- deployment cost exceeds expected value
- the real question is causal rather than predictive

---

## Common failure modes

1. Target leakage
2. Random splitting when production is temporal
3. Using accuracy for a highly imbalanced target
4. Tuning on the test set
5. Selecting a threshold without business context
6. Ignoring probability calibration
7. Ignoring operational capacity
8. Treating feature importance as causation
9. Reporting only aggregate model performance
10. Failing to compare against a simple baseline
11. Training features that cannot be recreated in production
12. No model monitoring plan

---

## Key takeaway

A strong predictive analytics project answers four questions:

1. **Can we predict the outcome reliably before it happens?**
2. **Can we identify the right cases for action?**
3. **Will acting on those predictions create enough business value?**
4. **Can the model be deployed, monitored, and governed safely and consistently?**