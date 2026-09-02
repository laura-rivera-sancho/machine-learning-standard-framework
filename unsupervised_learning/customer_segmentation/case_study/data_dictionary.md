# Data Dictionary

All data are deterministic and synthetic. Each row represents one customer at one snapshot.

| Field | Type | Used in model | Definition / control |
|---|---|---:|---|
| `customer_id` | string | No | Synthetic stable identifier |
| `snapshot_date` | date | No | Observation cutoff; prevents future-data use |
| `recency_days` | integer | Yes | Days since most recent purchase; must be non-negative |
| `frequency_12m` | integer | Yes | Completed orders in trailing 12 months |
| `monetary_12m` | decimal | Yes | Net trailing-12-month merchandise value |
| `avg_order_value` | decimal | Yes | Average completed-order value |
| `discount_order_share` | rate | Yes | Share of orders using a discount, bounded 0–1 |
| `email_engagement_rate` | rate | Yes | Historical eligible-email engagement rate, bounded 0–1 |
| `digital_order_share` | rate | Yes | Share of orders placed digitally, bounded 0–1 |
| `return_rate` | rate | Yes | Historical returned-order share, bounded 0–1 |
| `tenure_days` | integer | Yes | Days since first recorded purchase |
| `synthetic_profile_truth` | category | No | Generator-only diagnostic; never available in real deployment |
| `marketing_consent` | binary | No | Activation eligibility control, not a behavioral feature |
| `region` | category | No | Retained for descriptive checks; excluded from clustering |

## Quality rules

Uniqueness is enforced on customer and snapshot. Negative recency, out-of-range rates, and duplicates are removed. Missing behavioral values are median-imputed within the preprocessing pipeline and monitored as a data-quality signal.
