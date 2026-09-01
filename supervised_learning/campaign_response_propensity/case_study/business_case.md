# Harbor & Pine Campaign Response Business Case

## Situation

Harbor & Pine is a fictional omnichannel retailer. Its CRM team runs a monthly retention campaign but can contact only 20% of the eligible customer population because of budget and channel-pressure limits.

The current targeting rule prioritizes recent customers with strong historical email engagement and prior campaign response. The team wants to know whether a supervised model can identify more likely responders without increasing contact volume.

## Decision owner and users

- Decision owner: Director of CRM and Lifecycle Marketing
- Primary users: campaign operations, marketing analytics, and model-risk reviewers
- Decision: approve a model for shadow scoring and a controlled randomized pilot

## Prediction contract

| Element | Definition |
|---|---|
| Unit | One eligible customer at one monthly scoring date |
| Target | At least one qualifying response within 14 days after campaign assignment |
| Positive class | `responded_within_14d = 1` |
| Feature cutoff | Before campaign assignment on the scoring date |
| Scoring population | Consented customers who are not suppressed and have at least 30 days of tenure |
| Action | Rank customers for a campaign with 20% contact capacity |
| Refresh | Monthly |

## Acceptance criteria

The selected model must:

1. beat the current targeting rule on Validation PR AUC
2. capture at least 5% more responders than the rule at identical Test capacity
3. document probability calibration and segment behavior
4. exclude current-campaign outcomes, generator-only fields, and protected characteristics
5. produce reproducible results and pass automated tests
6. retain deterministic consent, suppression, and capacity controls outside the model

## Constraints and assumptions

- The dataset is synthetic and represents a standardized campaign policy.
- Response labels describe association under that policy, not incremental treatment effect.
- Contact and offer economics are illustrative, not a financial forecast.
- Consent and suppression are eligibility rules, never model optimization variables.
- No live customer activation is implemented.

## Recommended decision path

1. Validate the model through time against the current rule.
2. Run shadow scoring to verify data freshness and operational volume.
3. Conduct a randomized pilot within the eligible population.
4. Measure incremental impact, opt-outs, complaints, and segment outcomes.
5. Scale only if the randomized evidence and monitoring gates pass.
