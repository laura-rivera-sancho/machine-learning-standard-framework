# Model Release Checklist

## Identity and provenance

- [ ] Immutable model ID and version assigned
- [ ] Artifact checksum recorded
- [ ] Source revision and dependency reference recorded
- [ ] Training-data snapshot or query version recorded
- [ ] Training cutoff and evaluation window recorded

## Evidence

- [ ] Decision contract and intended population are current
- [ ] Candidate compared with champion and safe baseline
- [ ] Future-like validation completed without leakage
- [ ] Decision-aware metric meets the release threshold
- [ ] Calibration or unsupervised stability reviewed as appropriate
- [ ] Error, segment, and customer-impact review completed
- [ ] Model card updated

## Compatibility and controls

- [ ] Training and inference schemas agree
- [ ] Output contract validated with a consumer
- [ ] Eligibility, consent, suppression, and capacity controls tested where applicable
- [ ] Score freshness or assignment validity defined
- [ ] Secrets and direct identifiers excluded from the manifest

## Operations

- [ ] Service, data, model, decision, and impact signals assigned to owners
- [ ] Warning, restriction, and rollback thresholds documented
- [ ] Delayed-label workflow tested where applicable
- [ ] Fallback named and rollback rehearsed
- [ ] Incident contacts and response targets current

## Approval and rollout

- [ ] Technical approver accepted the exact version
- [ ] Business approver accepted the intended use and limitations
- [ ] Initial rollout mode and scope approved
- [ ] Shadow or limited-release evidence reviewed before expansion
- [ ] Registry state and audit record updated

