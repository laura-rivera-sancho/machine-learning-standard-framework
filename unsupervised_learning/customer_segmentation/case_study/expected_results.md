# Expected and Reference Results

## Selection criteria

A production candidate should provide at least 90% coverage, no segment below 5% of the eligible base, bootstrap ARI of at least 0.75, defensible separation, and interpretable profiles. Candidate selection therefore does not maximize silhouette alone.

## Reference result

K-means with four clusters is selected:

| Measure | Result | Interpretation |
|---|---:|---|
| Customers segmented | 5,966 | Current cleaned snapshot |
| Coverage | 100% | Every eligible record receives a segment |
| Silhouette | 0.245 | Moderate separation, realistic for overlapping customer behavior |
| Bootstrap stability ARI | 0.846 | Robust to resampling |
| Temporal assignment ARI | 0.717 | Most structure persists across snapshots despite behavioral noise |
| Smallest segment | 18.1% | Operationally material; no micro-segment |
| Synthetic-truth ARI | 0.613 | Diagnostic only; confirms partial recovery of generator structure |

GMM four- and five-component candidates produce slightly higher separation in places but create a sub-3% segment, failing the operational-size gate. DBSCAN produces strong separation among retained points but either excludes too many customers or creates a very small cluster. K-means five is highly stable, yet adds complexity without improving separation.

## Segment profiles

| Segment | Share | Recency | Orders | Annual value | Primary interpretation |
|---|---:|---:|---:|---:|---|
| Champions | 32.5% | 18.9 days | 14.3 | $1,889 | High-value, frequent, engaged customers |
| At Risk | 26.9% | 171.8 days | 2.7 | $223 | Long-tenured but inactive, low-engagement customers |
| Digital Growth | 22.5% | 50.1 days | 7.2 | $597 | Newer, digital-first customers with growth potential |
| Deal Seekers | 18.1% | 35.5 days | 10.7 | $699 | Active customers with strong discount dependence |

## Decision

Use the four groups to structure marketing experiments and reporting. Do not deploy segment-specific treatment policies until randomized tests demonstrate incremental value, customer-experience safety, and acceptable unit economics.
