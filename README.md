# Machine Learning Standard Framework

[![Repository quality](https://github.com/laura-rivera-sancho/machine-learning-standard-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/laura-rivera-sancho/machine-learning-standard-framework/actions/workflows/ci.yml)

**A decision-focused portfolio of supervised and unsupervised machine-learning systems built with reproducible evaluation, explainability, and operational controls.**

This repository demonstrates how I move from a business decision to a defensible model: defining supervised targets and unsupervised similarity contracts, preventing leakage, validating through time, comparing realistic candidates, evaluating operational decisions, explaining model behavior, and defining monitoring before deployment.

All companies, customer records, and results are fictional or synthetically generated. No employer, client, or confidential data are used.

## Explore the Machine Learning portfolio

Use these shortcuts to explore the decisions, methods, and stakeholder-ready
evidence across the portfolio:

| What to assess | Start here | What it demonstrates |
|---|---|---|
| Campaign-response modeling | [Campaign Response Propensity case](supervised_learning/campaign_response_propensity/README.md) | Target definition, leakage prevention, temporal validation, calibration, capacity-aware ranking, and pilot design |
| Inactivity-risk modeling | [PayWave Inactivity case](supervised_learning/paywave_inactivity/README.md) | A second supervised decision with baseline comparison, capacity evidence, model governance, and an executive readout |
| Customer segmentation | [Customer Segmentation case](unsupervised_learning/customer_segmentation/README.md) | Unsupervised candidate comparison, stability testing, interpretable personas, and activation guidance |
| Executive communication | [Campaign-response PowerPoint](supervised_learning/campaign_response_propensity/reports/stakeholder_readout.pptx) and [segmentation PowerPoint](unsupervised_learning/customer_segmentation/reports/stakeholder_readout.pptx) | Clear model results, limitations, recommendations, and next actions for non-technical stakeholders |
| Responsible model operation | [Campaign-response model card](supervised_learning/campaign_response_propensity/model_card/model_card.md) and [PayWave monitoring plan](supervised_learning/paywave_inactivity/case_study/monitoring_plan.md) | Intended use, exclusions, controls, monitoring thresholds, retraining signals, and rollback boundaries |
| Machine Learning concepts | [Campaign-response fundamentals](supervised_learning/campaign_response_propensity/campaign_response_fundamentals.md) and [segmentation fundamentals](unsupervised_learning/customer_segmentation/customer_segmentation_fundamentals.md) | Supervised and unsupervised concepts, evaluation choices, interpretation, and common failure modes |
| Reproducible implementation | [Campaign-response source](supervised_learning/campaign_response_propensity/src), [segmentation source](unsupervised_learning/customer_segmentation/src), and [automated tests](tests) | Deterministic data, reusable workflows, analytical controls, and repository quality checks |
| Portfolio scope and milestones | [Roadmap](ROADMAP.md) | Completed cases, production-readiness goals, completion criteria, and delivery sequence |

## Repository map

```text
machine-learning-standard-framework/
├── supervised_learning/
│   ├── campaign_response_propensity/
│   │   ├── case_study/       # Decision contract, dictionary, results, monitoring
│   │   ├── data/             # Review sample and generated outputs
│   │   ├── model_card/       # Intended use, limitations, risks, controls
│   │   ├── reports/          # Stakeholder readout and executive visual
│   │   └── src/              # Generator, training, evaluation, and visualization
│   └── paywave_inactivity/   # Inactivity-risk case and executive readout
├── unsupervised_learning/
│   └── customer_segmentation/
│       ├── case_study/       # Decision contract, dictionary, results, monitoring
│       ├── data/             # Review sample and generated outputs
│       ├── model_card/       # Intended use, limitations, risks, controls
│       ├── reports/          # Stakeholder readout and executive visual
│       └── src/              # Generator, candidate comparison, and visualization
├── tests/                    # Model logic and repository integrity
├── ROADMAP.md
└── README.md
```


## Reproduce the case studies

Use Python 3.11 or 3.12:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

python supervised_learning/campaign_response_propensity/src/generate_synthetic_data.py
python supervised_learning/campaign_response_propensity/src/train_evaluate.py
python supervised_learning/campaign_response_propensity/src/create_visuals.py

python supervised_learning/paywave_inactivity/src/generate_synthetic_data.py
python supervised_learning/paywave_inactivity/src/train_evaluate_models.py

python unsupervised_learning/customer_segmentation/src/generate_synthetic_data.py
python unsupervised_learning/customer_segmentation/src/segment_evaluate.py
python unsupervised_learning/customer_segmentation/src/create_visuals.py
pytest
```

## Design principles

- Start with the operational decision, capacity, and error costs.
- Define the target, horizon, eligibility, and observation cutoff before feature engineering.
- Compare models with a realistic current-state baseline.
- Match validation to how the model will encounter future data.
- Evaluate ranking, calibration, economics, and segment behavior—not accuracy alone.
- For unsupervised models, evaluate stability, coverage, minimum size, interpretability, and actionability—not separation alone.
- Treat model explanations as predictive evidence, not causal conclusions.
- Separate propensity modeling from uplift or treatment-effect estimation.
- Require monitoring, rollback, and human ownership before production use.

## License

This project is available under the [MIT License](LICENSE). Citation metadata are provided in [CITATION.cff](CITATION.cff).
