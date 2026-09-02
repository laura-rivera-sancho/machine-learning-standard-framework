# Retraining and Rollback

## Retraining triggers

A trigger starts investigation; it does not authorize promotion.

- Mature-cohort performance remains below the case threshold
- Calibration or assignment stability degrades materially
- The population or operating policy changes enough to invalidate validation evidence
- Feature availability or meaning changes
- A scheduled review finds that the champion is no longer fit for its approved decision

## Controlled retraining workflow

1. Open a retraining record with the trigger, affected versions, owner, and scope.
2. Freeze the prior training-data and code references.
3. Rebuild the candidate reproducibly with point-in-time correct data.
4. Compare candidate, champion, and safe baseline on future-like validation data.
5. Review aggregate, segment, error, and customer-impact evidence.
6. Update the model card, release manifest, monitoring thresholds, and rollback target.
7. Obtain technical and business approval for the exact candidate version.
8. Run shadow or limited rollout before changing the champion alias.

## Rollback triggers

Immediate rollback is appropriate when:

- Consent, suppression, eligibility, or other mandatory controls fail
- The input schema is incompatible or critical data are stale
- Outputs are corrupted, missing, or materially outside valid ranges
- A severe customer-impact or security issue is identified
- The version breaches a documented red threshold

Performance-related rollback may use persistence rules when labels are delayed and the model remains safe to observe.

## Rollback procedure

1. Stop new consumption of the affected version.
2. Point consumers to the named fallback model, business rule, or manual process.
3. Preserve the manifest, inputs, outputs, logs, and configuration needed for investigation.
4. Reconcile decisions already produced and identify any remediation.
5. Notify the business, model, service, and risk owners.
6. Verify fallback volume, eligibility, and outcome tracking.
7. Complete root-cause review and approve any re-release as a new event.

## Rehearsal standard

Before full approved use, demonstrate that the team can identify the active version, disable it, activate the fallback, verify consumer behavior, and recover audit evidence within the stated recovery objective.

