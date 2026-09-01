# PostPilot AI Report

## Abstract

PostPilot AI estimates whether a planned social-media post is likely to reach the highest-performing quartile of historical engagement. It derives an engagement rate from historical interactions, defines the top quartile as high performance, and trains a Random Forest classifier using only pre-publication metadata. The model probability and descriptive strategy summaries are exported for Power BI.

## Dataset and methodology

The input schema includes platform, timestamp, topic, campaign phase, sentiment, emotion, sentiment score, impressions, likes, comments, and shares. Duplicate rows are removed; invalid timestamps, missing impressions, and non-positive impressions are excluded; missing engagement counts are treated as zero. Posting hour, weekday, and month are derived from the timestamp.

`Total Engagement = Likes + Comments + Shares`

`Engagement Rate = Total Engagement / Impressions × 100`

Rows at or above the 75th percentile of engagement rate receive the `High_Performance` label. The classifier excludes likes, comments, shares, impressions, total engagement, engagement rate, and the target itself to prevent target leakage.

## Results

Run the pipeline with the project dataset, then insert the generated values from `output/model_metrics.csv`, `output/feature_importance.csv`, and `output/strategy_summary.json` here. Do not manually estimate metrics.

## Dashboard

Power BI should import `output/postpilot_predictions.csv` and `output/feature_importance.csv`. Use one descriptive page for platform/topic/timing engagement and one predictive page for probabilities, performance segments, and feature importance.

## Limitations and future work

The model does not guarantee virality and currently omits media quality, follower count, hashtags, creator history, platform algorithm changes, and external events. Caption NLP, image/video analysis, platform APIs, A/B testing, and a Streamlit interface are deferred until after the September 4 demo.
