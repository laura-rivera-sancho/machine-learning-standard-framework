# Customer Segmentation Fundamentals

## What segmentation answers

Unsupervised segmentation groups observations using similarities in selected features without a labeled outcome. It is most useful when the business needs a manageable behavioral taxonomy for planning, analysis, or experiment design.

It does **not** prove that groups are naturally real, that every customer belongs permanently to one identity, or that different treatment causes better outcomes.

## Core concepts

### Feature choice defines similarity

Distance is calculated from the supplied representation. Including spend, recency, channel mix, or discount behavior expresses a business view of which differences matter. Highly skewed monetary and count features are log-transformed; all inputs are standardized so units do not dominate distance.

### K-means

K-means minimizes within-cluster squared Euclidean distance. It is fast, easy to score, and operationally transparent, but favors roughly compact groups and requires a chosen number of clusters.

### Gaussian Mixture Models

GMM represents data as a mixture of probabilistic components with flexible covariance. It supports soft membership but can create small, unstable components and is more sensitive to specification.

### Density-based clustering

DBSCAN connects dense neighborhoods and labels sparse observations as noise. It can find irregular shapes and identify outliers, but one density threshold often struggles when customer groups have different densities. Coverage is therefore a first-class metric.

## Evaluation without a target

- **Silhouette:** compares cohesion with separation; higher is better, but a high score can reward overly coarse solutions.
- **Calinski–Harabasz:** ratio of between- to within-cluster dispersion; useful mainly for relative comparison.
- **Davies–Bouldin:** average similarity to the most similar other cluster; lower is better.
- **Adjusted Rand Index (ARI):** agreement between two partitions corrected for chance; label numbering does not matter.
- **Stability:** whether resampling or time changes the partition materially.
- **Coverage and size:** whether the solution assigns enough customers and avoids unusable micro-segments.
- **Interpretability and actionability:** whether profiles support distinct, testable decisions.

## Choosing the number of segments

There is rarely a single statistically correct answer. Compare several values of *k*, then balance separation, stability, minimum size, simplicity, and the number of strategies the organization can operate. More clusters are not automatically more insightful.

## Interpretation rules

Cluster IDs are arbitrary; profile-based names must be versioned and reviewed. A centroid is an average, not a description of every member. Differences are descriptive associations, not causal drivers. Synthetic truth can validate this demonstration, but real projects have no ground-truth persona label.

## From segmentation to value

Treat each segment as a hypothesis. Define an intervention, comparison group, primary metric, guardrails, and decision rule. Randomized experiments determine whether a differentiated treatment creates incremental value; the clustering model alone cannot.
