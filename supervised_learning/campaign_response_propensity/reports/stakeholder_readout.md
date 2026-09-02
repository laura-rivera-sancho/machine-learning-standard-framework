# ML1 Stakeholder Readout — Campaign Response Propensity

[Download the five-slide executive PowerPoint](stakeholder_readout.pptx) for a non-technical presentation of the decision, evidence, limitations, and pilot plan.

## Decision

Advance the selected model to shadow scoring and a randomized pilot. Do not use it for autonomous campaign execution or claim incremental lift from the retrospective propensity results.

## Business context

Harbor & Pine can contact 20% of the eligible monthly retention audience. The current rule uses recency, engagement, prior response, and sessions. ML1 evaluates whether a supervised model identifies more responders within the same contact limit.

## Evidence

The selected HistGradientBoosting model was chosen using May–June 2026 Validation cohorts and evaluated once on the July–August 2026 Test cohorts.

| Held-out measure | Selected model | Current rule | Decision signal |
|---|---:|---:|---|
| Customers selected | 2,399 | 2,399 | Identical capacity |
| Responders captured | **439** | 392 | **+47 responders** |
| Precision | **18.30%** | 16.34% | +1.96 percentage points |
| Recall | **45.68%** | 40.79% | +4.89 percentage points |
| Lift | **2.28x** | 2.04x | Stronger concentration |
| PR AUC | **0.2201** | 0.1827 | Better responder ranking |

The model captures 12.0% more responders than the rule without increasing volume. Under explicit synthetic assumptions, retrospective net value is $11,517.72 versus $9,809.31.

## What drives the score

Historical click rate, discount share, prior responses, campaign spacing, loyalty tier, recency, and spend are the most influential inputs. These relationships are predictive and should not be interpreted as causes of response.

## Risks and limitations

- Propensity does not estimate incremental treatment effect; some selected customers may respond without contact.
- Upper score bands modestly overpredict response.
- Performance varies across loyalty tiers and regions.
- Historical campaign policy can be embedded in both labels and features.
- Economics are synthetic and exclude broader customer-experience effects.
- Excluding protected attributes does not eliminate proxy or allocation risk.

## Controlled pilot

1. Run one or more cohorts in shadow mode to verify freshness, eligibility, volume, latency, and reason-code output.
2. Randomize eligible customers within score bands into contact and holdout groups.
3. Preserve consent, suppression, frequency caps, and capacity as deterministic controls.
4. Measure incremental conversion, margin, opt-outs, complaints, and segment outcomes.
5. Compare model targeting with the current rule using identical budget and measurement windows.
6. Scale only after calibration and customer-impact gates pass.

## Stop conditions

Fall back to the current rule if consent cannot be verified, scores are stale, the schema changes without approval, contact volume exceeds capacity, lift falls below the monitoring threshold, or a material segment shows unacceptable degradation.

## Bottom line

The model has earned a controlled pilot, not broad deployment. The evidence supports improved ranking under fixed capacity while the governance plan preserves human ownership, deterministic eligibility, and a measurable rollback path.
