# ML3 Stakeholder Readout — Production Readiness

[Download the six-slide executive PowerPoint](stakeholder_readout.pptx) for a non-technical explanation of the operating model, release gates, monitoring decisions, and rollback path.

## Recommendation

Adopt one release contract across the repository's three ML cases. Permit operational use only when the exact version has complete evidence, named technical and business approval, active monitoring, and a rehearsed fallback.

## Why this matters

The completed cases demonstrate modeling decisions, but operating risk appears after handoff: feature definitions can change, labels arrive late, populations drift, consumers can misuse outputs, and teams may be unable to identify or reverse the active version.

## Operating model

| Decision point | Required evidence | Outcome |
|---|---|---|
| Validate | Reproducible build, baseline comparison, future-like evaluation, segment review | Candidate may enter approval review |
| Approve | Model card, manifest, intended use, owners, monitoring, rollback | Exact version is authorized for a named use |
| Release | Compatible contracts, immutable artifact, controlled rollout | Shadow or limited operation begins |
| Operate | Service, data, model, decision, and impact signals | Continue, observe, restrict, retrain, or roll back |
| Retire | Replacement or end-of-use decision with retained lineage | New consumption is blocked |

## Controls by case

- **Campaign response:** lift and calibration at capacity, deterministic consent and suppression, controlled pilot measurement.
- **PayWave inactivity:** temporal performance, score freshness, outreach capacity, and false-positive burden.
- **Customer segmentation:** coverage, cluster-size concentration, temporal stability, persona drift, and activation tests.

## Non-negotiable release gates

1. Reproducible lineage from source and data to the artifact
2. Evidence against a realistic champion and safe baseline
3. Compatible feature and output contracts
4. Intended use, exclusions, and segment review
5. Monitoring tied to named responses and owners
6. Human approval and a tested rollback target

## Rollback principle

Rollback is an approved operating state, not an improvised emergency. The team must be able to stop new consumption, activate the named fallback, preserve evidence, reconcile affected decisions, and approve any re-release as a new event.

## Next action

Run a tabletop operating rehearsal using one portfolio case: validate its manifest, simulate an incompatible schema, invoke the fallback, verify ownership and evidence capture, and record the lessons before any real deployment.

