# ML3 — Production Readiness

> **Status: Complete.** A shared operating framework for releasing, monitoring, retraining, and rolling back the repository's supervised and unsupervised ML systems.

**Decision:** What evidence and controls must be present before a model is released, and what should happen when its data, behavior, or business context changes?

ML3 connects the three completed case studies to one lifecycle. It separates model development from release approval, records the exact model and data contract, translates monitoring signals into owned actions, and requires a reversible path back to a safe baseline.

## What this module demonstrates

- A versioned release contract covering provenance, evaluation, approval, serving, monitoring, and rollback
- A model-registry approach that preserves lineage between code, data, evaluation evidence, and deployment state
- Monitoring across service health, data quality, drift, model behavior, business outcomes, and customer impact
- Risk-based retraining and rollback workflows with mandatory human approval
- Practical runbooks for incidents and controlled operating rehearsals
- An executable validator and tests for the example release manifest

## Portfolio review path

1. [Executive PowerPoint](reports/stakeholder_readout.pptx)
2. [Stakeholder readout](reports/stakeholder_readout.md)
3. [Production-readiness fundamentals](production_readiness_fundamentals.md)
4. [Operating model](operating_model.md)
5. [Release contract](contracts/model_release_contract.md)
6. [Example release manifest](contracts/example_release_manifest.json)
7. [Monitoring and alerting](monitoring/monitoring_and_alerting.md)
8. [Retraining and rollback](operations/retraining_and_rollback.md)
9. [Incident runbook](operations/incident_runbook.md)
10. [Release checklist](templates/model_release_checklist.md)
11. [Manifest validator](src/validate_release_manifest.py)

## Validate the release contract

From the repository root:

```bash
python production_readiness/src/validate_release_manifest.py \
  production_readiness/contracts/example_release_manifest.json
pytest
```

The example describes a fictional campaign-response release. It is an inspectable governance artifact, not evidence that a live model has been deployed.

