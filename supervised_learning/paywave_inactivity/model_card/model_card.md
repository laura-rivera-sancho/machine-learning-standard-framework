# Model Card — PayWave Inactivity Risk

## Model details

| Attribute | Value |
|---|---|
| Model | Gradient Boosting binary classifier |
| Version | Portfolio transfer v1.0 |
| Owner | Retention Analytics / Customer Operations |
| Target | Inactivity within 30 days |
| Unit | Active customer at scoring date |
| Decision capacity | 5,000 customers per scoring cycle |
| Validation | Chronological Train, Validation, and Test cohorts |

## Intended use

- Rank active customers for human-reviewed retention outreach.
- Compare a model shortlist with the current recency rule at equal capacity.
- Support a controlled pilot with explicit economics and monitoring.

## Out-of-scope use

- Autonomous messaging or customer treatment
- Claims that outreach prevents inactivity
- Credit, employment, insurance, healthcare, or other high-impact decisions
- Use outside the documented population, horizon, or feature-timing contract

## Reference evaluation

At 5,000-customer capacity on the 29,999-customer Test cohort, the model captures 3,853 future-inactive customers with 77.06% precision, 42.99% recall, and 2.58x lift. The recency rule captures 3,301.

## Limitations

- Evidence is synthetic and does not establish real-world generalization.
- Prediction is not treatment effect; high-risk customers may not be persuadable.
- Historical policy can affect labels and behavioral features.
- Performance and calibration can change with product, market, or eligibility shifts.
- Excluding protected characteristics does not eliminate proxy risk.

## Controls and approval boundary

Keep consent, suppression, frequency caps, message selection, and campaign execution outside the model. Version scores and model artifacts, use a randomized pilot, monitor segment outcomes, and retain the recency rule as a rollback. A human owner approves every activation policy.
