# ML Operating Model

## Objective

Create one auditable path from validated model evidence to a reversible operational decision. The framework applies to batch and online scoring and distinguishes supervised performance monitoring from unsupervised stability monitoring.

## Lifecycle and decision rights

| Stage | Required evidence | Accountable decision | Exit condition |
|---|---|---|---|
| Develop | Decision contract, source revision, data definition | Model owner | Candidate is reproducible |
| Validate | Baseline comparison, future-like evaluation, segment review | Model owner + independent reviewer | Evidence meets documented gates |
| Approve | Model card, release manifest, monitoring and rollback plans | Business owner + risk approver | Version is authorized for a named use |
| Release | Immutable artifact, configuration, consumer contract | Service owner | Shadow or limited rollout is healthy |
| Operate | Monitoring, incidents, overrides, outcome review | Operations owner | Continue, restrict, retrain, or roll back |
| Retire | Replacement or end-of-use decision, retained lineage | Business owner | New consumption is blocked |

The same person may fill more than one role in a small team, but the decisions and evidence remain distinct.

## Registry record

Each version receives an immutable identifier such as `campaign-response:1.0.0`. The registry record points to—not silently replaces—the following:

- Source revision and dependency lock
- Training-data snapshot or query version
- Feature and output contracts
- Serialized model or segmentation artifact checksum
- Evaluation report and model card
- Approval record
- Deployment configuration and environment
- Monitoring policy and rollback target

Mutable aliases such as `champion` may reference an immutable version. Alias changes require an approval event and remain in the audit history.

## Release gates

1. **Reproducibility:** source, data reference, parameters, and dependencies are recorded.
2. **Validity:** the model meets its documented decision metric and baseline comparison.
3. **Compatibility:** training and inference schemas agree; required inputs and outputs validate.
4. **Responsible use:** intended use, prohibited uses, affected population, and segment review are complete.
5. **Operability:** monitoring, ownership, incident response, and rollback are ready.
6. **Approval:** named technical and business owners approve the exact version.

Failure of a blocking gate leaves the version in candidate status.

## Rollout patterns

- **Shadow:** generate outputs without allowing them to affect decisions.
- **Limited:** expose a small, controlled portion of eligible decisions.
- **Parallel:** compare champion and challenger on the same eligible population.
- **Full approved scope:** expand only after predefined operational and impact gates pass.

The release manifest records the permitted mode. Expansion is a new approval event, not an undocumented configuration change.

## Cadence

| Review | Typical focus | Decision |
|---|---|---|
| Per run or near real time | Schema, freshness, service errors, volume, blocking controls | Continue or stop the run |
| Weekly | Drift, score or assignment distribution, overrides, capacity | Observe, investigate, or restrict |
| After label maturity | Ranking, calibration, errors, business outcomes, segment impact | Continue, retrain, or roll back |
| Quarterly | Intended use, ownership, thresholds, fallback rehearsal, accumulated incidents | Reapprove, revise, or retire |

Cadence should be adapted to risk, data volume, and outcome delay rather than copied mechanically.

