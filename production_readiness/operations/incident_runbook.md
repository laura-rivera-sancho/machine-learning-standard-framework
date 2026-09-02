# ML Incident Runbook

## Purpose

Coordinate a fast, evidence-preserving response when an ML release may be unsafe, unavailable, or outside its approved use.

## Triage

Record:

- Detection time, signal, and reporter
- Model identifier, version, environment, and consumers
- Affected scoring window and estimated decision volume
- Whether the issue affects service, data, model behavior, decision controls, or customer impact
- Current lifecycle and rollout state

## Severity

- **SEV-1:** mandatory control failure, corrupt outputs, material harmful impact, or inability to stop affected use
- **SEV-2:** degraded model or data behavior requiring restriction, but a safe fallback is available
- **SEV-3:** contained anomaly with no current decision impact

## First response

1. Name an incident lead and scribe.
2. Stop or restrict the affected decision path when a blocking condition exists.
3. Activate the approved fallback when required.
4. Preserve evidence; do not overwrite artifacts or logs.
5. Notify named technical and business owners.
6. Establish the next review time and decision owner.

## Investigation prompts

- Did source data, feature meaning, schema, or freshness change?
- Is the active artifact the approved version and checksum?
- Did eligibility or suppression logic change?
- Are failures concentrated by cohort, geography, product, or customer segment?
- Are labels mature enough to interpret performance?
- Did an upstream policy or downstream consumer change?

## Recovery and closure

Recovery requires evidence that the selected state—fallback, prior version, or repaired new version—is operating within approved boundaries. Close the incident only after decision reconciliation, stakeholder communication, root-cause analysis, assigned corrective actions, and a documented re-release or retirement decision.

