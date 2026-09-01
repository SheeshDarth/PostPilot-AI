# Instagram PostPilot Analytics Report

## Abstract

This project analyzes 29,999 Instagram posts and predicts whether a future post will fall in the top engagement quartile. The workflow combines Python data preparation, exploratory analysis, leakage-safe feature engineering, Random Forest classification, and Power BI/Tableau-ready exports. The dataset is synthetic, so the results are suitable for an academic demonstration rather than production forecasting.

## Dataset

Each row contains account attributes, follower count, media type, content category, traffic source, call-to-action flag, timestamp, caption length, hashtag count, engagement outcomes, and a supplied performance label. Engagement outcomes are used only to calculate the historical target and are excluded from predictive features.

## Methodology

`Engagement Rate = (Likes + Comments + Shares + Saves) / Followers × 100`

Posts at or above the 75th percentile are labeled `High_Performance`. The model uses account type, media type, content category, traffic source, CTA, weekday, language, follower count, following count, account age, posting hour, caption length, hashtag count, TF-IDF caption features, and prior account engagement computed only from earlier posts. Likes, comments, shares, saves, reach, impressions, engagement rate, followers gained, and performance labels are excluded.

The final evaluation is chronological: the earliest 80% of posts are used for training and the latest 20% for testing.

## Results

The generated values are stored in `output/instagram_model_metrics.csv`. The measured chronological run on 29,999 rows produced accuracy 0.762, precision 0.563, recall 0.213, F1 0.309, and ROC-AUC 0.759. These results are materially stronger than the earlier synthetic datasets, but the source is still synthetic and should not be presented as production validation.

## Dashboard design

Use `output/instagram_predictions.csv` as the primary Power BI/Tableau source and `output/instagram_feature_importance.csv` as the model source.

### Page 1 — Instagram Performance Analytics

KPI cards: total posts, average engagement rate, total reach, average followers, and high-performance posts. Add bar charts for media type and content category, a line chart by posting hour, a column chart by traffic source, and slicers for account type, media type, category, device/source, and month.

### Page 2 — Predictive Content Strategy

KPI cards: predicted high-performance posts, average prediction probability, high-intent posts, F1, and ROC-AUC. Add probability by media type/category, performance-segment distribution, feature importance, and a table containing post ID, media type, category, post hour, probability, and predicted class.

## Limitations

The dataset is synthetic and does not represent a real Instagram audience or algorithm. The target is derived from post-publication outcomes. Accuracy is not sufficient as a standalone metric because the target is imbalanced. Real deployment would require first-party analytics, creator-history data, media quality, audience demographics, and repeated time-based validation.

## Conclusion

PostPilot demonstrates a complete social-media analytics workflow from raw post data to predictive outputs and interactive business intelligence. Its strongest technical decision is strict separation between pre-publication predictors and post-publication outcomes.
