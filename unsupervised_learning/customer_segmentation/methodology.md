# Methodology

## 1. Snapshot design

The generator creates two observations for the same synthetic customers: June 30 and August 31, 2026. Features use only behavior available at each cutoff. Stable latent profiles generate correlated but noisy behavior, allowing a meaningful temporal-stability check.

## 2. Data controls

The workflow reports and resolves duplicate customer-snapshot keys, negative recency, rates outside 0–1, and missing values. Customer IDs, dates, region, consent, and synthetic generator truth are excluded from the feature matrix.

## 3. Preprocessing

Skewed RFM, value, and tenure variables use `log1p` after median imputation. Rate features use median imputation without log transformation. All features are standardized within one reusable preprocessing pipeline.

## 4. Candidate comparison

- K-means for *k*=4–7, with 30 initializations
- Full-covariance GMM for 4–7 components, with regularization and five initializations
- DBSCAN across a documented epsilon grid with 25 minimum samples

Each candidate is evaluated on silhouette, Calinski–Harabasz, Davies–Bouldin, coverage, and smallest-segment share. K-means and GMM also receive five bootstrap fits; pairwise ARI summarizes stability. DBSCAN receives a small-perturbation ARI diagnostic.

## 5. Selection

Candidates first pass coverage ≥90%, smallest segment ≥5%, and bootstrap ARI ≥0.75. Eligible candidates are ranked jointly on silhouette, stability, minimum size, and Davies–Bouldin rather than one metric. The reference result selects four-cluster K-means.

## 6. Temporal validation

The current fitted solution assigns both snapshots using one preprocessing and centroid contract. ARI across matched customers measures structural persistence. This is stricter than reporting only the current cross-section.

## 7. Persona naming

Deterministic rules map profile statistics to human-readable names. Names are presentation labels—not learned classes—and require review whenever profile directions change.

## 8. Activation boundary

The output supports audience hypotheses and experiment stratification. Consent, suppression, frequency caps, fairness review, treatment choice, and campaign execution remain outside the clustering model.
