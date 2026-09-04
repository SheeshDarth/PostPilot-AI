# Power BI / Tableau Dashboard Specification

Use `output/instagram_predictions.csv` as the primary data source and `output/instagram_feature_importance.csv` for the model chart.

For the final YouTube project, use `output/youtube_predictions.csv` and `output/youtube_feature_importance.csv` instead. Rename the imported table to `YouTube`.

## YouTube Dashboard

Page 1 should contain cards for total videos, average watch time, average CTR, total impressions, and subscribers gained. Add charts for watch time by content category, CTR by traffic source, average view percentage by video duration, and upload volume by hour.

Page 2 should contain predicted high-performance videos, average prediction probability, F1, ROC-AUC, prediction probability by category/source, performance segments, feature importance, and a detail table with video ID, category, traffic source, duration, probability, and predicted class.

## Page 1 — Instagram Performance

KPI cards: total posts, average calculated engagement rate, total reach, average follower count, and high-performance posts.

Charts: average engagement rate by media type, content category, traffic source, posting hour, and account type. Add slicers for media type, category, traffic source, account type, CTA, and day of week.

## Page 2 — Predictive Strategy

KPI cards: predicted high-performance posts, average prediction probability, high-intent posts, F1, and ROC-AUC. Add probability by media type/category, performance segment distribution, feature importance, and a detail table with post ID, media type, category, hour, probability, and predicted class.

## Core measures

```DAX
Total Posts = COUNTROWS(Instagram)
Average Engagement Rate = AVERAGE(Instagram[engagement_rate_calculated])
High Performance Posts = CALCULATE(COUNTROWS(Instagram), Instagram[High_Performance] = 1)
Predicted High Posts = CALCULATE(COUNTROWS(Instagram), Instagram[Predicted_High_Performance] = 1)
Average Prediction Probability = AVERAGE(Instagram[High_Performance_Probability])
```
