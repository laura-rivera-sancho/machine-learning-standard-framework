# PayWave Synthetic Data Dictionary

The dataset is customer-at-scoring-date level. One row represents an eligible customer evaluated on a historical scoring date using only information available at that time.

| Field | Type | Description |
|---|---|---|
| `customer_id` | string | Synthetic customer identifier. A customer may appear in multiple scoring cohorts. |
| `scoring_date` | date | Historical date on which the prediction would have been made. |
| `country` | category | Synthetic market: US, MX, CR, or BR. |
| `device_type` | category | Primary recent device: Mobile or Desktop. |
| `customer_tenure_days` | integer | Days since account opening as of the scoring date. |
| `customer_value_tier` | category | Low, Medium, or High value grouping derived from prior activity. |
| `days_since_last_transaction` | integer | Recency of the last qualifying transaction before the scoring date. |
| `transactions_7d` | integer | Number of qualifying transactions in the 7 days before scoring. |
| `transactions_30d` | integer | Number of qualifying transactions in the 30 days before scoring. |
| `transactions_60d` | integer | Number of qualifying transactions in the 60 days before scoring. |
| `active_days_30d` | integer | Number of days with at least one qualifying transaction in the prior 30 days. |
| `payment_volume_30d_usd` | float | Total qualifying payment volume in the prior 30 days. |
| `avg_transaction_value_30d` | float | Average qualifying transaction value during the prior 30 days. |
| `transaction_count_change_30d_vs_prior30d` | float | Relative or normalized change in transaction count between the most recent 30-day window and the preceding 30-day window. |
| `payment_volume_change_30d_vs_prior30d` | float | Change in payment volume between recent and preceding 30-day windows. |
| `failed_transactions_30d` | integer | Number of failed/declined qualifying attempts during the prior 30 days. |
| `support_contacts_30d` | integer | Number of support contacts in the prior 30 days. |
| `login_days_30d` | integer | Number of distinct days with app/web login activity during the prior 30 days. |
| `products_used_60d` | integer | Number of distinct PayWave product/features used in the prior 60 days. |
| `marketing_engagement_30d` | float | Synthetic recent engagement score derived only from pre-scoring activity. |
| `inactive_next_30d` | binary | Prediction target. 1 if zero qualifying payment transactions occur during the next 30 days; otherwise 0. |

## Deliberate leakage fields in the raw training data

The raw dataset intentionally contains several fields that **must not be used as predictors** because they are generated after the scoring date or directly reveal the target.

| Field | Why invalid |
|---|---|
| `transactions_next_30d` | Directly uses the target horizon. |
| `future_inactivity_status` | Direct target proxy recorded after the outcome is known. |
| `retention_case_opened_after_score` | Downstream business action that occurs after scoring and may be influenced by future information. |

The guided workflow should explicitly identify and remove these fields before modeling.

## Target definition

### `inactive_next_30d`

`1` when the eligible customer records zero qualifying payment transactions during the 30 days following the scoring date.

`0` otherwise.

The target should never be reconstructed using information that overlaps the feature observation window.

## Feature families

### Recency
- `days_since_last_transaction`

### Frequency
- `transactions_7d`
- `transactions_30d`
- `transactions_60d`
- `active_days_30d`

### Monetary / value
- `payment_volume_30d_usd`
- `avg_transaction_value_30d`
- `customer_value_tier`

### Behavioral change
- `transaction_count_change_30d_vs_prior30d`
- `payment_volume_change_30d_vs_prior30d`

### Friction / service
- `failed_transactions_30d`
- `support_contacts_30d`

### Engagement
- `login_days_30d`
- `products_used_60d`
- `marketing_engagement_30d`

### Customer context
- `country`
- `device_type`
- `customer_tenure_days`

## Synthetic behavior

The generator intentionally encodes:
- minority positive-class prevalence
- increasing inactivity risk with greater transaction recency
- elevated risk when recent transaction frequency/volume declines
- non-linear recency effects
- lower risk with stronger login/product engagement
- modest market and tenure differences
- mild temporal drift in customer behavior and target prevalence
- missing values in selected behavioral features
- repeated customers across historical scoring cohorts
- leakage columns that appear deceptively predictive

## Data-quality checks expected

Before modeling, validate at minimum:
- uniqueness of `customer_id` + `scoring_date`
- duplicate rows
- date parsing and chronological order
- target values restricted to 0/1
- missingness by feature and scoring period
- impossible negative counts
- impossible recency/tenure values
- consistency among rolling-window counts
- target prevalence by scoring cohort
- feature distribution drift over time
- invalid/unexpected categorical values
- leakage fields

## Temporal split

The generated case will contain multiple monthly or weekly historical scoring cohorts. The modeling workflow should split cohorts chronologically into:

- Training
- Validation
- Test

The supplied workflow uses January-May 2026 for Train, June-July 2026 for Validation, and August 2026 for Test.

## Operational evaluation

Because Retention can contact only about 5,000 customers per scoring cycle, model evaluation should include ranking metrics at the equivalent capacity level:

- precision@k
- recall@k
- lift@k
- number of true inactive customers captured

This operational policy is more relevant than applying a default probability threshold of 0.50.

## Important modeling note

All transformations, imputations, encoders, scalers, and learned preprocessing parameters must be fit using training data only and then applied unchanged to Validation and Test.
