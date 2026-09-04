# PostPilot AI — YouTube Video Analytics Report

## Abstract

PostPilot AI analyzes YouTube video performance and predicts whether a video will fall in the top quartile of total watch time. The workflow uses Python for cleaning, feature engineering, exploratory analysis, Random Forest classification, evaluation, and CSV export for Power BI or Tableau. The dataset is a simulated YouTube Studio-style dataset and is used for academic prototyping.

## Dataset and target

The dataset contains 29,999 videos with upload date, duration, traffic source, content category, impressions, click-through rate, watch duration, watch percentage, likes, comments, shares, subscribers gained, and total watch time. The target is derived from the top 25% of `total_watch_time_hours`.

## Leakage prevention

The model uses only upload hour, upload weekday, video duration, traffic source, and content category. It excludes final views/watch time, impressions, CTR, likes, comments, shares, average view duration, retention, and subscribers gained because these are measured after publication or directly reflect performance.

## Results

The chronological run on 29,999 videos produced accuracy 0.681, precision 0.410, recall 0.617, F1 0.493, and ROC-AUC 0.747. Run `src/youtube_postpilot.py` to regenerate `output/youtube_model_metrics.csv`, `output/youtube_predictions.csv`, and `output/youtube_feature_importance.csv`. Do not claim the model predicts live YouTube performance; the source is simulated.

## Dashboard

Use `output/youtube_predictions.csv` as the Power BI/Tableau source. Recommended visuals are total videos, average watch time, average CTR for descriptive analysis, watch time by category, prediction probability by traffic source, video duration bands, upload hour, performance segments, and feature importance.

## Limitations

The dataset does not contain real channel history, title/description text, thumbnails, audience demographics, or a live API connection. The project is a decision-support prototype, not a production YouTube forecasting system.
