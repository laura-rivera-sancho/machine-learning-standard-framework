# Model Card — ML2 Customer Segmentation

## Model details

| Attribute | Value |
|---|---|
| Model | K-means, four clusters |
| Version | Portfolio reference v1.0 |
| Owner | Customer Analytics / Lifecycle Marketing |
| Unit | Customer at bi-monthly snapshot |
| Features | Nine trailing-behavior measures |
| Reference snapshot | August 31, 2026 |
| Refresh | Bi-monthly after analyst approval |

## Intended use

- Structure lifecycle strategy and customer reporting.
- Generate differentiated marketing hypotheses.
- Stratify or analyze randomized experiments.
- Support human-reviewed audience planning.

## Out-of-scope use

- Autonomous targeting, pricing, eligibility, or suppression
- High-impact decisions such as credit, employment, insurance, or healthcare
- Claims that a segment causes response or business value
- Permanent customer identity or individual-level worth judgments
- Use outside the documented feature and snapshot contract

## Reference evaluation

The synthetic reference run segments 5,966 customers with 100% coverage, silhouette 0.245, bootstrap ARI 0.846, temporal assignment ARI 0.717, and an 18.1% minimum segment share.

## Risks and limitations

- Synthetic evidence does not establish real-world utility.
- Segment structure depends on feature selection, scaling, and time window.
- K-means favors compact groups and hard assignments.
- Campaigns can alter the behaviors used in later snapshots.
- Names may invite stereotypes or overgeneralization.
- Excluding protected attributes does not eliminate proxy or allocation risk.

## Controls

- Keep consent, suppression, and activation eligibility external.
- Version preprocessing, centroids, names, and snapshot dates.
- Review distribution, stability, and profile changes before publishing.
- Measure outcomes with randomized holdouts and customer-experience guardrails.
- Provide a governed RFM fallback when stability gates fail.

## Approval boundary

The model may assign a descriptive segment. A human owner must approve names, activation hypotheses, experiment designs, and any customer-facing use.
