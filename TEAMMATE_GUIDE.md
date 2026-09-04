# PostPilot AI — Teammate Guide

This guide is designed for someone who does not want to write code. Follow the steps in order.

## What this project does

PostPilot AI analyzes YouTube videos and predicts whether a future video is likely to be high-performing. It also exports tables for Power BI or Tableau.

Use the **YouTube pipeline** for the final demo. Do not start with the older Instagram or unified experiments.

## Step 1 — Install Python

Install Python 3.11 or newer from <https://www.python.org/downloads/>. During installation, select **Add Python to PATH**.

## Step 2 — Open the project

Extract this ZIP. Open the extracted `PE3 project` folder.

In File Explorer, click the address bar, type `powershell`, and press Enter.

## Step 3 — Install libraries

Copy and run:

```powershell
python -m pip install -r requirements.txt
```

## Step 4 — Run the final YouTube analysis

Copy and run:

```powershell
python src/youtube_postpilot.py --input data/youtube_analytics/YouTube_Video.csv --output output
python src/hashtag_generator.py --input data/youtube_analytics/YouTube_Video.csv --output output/youtube_hashtags.csv
```

You should see metrics printed in the terminal. The run creates the dashboard files in `output/`.

## Step 5 — Check the results

Open these files:

- `output/youtube_model_metrics.csv` — model metrics
- `output/youtube_predictions.csv` — main dashboard table
- `output/youtube_feature_importance.csv` — model feature importance
- `output/instagram_analysis_media_type.csv`
- `output/instagram_analysis_content_category.csv`
- `output/instagram_analysis_post_hour.csv`
- `output/instagram_analysis_traffic_source.csv`

The current leakage-safe YouTube chronological benchmark is 73.25% accuracy, 0.772 ROC-AUC, and 0.422 F1. The majority-class accuracy baseline is 74.9%, so report all metrics together. Do not change the result to 85% by adding final likes, comments, shares, impressions, watch time, or subscriber gains as model inputs; those are post-publication outcomes.

## Step 6 — Create the Power BI dashboard

1. Open Power BI Desktop.
2. Select **Get data → Text/CSV**.
3. Select `output/instagram_predictions.csv`.
4. Click **Load**.
5. Rename the table to `Instagram` if needed.
6. Create Page 1 named **Instagram Performance**.
7. Add cards for total posts, average engagement rate, total reach, average followers, and high-performance posts.
8. Add bar charts for media type, content category, and traffic source.
9. Add a line chart using `post_hour` and average `engagement_rate_calculated`.
10. Add slicers for media type, content category, traffic source, account type, and day of week.
11. Create Page 2 named **Predictive Strategy**.
12. Import `output/instagram_feature_importance.csv` as a second table.
13. Add cards for predicted high-performance posts, average prediction probability, F1, and ROC-AUC.
14. Add a chart for `High_Performance_Probability` by media type and content category.
15. Add a table with `post_id`, `media_type`, `content_category`, `post_hour`, `High_Performance_Probability`, and `Predicted_High_Performance`.
16. Save the file as `dashboard/PostPilot_AI.pbix`.

## Step 7 — Create the report

Use `report/YouTube_PostPilot_Report.md` as the report content. Add screenshots of both Power BI pages and export the final report to PDF.

## Step 6A — Hashtag recommendations

The hashtag file is `output/youtube_hashtags.csv`. Import it into Power BI as `YouTubeHashtags` and connect it to `YouTube` using `post_id`. The current dataset has no title or transcript, so the first run uses category and traffic-source fallback labels. For video-specific hashtags, add `title`, `description`, `transcript`, or `keywords` columns to the input CSV and rerun the generator.

## Step 8 — Demo script

1. Explain the problem: dashboards usually show what already happened.
2. Show the dataset fields and cleaning process.
3. Explain the engagement-rate formula and top-quartile target.
4. Show the Python metrics and feature importance.
5. Show Power BI Page 1 for descriptive insights.
6. Show Power BI Page 2 for prediction probabilities.
7. Explain that the model predicts probability, not guaranteed virality.

## Troubleshooting

If `python` is not recognized, reinstall Python and select **Add Python to PATH**.

If a file is not found, confirm that the PowerShell window is inside the extracted project folder.

If Power BI asks whether to load or transform the CSV, choose **Load**.

If a metric is different, rerun the Python command and use the newly generated output files.

## Optional unified experiment

Only run this after the Instagram dashboard is complete:

```powershell
python src/unify_datasets.py --original data/social_media_engagement.csv --social-2025 data/dataset_2025/synthetic_social_media_engagement.csv --instagram data/instagram_analytics/Instagram_Analytics.csv
python src/unified_postpilot.py --input output/unified_social_media.csv --output output/unified_model_metrics.json
```

The unified data is for comparison only because its sources use different engagement denominators.
