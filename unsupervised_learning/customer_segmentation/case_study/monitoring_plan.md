# Monitoring Plan

## Refresh controls

Run data validation before every bi-monthly refresh. Assignments are published only after an analyst reviews quality, distribution, stability, and profile meaning.

| Signal | Review threshold | Response |
|---|---:|---|
| Missing model-feature values | >2% for any feature | Stop publication; investigate pipeline/source |
| Out-of-range rate or negative recency | Any material count | Quarantine affected records and correct upstream |
| Population-size change | >15% vs. prior snapshot | Validate eligibility and source coverage |
| Segment population shift | >8 percentage points | Review drift, campaign effects, and naming |
| Temporal assignment ARI | <0.60 | Suspend automatic refresh; refit and investigate |
| Smallest segment share | <5% | Merge, redesign, or retire the solution |
| Unassigned/noise share | >10% | Review preprocessing and density assumptions |
| Profile direction reversal | Any key persona feature | Require human relabeling and stakeholder review |

## Outcome monitoring

Segment stability is not business success. For each activation test, track incremental conversion, margin, opt-out/contact complaints, returns, and contact cost by segment. Retain a randomized holdout and prevent repeated targeting from contaminating future behavior without documentation.

## Change and rollback

Version feature logic, scaler, algorithm, cluster centers, naming rules, and snapshot date. If a gate fails, retain the last approved segmentation or revert to governed RFM reporting. Never silently rename cluster IDs or overwrite historical assignments.
