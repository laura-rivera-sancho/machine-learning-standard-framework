# Production Readiness Fundamentals

Production readiness asks whether a model can be operated safely and usefully after experimentation ends. A strong offline score is necessary evidence, but it is not a release decision by itself.

## 1. Model lifecycle

A practical lifecycle separates six states:

1. **Developed:** candidate code and features exist.
2. **Validated:** evaluation is complete on representative, untouched data.
3. **Approved:** accountable owners accept the intended use, limitations, and controls.
4. **Released:** a specific version is available to an approved process.
5. **Monitored:** service, data, model, decision, and impact signals are observed.
6. **Retired:** the version can no longer be used for new decisions.

State transitions should be explicit. A model does not become approved merely because a file was deployed.

## 2. Training–serving consistency

The same feature meaning, transformation, unit, time cutoff, and missing-value treatment must apply during training and inference. Training–serving skew occurs when those definitions diverge.

Important controls include:

- One documented feature contract with names, types, ranges, owners, and freshness
- Point-in-time correct joins that prevent future information from entering a score
- Deterministic preprocessing shared or tested across training and inference
- Schema validation before scoring
- Versioned code, parameters, and dependency environment

## 3. Release manifest and lineage

A release manifest is the evidence envelope for one model version. It should connect:

- Model identifier, version, task type, and lifecycle state
- Source-code revision and training-data reference
- Evaluation window, baseline, decision metric, and threshold
- Intended use, exclusions, and responsible owners
- Serving mode, freshness expectation, and output contract
- Monitoring thresholds, escalation routes, and rollback target
- Approval record and decision date

Lineage answers: *What produced this output, from which data and code, under which approval?*

## 4. Registry concepts

A model registry is more than a file store. It records versions, evidence, stage, ownership, and allowed transitions. Useful distinctions are:

- **Candidate:** being evaluated; not permitted for operational decisions
- **Approved:** evidence and controls passed review
- **Champion:** the version currently preferred for an approved use
- **Challenger:** compared with the champion without silently replacing it
- **Archived:** preserved for audit but blocked from new decisions

Promotion should reference evaluation evidence and an approver. Demotion and retirement should remain possible without deleting history.

## 5. Monitoring layers

No single metric proves that a model is healthy.

| Layer | Examples | Interpretation |
|---|---|---|
| Service | Availability, latency, errors, scoring volume | Can the scoring process operate as expected? |
| Data quality | Missingness, schema validity, freshness, range checks | Are inputs complete, timely, and structurally valid? |
| Drift | Population stability, distribution distance, category shift | Has the input or score population changed? |
| Model behavior | Calibration, ranking, cluster stability, coverage | Does model behavior remain consistent with validation evidence? |
| Decision | Selection volume, capacity use, overrides, abstentions | Is the model being used as intended? |
| Outcome and impact | Conversion, inactivity, margin, complaints, segment outcomes | Is the decision useful and acceptable in practice? |

Drift is a diagnostic signal, not automatic proof of performance loss. Conversely, stable input distributions do not guarantee stable outcomes.

## 6. Delayed labels

Many supervised outcomes arrive days or weeks after scoring. Monitoring therefore needs two speeds:

- **Immediate proxies:** schema, freshness, score distributions, volume, latency, overrides
- **Mature outcomes:** ranking, calibration, error rates, business value, and segment impact after the label window closes

The delayed-label design should specify attribution windows, incomplete cohorts, backfill behavior, and the date on which a cohort is mature enough to evaluate.

## 7. Unsupervised monitoring

Unsupervised systems require different evidence because there is no target label. Useful checks include:

- Assignment coverage and unassigned-rate changes
- Cluster-size concentration and minimum viable segment size
- Distance to centroids or likelihood under the reference model
- Bootstrap or temporal assignment stability
- Persona drift and whether activation rules remain meaningful

High silhouette scores do not guarantee stable or actionable segments.

## 8. Thresholds and alert design

Thresholds should be tied to actions. A warning without an owner or response window becomes noise.

- **Observe:** investigate during routine review; no decision change yet
- **Restrict:** narrow use, freeze expansion, or require manual review
- **Rollback:** stop using the model and return to the approved fallback

Use persistence rules where appropriate—for example, two consecutive breaches—to reduce reactions to random variation. Some failures, such as missing consent controls or incompatible schemas, justify immediate blocking.

## 9. Retraining

Retraining is a new model release, not routine maintenance that bypasses review. A trigger may start investigation, but promotion still requires:

1. Reproducible data and code
2. Candidate-versus-champion comparison
3. Validation on representative future-like data
4. Segment and customer-impact review
5. Updated model card and manifest
6. Human approval
7. Controlled rollout and rollback readiness

Scheduled retraining is appropriate only when the schedule reflects how the data-generating process changes. Event-driven retraining may be preferable when labels mature slowly or material changes are irregular.

## 10. Rollback and safe fallback

Rollback restores an approved safe state. It requires:

- A known prior model, business rule, or manual process
- Versioned artifacts and configuration
- A clear decision owner
- Tested switching instructions
- Reconciliation of decisions already made
- Post-incident review before re-release

Rollback is not failure; lack of a rollback path is the operational failure.

## 11. Human oversight

Human approval should be meaningful. Reviewers need the model's intended decision, evidence, uncertainty, affected population, prohibited uses, monitoring plan, and fallback. Approval records should identify who accepted which version and when.

For these portfolio cases, the model ranks or organizes decisions; it does not independently contact customers, change eligibility, or create irreversible actions.

## 12. Common failure modes

- Shipping the latest artifact without a versioned evidence package
- Monitoring only API uptime while ignoring decisions and customer outcomes
- Treating drift as an automatic retraining command
- Evaluating only aggregate performance and missing segment degradation
- Allowing feature definitions to change without compatibility review
- Keeping a rollback document that has never been rehearsed
- Replacing a champion before the challenger completes controlled comparison
- Reporting model explanations as causal evidence

## 13. Questions a reviewer should ask

- What exact decision is this version permitted to support?
- Which data and code produced it?
- Which validation period and baseline justify release?
- What must be true before a score may be consumed?
- How quickly will labels mature?
- Which signal causes observation, restriction, or rollback?
- Who owns each response?
- Can the system return to a safe baseline without losing decision history?

