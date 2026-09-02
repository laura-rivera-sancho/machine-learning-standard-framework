# Monitoring and Alerting

## Monitoring objective

Detect when the service, inputs, model behavior, decision process, or customer impact no longer supports the approved use. Every alert maps to an owner and a response.

## Signal catalogue

| Signal family | Supervised examples | Unsupervised examples | Default owner |
|---|---|---|---|
| Service | Run completion, latency, scoring errors | Run completion, assignment errors | Service owner |
| Data quality | Missingness, freshness, schema, ranges | Missingness, freshness, schema, ranges | Data owner |
| Population | Feature and score drift | Feature drift, cluster-size shift, distance shift | Model owner |
| Model behavior | Lift, PR AUC, calibration, recall at capacity | Coverage, stability, minimum segment size, persona drift | Model owner |
| Decision | Volume, overrides, exclusions, stale-score use | Activation volume, overrides, unassigned cases | Business owner |
| Impact | Conversion, inactivity, margin, complaints, segment outcomes | Experiment outcomes by segment, complaints, exclusions | Business owner |

## Severity and response

| Level | Meaning | Response | Target |
|---|---|---|---|
| Green | Within approved operating range | Continue and record | Routine review |
| Amber | Investigation threshold breached | Assign owner, inspect lineage and segments, freeze expansion | One business day |
| Red | Blocking control or rollback threshold breached | Stop affected use, invoke fallback, preserve evidence, notify owners | Immediate |

Thresholds are case-specific. Statistical alerts should be evaluated with sample size, seasonality, and persistence; hard control failures may block immediately.

## Delayed-outcome workflow

1. Record the scoring cohort and prediction timestamp.
2. Apply eligibility and intervention controls outside the model.
3. Mark the cohort incomplete until the outcome window closes.
4. Backfill outcomes using a versioned attribution rule.
5. Calculate aggregate and segment-level measures only for mature cohorts.
6. Compare with release thresholds and the approved baseline.
7. Record the decision: continue, observe, restrict, retrain, or roll back.

## Case-specific emphasis

- **Campaign response:** lift and calibration at the contact capacity, plus opt-outs and complaints.
- **PayWave inactivity:** recall and precision within outreach capacity, score freshness, and false-positive burden.
- **Customer segmentation:** assignment coverage, cluster size, temporal stability, persona drift, and activation-test outcomes.

## Alert quality

Review alert volume and usefulness quarterly. Retire alerts that have no decision consequence, refine noisy thresholds, and retain an audit trail of threshold changes.

