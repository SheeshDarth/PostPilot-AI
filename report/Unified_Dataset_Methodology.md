# Unified Dataset Methodology

## Purpose

The three project datasets are combined into one canonical table for comparative experimentation. They are not row-joined because they have no shared post key and represent different synthetic populations.

## Source harmonization

Each source is mapped to the same fields: post/account identifiers, platform, content/topic metadata, timestamp, audience size, engagement counts, text/caption fields, and derived performance fields. Missing source fields remain null rather than being fabricated.

## Metric harmonization

The original 12,000-row source uses impressions as its audience denominator. The 20,000-row 2025 source and 29,999-row Instagram source use followers. Therefore raw engagement rates are not directly comparable. The unified table preserves `denominator_type` and creates `engagement_percentile` separately within each source.

## Common classes

Classes are defined within each source using the source-relative percentile:

- Low: 0th–50th percentile
- Medium: 50th–75th percentile
- High: 75th–100th percentile

This makes the classes comparable as relative performance, not as identical absolute engagement rates.

## Leakage rules

The following fields are outcomes and must never be model predictors: likes, comments, shares, saves, reach, impressions, total engagement, raw engagement rate, engagement percentile, and performance class. They are retained only for analysis and target construction. Any historical account feature must be calculated using earlier posts only.

## Modeling and validation

The unified table should include `source_dataset` as a feature and use chronological validation. Report overall metrics plus per-source metrics so that synthetic-source artifacts are visible. A unified model is an experiment; the Instagram-only model remains the recommended demo model because it has the most coherent feature definitions.

The corrected source-aware benchmark holds out the latest 20% within each source. It achieved 52.7% overall accuracy and macro-F1 0.489. Per-source accuracy was 74.3% for the original dataset, 54.7% for Instagram, and 36.8% for Social 2025. The date ranges are not aligned, so a single global chronological split would incorrectly test only the latest source.

## Dashboard use

Use `output/unified_social_media.csv` for cross-source comparisons. Add source and denominator type as slicers. For the primary demo, use `output/instagram_predictions.csv` because it avoids mixing incompatible denominators.
