# Model Release Contract

The contract defines the minimum evidence envelope for one release. The executable representation is the [example JSON manifest](example_release_manifest.json), validated by [`validate_release_manifest.py`](../src/validate_release_manifest.py).

## Required sections

| Section | Purpose | Blocking examples |
|---|---|---|
| `model` | Immutable identity, version, task type, and state | Missing version; unsupported task type; state not approved |
| `provenance` | Reproducibility and lineage | Missing source revision or training-data reference |
| `decision` | Permitted use and exclusions | No named decision; no prohibited-use statement |
| `evaluation` | Evidence and baseline comparison | Metric below its release threshold; missing evaluation window |
| `serving` | Consumer-facing behavior | Unsupported mode; missing output contract; stale scores |
| `monitoring` | Signals, thresholds, and response ownership | No rollback trigger or review cadence |
| `rollback` | Reversible safe state | Missing fallback or accountable owner |
| `approvals` | Human authorization | Technical or business approval absent |

## Compatibility principles

- Additive optional fields may be introduced within a contract version.
- Removing, renaming, or changing the meaning of a required field creates a new contract version.
- Consumers validate contract and model versions before accepting outputs.
- A release is blocked if feature or output compatibility cannot be established.
- The manifest never contains credentials, direct customer identifiers, or confidential training records.

## Output contract

Every score or assignment should include:

- `entity_id`: pseudonymous decision key
- `model_id` and `model_version`
- `scored_at`: timestamp in UTC
- `prediction`: probability, score, or cluster assignment
- `decision_context`: approved use or campaign/run identifier
- `reason_codes` where appropriate
- `valid_until` for time-sensitive scores

Eligibility, consent, suppression, capacity, and other deterministic business controls remain outside the predictive score and must be applied before action.

