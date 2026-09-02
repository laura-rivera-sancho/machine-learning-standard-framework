# Stakeholder Readout — ML2 Customer Segmentation

[Download the five-slide executive PowerPoint](stakeholder_readout.pptx) for a non-technical presentation of the recommendation, model choice, personas, limitations, and activation plan.

## Recommendation

Adopt the four-segment K-means solution as a **planning and experimentation framework**, beginning with controlled tests. Do not use segment membership as an automatic treatment rule.

## What changed

The current RFM approach describes recency, frequency, and value with fixed cutoffs. ML2 adds engagement, digital mix, discount use, returns, average order value, and tenure, then tests whether the resulting groups are stable and operationally material.

## Evidence

- 5,966 customers receive one of four segments; there is no unassigned population.
- Bootstrap ARI is 0.846 and temporal assignment ARI is 0.717.
- The smallest group still represents 18.1% of customers.
- GMM and DBSCAN alternatives fail minimum-size or coverage expectations despite some stronger geometric metrics.

## Proposed tests

| Segment | Hypothesis | Primary measure | Guardrails |
|---|---|---|---|
| Champions | Recognition or early access improves repeat value | Incremental margin/customer | Opt-outs, offer cost |
| At Risk | Carefully timed win-back improves reactivation | Incremental reactivation | Complaints, contact cost |
| Digital Growth | Guided cross-sell accelerates second-category adoption | Incremental category adoption | Returns, unsubscribes |
| Deal Seekers | Threshold offers protect margin better than broad discounts | Incremental contribution margin | Conversion, discount cost |

## Decision gates

1. Confirm data-quality and stability thresholds on a real historical backtest.
2. Review persona language with marketing, privacy, and customer-experience owners.
3. Run randomized segment-specific pilots with a common holdout.
4. Scale only where incremental margin and guardrails meet predeclared thresholds.

## Limitations

These results are synthetic. Segment differences are descriptive, not causal. The model does not determine consent, eligibility, message content, contact frequency, or offer value.
