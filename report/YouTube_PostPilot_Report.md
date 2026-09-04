# PostPilot AI — YouTube Video Analytics Report

## Abstract

PostPilot AI analyzes YouTube video performance and predicts whether a video will fall in the top quartile of total watch time. The workflow uses Python for cleaning, feature engineering, exploratory analysis, Random Forest classification, evaluation, and CSV export for Power BI or Tableau. The dataset is a simulated YouTube Studio-style dataset and is used for academic prototyping.

## Dataset and target

The dataset contains 29,999 videos with upload date, duration, traffic source, content category, impressions, click-through rate, watch duration, watch percentage, likes, comments, shares, subscribers gained, and total watch time. The target is derived from the top 25% of `total_watch_time_hours`.

## Leakage prevention

The model uses only information available at upload time: upload hour, weekday, month, day of month, ISO week, video duration, traffic source, and content category. It excludes final views/watch time, impressions, CTR, likes, comments, shares, average view duration, retention, and subscribers gained because these are measured after publication or directly reflect performance.

## Results

The chronological 64/16/20 train/validation/test run on 29,999 videos produced accuracy 0.733, precision 0.461, recall 0.388, F1 0.422, and ROC-AUC 0.772. The model is a Random Forest with a validation-selected decision threshold (0.42); the threshold is selected before the final test evaluation. The majority-class accuracy baseline is 0.749, so accuracy alone is not sufficient evidence of a useful model. Run `src/youtube_postpilot.py` to regenerate the outputs. Do not claim the model predicts live YouTube performance; the source is simulated.

## Dashboard

Use `output/youtube_predictions.csv` as the Power BI/Tableau source. The ready-to-build Power BI instructions are in `dashboard/PowerBI_Setup.md`. Recommended visuals are total videos, average watch time, average CTR for descriptive analysis, watch time by category, prediction probability by traffic source, video duration bands, upload hour, performance segments, and feature importance.

## Limitations

The dataset does not contain real channel history, title/description text, thumbnails, audience demographics, or a live API connection. The project is a decision-support prototype, not a production YouTube forecasting system.
