# Contributing

Contributions should improve analytical correctness, reproducibility, responsible operation, or reviewer clarity.

## Case-study standard

Every completed case should include:

1. a business decision, scoring population, target, horizon, and success criteria
2. a data contract with feature availability and leakage controls
3. an appropriate baseline and validation design
4. discrimination, calibration, decision, and segment evaluation
5. explainability with non-causal interpretation
6. operational economics and capacity trade-offs
7. tests, pinned dependencies, and deterministic sample data
8. a model card, monitoring plan, and rollback conditions
9. a stakeholder readout with limitations and recommended action

Do not add challenge notebooks. Add a guided notebook only when it materially improves review beyond the tested source workflow.

## Local checks

```bash
ruff check .
ruff format --check .
python -m compileall -q supervised_learning tests
pytest --cov
```

Only fictional or synthetic data belong in this repository. Never include credentials, personal data, employer/client artifacts, or confidential information.
