# Campaign Response Data Dictionary

The unit of analysis is one eligible customer at one monthly campaign scoring date. Every feature is computed using information available before campaign assignment.

| Field | Role | Definition and timing |
|---|---|---|
| `customer_id` | Identifier | Synthetic customer identifier; not a model input |
| `scoring_date` | Split/governance | Monthly feature cutoff and campaign assignment date |
| `campaign_id` | Identifier | Synthetic campaign cohort identifier |
| `region` | Feature | Operational region known before scoring |
| `preferred_channel` | Feature | Previously observed preferred channel |
| `loyalty_tier` | Feature | Loyalty status effective at scoring |
| `customer_tenure_days` | Feature | Days since customer start date |
| `recency_days` | Feature | Days since most recent qualifying purchase |
| `orders_180d` | Feature | Qualifying orders in the preceding 180 days |
| `spend_180d` | Feature | Gross merchandise value in the preceding 180 days |
| `average_order_value_180d` | Feature | Mean order value in the preceding 180 days |
| `email_open_rate_90d` | Feature | Historical email opens divided by delivered messages in the preceding 90 days |
| `email_click_rate_90d` | Feature | Historical clicks divided by delivered messages in the preceding 90 days |
| `site_sessions_30d` | Feature | Web/app sessions in the preceding 30 days |
| `prior_campaigns_12m` | Feature | Campaigns delivered in the preceding 12 months |
| `prior_campaign_responses_12m` | Feature | Responses to campaigns delivered before the scoring date |
| `days_since_last_campaign` | Feature | Days since the latest prior campaign contact |
| `discount_share_180d` | Feature | Share of prior-180-day orders using a discount |
| `margin_rate_180d` | Feature/value | Historical realized margin rate; available before scoring |
| `marketing_consent` | Eligibility | Must equal 1; enforced before scoring and outside the model |
| `contact_suppressed` | Eligibility | Must equal 0; enforced before scoring and outside the model |
| `responded_within_14d` | Target | Qualifying response within 14 days after assignment |
| `response_order_value_14d` | Outcome-only | Post-campaign order value; prohibited as a feature, used only for retrospective value |
| `opened_current_campaign` | Leakage | Current campaign open; unavailable at scoring |
| `clicked_current_campaign` | Leakage | Current campaign click; unavailable at scoring |
| `response_probability_generator_only` | Generator-only | Synthetic latent probability; prohibited from all model inputs |

## Missingness policy

- Numeric engagement/value fields are median-imputed using Train-fitted values with missingness indicators.
- Categorical fields are most-frequent-imputed using Train-fitted values.
- Missing target, scoring date, or eligibility controls fail the scoring contract rather than being imputed.

## Data-quality controls

- uniqueness of `customer_id + scoring_date`
- valid dates and binary target
- nonnegative recency, tenure, counts, spend, and sessions
- normalized controlled categories
- consent and suppression eligibility
- explicit leakage-column detection
