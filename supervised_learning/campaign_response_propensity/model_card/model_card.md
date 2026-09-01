# Model Card — ML1 Campaign Response Propensity

## Model details

| Attribute | Value |
|---|---|
| Model | HistGradientBoosting binary classifier |
| Version | Portfolio reference v1.0 |
| Owner | Marketing ML / CRM Analytics |
| Target | Response within 14 days |
| Unit | Eligible customer at monthly scoring date |
| Training period | Sep 2025–Jun 2026 after model selection/refit |
| Test period | Jul–Aug 2026 |
| Refresh | Monthly scoring; retraining only after review |

## Intended use

- Rank consented, non-suppressed customers for a standardized retention campaign.
- Support a fixed-capacity shortlist and controlled pilot.
- Provide probability, rank, model version, and scoring timestamp for review.

## Out-of-scope use

- Autonomous message delivery or campaign execution
- Eligibility, consent, suppression, or frequency-cap decisions
- Credit, employment, insurance, healthcare, or other high-impact decisions
- Causal claims about campaign incrementality
- Individual customer worth or long-term value judgments
- Scoring data outside the documented feature and timing contract

## Data

The reference dataset is deterministic and synthetic. Features describe prior purchase behavior, historical engagement, campaign history, loyalty, and operational region. Current-campaign actions and outcomes are excluded from inputs.

Protected or sensitive personal characteristics are not included. Proxy and allocation risks still require outcome monitoring.

## Evaluation

On the 11,993-row chronological Test set:

- ROC AUC: 0.7108
- PR AUC: 0.2201 at 8.01% prevalence
- Brier score: 0.0693
- Precision at 20% capacity: 18.30%
- Recall at 20% capacity: 45.68%
- Lift at 20% capacity: 2.28x
- Responders captured: 439, versus 392 for the current rule

## Explainability

Permutation importance is reported at the original feature level. It describes predictive dependence, not causality, and can understate correlated features. Operational explanations should use approved reason-code groupings and never expose raw behavioral detail unnecessarily.

## Limitations

- Synthetic evidence does not establish real-world generalization.
- Response labels reflect a campaign policy rather than randomized treatment assignment.
- Highest score bands show modest overprediction.
- Performance varies with segment base rate and sample composition.
- Economic estimates are illustrative and retrospective.

## Required controls

- consent, suppression, and capacity checks outside the model
- immutable model version and scoring timestamp
- feature freshness and schema validation
- shadow scoring before customer use
- randomized pilot before claims of incremental value
- cohort and segment monitoring after labels mature
- documented rollback to the current targeting rule

## Approval boundary

The model can prepare a ranked audience only. Campaign activation remains an owned operational decision subject to marketing policy, legal requirements, and human approval.
