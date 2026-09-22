# PostPilot AI Power BI Dashboard

Power BI Desktop is the dashboard layer for this project. The Python pipeline already exports a Power BI-ready CSV; no live YouTube API is required for the academic demonstration.

## Load the data

1. Run `RUN_PROJECT.ps1` from the project folder.
2. Open Power BI Desktop.
3. Select **Get data → Text/CSV** and choose `output/youtube_predictions.csv`.
4. Repeat **Get data → Text/CSV** for `output/youtube_hashtags.csv`.
5. Select **Load** and rename the tables to `YouTube` and `YouTubeHashtags`.
5. In **Modeling**, set `upload_date` to Date/Time and probability/percentage fields to decimal number.

## Page 1 — Channel performance

Add these cards:

- Total Videos: `COUNTROWS(YouTube)`
- Average Watch Time (hours): `AVERAGE(YouTube[total_watch_time_hours])`
- Average CTR: `AVERAGE(YouTube[ctr_percentage])`
- Total Impressions: `SUM(YouTube[impressions])`
- Subscribers Gained: `SUM(YouTube[subscribers_gained])`

Exact field bindings used by the PBIP report:

| Visual | Category / X-axis | Value / Y-axis | Tooltip or detail |
|---|---|---|---|
| Watch Time by Category | `YouTube[content_category]` | `[Average Watch Time (Hours)]` | `[Average CTR]` |
| CTR by Traffic Source | `YouTube[traffic_source]` | `[Average CTR]` | `[Average Watch Time (Hours)]` |
| Upload Activity by Hour | `YouTube[upload_hour]` | `[Total Videos]` | `[Average CTR]` |
| Video Duration vs Watch Time | `AVG(YouTube[video_duration_min])` | `AVG(YouTube[total_watch_time_hours])` | Legend: `content_category`; Details: `post_id` |

For the horizontal bar chart, `traffic_source` is the Category/Y-axis and `[Average CTR]` is the X-axis/Values field.

Suggested arrangement: place the five KPI cards across the top, the category and traffic-source charts in the middle, and the upload-hour chart across the bottom. Use `dashboard/PostPilot_AI_Measures.dax` as the copy source for all measures.

## Page 2 — Prediction strategy

Add cards for predicted high-performance videos, average prediction probability, F1, ROC-AUC, and the decision threshold. Add a bar chart of average probability by `content_category`, a stacked column chart of `Performance_Segment`, a feature-importance bar chart using `output/youtube_feature_importance.csv`, and a table containing `post_id`, `content_category`, `traffic_source`, `video_duration_min`, `High_Performance_Probability`, and `Predicted_High_Performance`.

Exact prediction-page fields:

| Visual | Category / Legend | Value / X/Y-axis | Tooltip |
|---|---|---|---|
| High-Performance Videos by Category | `YouTube[content_category]` | `[Predicted High Videos]` | `[Average Prediction Probability]` |
| Prediction Segment Distribution | `YouTube[Performance_Segment]` | `[Total Videos]` | `[Average Prediction Probability]` |
| Probability by Traffic Source | `YouTube[traffic_source]` | `[Average Prediction Probability]` | `[Average CTR]` |

The recommendation table contains `post_id`, `content_category`, `traffic_source`, `High_Performance_Probability`, `Predicted_High_Performance`, `YouTubeHastags[recommended_hashtags]`, and `YouTubeHastags[hashtag_relevance_score]`.

Add a hashtag table using `YouTubeHastags[post_id]`, `recommended_hashtags`, `hashtag_relevance_score`, and `hashtag_generation_source`. Keep the model spelling `YouTubeHastags`. Relate `YouTubeHastags[post_id]` to `YouTube[post_id]` with a one-to-one relationship if Power BI does not detect it automatically.

Suggested arrangement: place prediction KPI cards across the top, slicers down the left, the hashtag table on the right, and probability/category charts along the bottom.

## Page 3 — Python comparison and recommendations

This page mirrors the Python dashboard's comparison views. It contains:

- KPI cards for predicted high rate, average hashtags per video, average hashtag relevance, average prediction probability, and total videos.
- Slicers for content category, traffic source, performance segment, and hashtag generation source.
- A **Category Comparison** table with content category, video count, average watch time, average CTR, average prediction probability, and predicted high videos.
- A **Highest-Probability Videos** table with post ID, category, traffic source, duration, probability, and prediction flag.
- A **Hashtag Quality and Recommendations** table with recommended hashtags, relevance score, hashtag count, and generation source.

The comparison columns use conditional color gradients: teal/gold for watch time, teal for CTR, blue/purple for prediction probability, red/green for high-performance probability, and slate/teal for hashtag relevance. Higher values are visually stronger, making category and video comparisons easy to infer.

## Measures

```DAX
Total Videos = COUNTROWS(YouTube)
Average Watch Time = AVERAGE(YouTube[total_watch_time_hours])
Average CTR = AVERAGE(YouTube[ctr_percentage])
Total Impressions = SUM(YouTube[impressions])
Subscribers Gained = SUM(YouTube[subscribers_gained])
Predicted High Videos = CALCULATE(COUNTROWS(YouTube), YouTube[Predicted_High_Performance] = 1)
Average Prediction Probability = AVERAGE(YouTube[High_Performance_Probability])
Test Accuracy = 0.7325
Test F1 = 0.4216
Test ROC AUC = 0.7716
Decision Threshold = 0.42
```

Add slicers for content category, traffic source, upload weekday, upload month, and performance segment. Use the slicers to demonstrate interactive filtering during the presentation.

## Important limitation

The supplied YouTube dataset is simulated/static. The report is not a live YouTube monitoring dashboard. A live version would require YouTube Data API/Analytics API credentials and scheduled refresh configuration.

Hashtags are relevance suggestions, not a guarantee of virality. The current dataset has no title, description, transcript, or keyword columns, so generated tags use category and traffic-source fallback labels. Add those text fields for genuinely video-specific tags.
