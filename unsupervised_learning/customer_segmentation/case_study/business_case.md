# Business Case — Behavioral Customer Segmentation

## Decision context

Northstar Market needs a small set of customer groups that can guide differentiated campaign design, lifecycle messaging, and measurement. Current RFM rules are useful for reporting but use fixed cutoffs and omit channel, engagement, discount, return, and tenure behavior.

## Decision contract

| Element | Definition |
|---|---|
| Decision | Which customer groups should receive distinct marketing hypotheses and test designs? |
| Unit | One eligible customer at a bi-monthly snapshot |
| Population | Customers with observable trailing-12-month behavior; consent is retained for activation checks, not clustering |
| Observation window | Trailing 12 months as of each snapshot |
| Refresh | Every two months after monitoring review |
| Users | CRM strategy, lifecycle marketing, customer analytics, and experimentation owners |
| Success | Stable, sizable, interpretable groups that produce measurably different test responses or operating decisions |

## Value hypothesis

Segmentation creates value only if it changes a decision. The reference activation hypotheses are:

- **Champions:** recognition, early access, and referral tests
- **At Risk:** suppression-aware win-back tests with strict contact-cost controls
- **Digital Growth:** onboarding and cross-sell journey tests
- **Deal Seekers:** margin-safe threshold and offer-structure tests

## Guardrails

- No protected personal characteristics are used.
- Region, consent, and the synthetic truth label are excluded from clustering features.
- Consent, suppression, frequency caps, and legal eligibility remain external controls.
- Segment membership is descriptive, not a causal response estimate or an individual judgment.
- Material actions require randomized holdouts and outcome measurement.
