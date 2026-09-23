# PostPilot AI — Teammate Guide

This is the final, beginner-friendly workflow for the YouTube project. The current implementation is called **PostPilot AI** and uses the YouTube dataset, Python/Streamlit, and Power BI.

## What the project does

PostPilot AI:

1. cleans and engineers YouTube video analytics data;
2. describes categories, traffic sources, timing coverage, CTR, watch time, and engagement;
3. predicts the probability that a video belongs to the historical top-watch-time quartile;
4. evaluates that prediction with accuracy, precision, recall, F1, ROC-AUC, and a decision threshold;
5. generates category/source-based hashtag recommendations; and
6. presents the same analysis in a dynamic Python dashboard and a presentation-ready Power BI report.

The dataset is academic/simulated. The output is a decision-support demonstration, not a live YouTube virality guarantee.

## 1. Install Python

Install Python 3.11 or newer from <https://www.python.org/downloads/>. During installation, select **Add Python to PATH**.

## 2. Open the project

Extract this ZIP and open the extracted `PE3 project` folder. In File Explorer, click the address bar, type `powershell`, and press Enter.

## 3. Install libraries

Run:

```powershell
python -m pip install -r requirements.txt
```

## 4. Re-run the Python pipeline

Run these commands from the project root:

```powershell
python src/youtube_postpilot.py --input data/youtube_analytics/YouTube_Video.csv --output output
python src/hashtag_generator.py --input data/youtube_analytics/YouTube_Video.csv --output output/youtube_hashtags.csv
```

Or run the one-click script:

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN_PROJECT.ps1
```

The pipeline writes:

- `output/youtube_predictions.csv` — one row per video with prediction probability and prediction flag;
- `output/youtube_hashtags.csv` — one row per video with recommended hashtags and relevance score;
- `output/youtube_model_metrics.csv` — held-out evaluation metrics;
- `output/youtube_feature_importance.csv` — model feature ranking.

## 5. Verify the current benchmark

The current leakage-safe chronological benchmark is:

| Metric | Value |
|---|---:|
| Accuracy | 73.25% |
| Precision | 46.10% |
| Recall | 38.84% |
| F1 | 42.16% |
| ROC-AUC | 77.16% |
| Decision threshold | 0.42 |

The majority-class accuracy baseline is 74.90%, so present all metrics together. Do not add post-publication likes, comments, impressions, watch time, or subscriber gains as model inputs just to inflate accuracy; that would leak the outcome into the prediction.

## 6. Open the dynamic Python dashboard

Run:

```powershell
streamlit run dashboard/app.py
```

Open `http://127.0.0.1:8501`.

The dashboard has three tabs:

- **Overview** — KPIs, category and traffic-source comparisons, weekday timing coverage, watch-time comparisons, dynamic metric selection, and duration versus watch-time scatter;
- **Predictions** — predicted-high videos, probability distribution, actual-versus-predicted comparison, model metrics, feature importance, and highest-probability review table;
- **Hashtags** — hashtag relevance, hashtag count, generation source, recommendations, and filtered downloads.

Use the sidebar filters to compare categories, traffic sources, performance segments, and minimum probability. Click **Refresh latest pipeline data** after regenerating the CSV outputs.

## 7. Open the Power BI report

Open this canonical PBIP file in Power BI Desktop:

```text
powerbi\PostPilot_AI_YouTube\Power BI Project.pbip
```

The Power BI report already contains six pages. Do not manually rebuild them unless Power BI asks to refresh the CSV sources.

### Page 1 — Channel Overview

- Total Videos
- Average Watch Time
- Average CTR
- Total Impressions
- Subscribers Gained
- Watch Time by Category
- CTR by Traffic Source
- Upload Volume by Weekday
- Video Duration versus Total Watch Time
- Content Category, Traffic Source, and Performance Segment slicers

### Page 2 — Complete Analysis Dashboard

This is the presentation page. It combines scale KPIs, category/source comparisons, predicted-high counts, probability, prediction segments, timing coverage, duration/watch-time analysis, and a category decision table.

### Page 3 — Model Evidence & Diagnostics

- Test Accuracy, Test F1, Test ROC-AUC
- Decision Threshold and Prediction Agreement
- Predicted High Rate
- Top Model Features
- Actual versus Predicted High Videos by Category
- Average Probability and Predicted High Videos by Traffic Source
- Metrics table and highest-probability review table

### Page 4 — Prediction and Hashtag Strategy

- Predicted high videos and predicted-high rate
- Average prediction probability and hashtag relevance
- Test Accuracy, F1, and ROC-AUC
- High-performance videos by category
- Prediction segment distribution
- Probability by traffic source
- Recommended hashtags table

### Page 5 — Strategy Deep Dive

Use this page for weekday watch-time, weekday upload coverage, category/source probability, duration/watch-time relationship, and the decision-guide table.

### Page 6 — Hashtag Prediction & Action Plan

This is the explicit hashtag-prediction page. It shows:

- average hashtag relevance;
- average hashtags per video;
- hashtag relevance by generation source;
- hashtags by category;
- prediction segment distribution;
- recommended hashtags beside video ID, category, traffic source, probability, prediction flag, relevance, source, and count;
- slicers for category, traffic source, performance segment, and hashtag source.

The model table name is intentionally spelled `YouTubeHastags` in the PBIP schema. Keep that spelling if Power BI displays it.

## 8. Refreshing Power BI after a new Python run

1. Close Power BI Desktop before changing the CSV files.
2. Run the two Python commands in Step 4.
3. Reopen `powerbi\PostPilot_AI_YouTube\Power BI Project.pbip`.
4. Select **Home → Refresh** if Power BI does not load the new values automatically.
5. Check that the report opens with all slicers unfiltered. Apply filters only when comparing a specific segment.

## 9. How to present the project

1. Explain the problem: normal dashboards show what already happened; PostPilot AI adds a pre-publication probability estimate.
2. Show the Python Overview tab for descriptive analysis.
3. Show Power BI Page 2 for the complete comparison story.
4. Show Power BI Page 3 to prove the model is evaluated, not just displayed.
5. Show Power BI Page 6 and the Python Hashtags tab to explain the recommendation layer.
6. State the limitation clearly: hashtag recommendations are category/source fallbacks because the dataset has no title, description, keyword, or transcript fields.

## Troubleshooting

- If `python` is not recognized, reinstall Python and select **Add Python to PATH**.
- If the dashboard is blank, run `RUN_PROJECT.ps1` and confirm the four YouTube output files exist.
- If Power BI shows old values, close Power BI, rerun the pipeline, reopen the PBIP, and select **Refresh**.
- If the report opens filtered to a small number of videos, use **Reset to default** or clear the slicers; the canonical files are saved with no default slicer selections.

## Important limitation

The source currently uses one upload hour for every record. The dashboards therefore show weekday coverage instead of implying that one hour is better than another. This is a data-quality limitation, not a missing feature.
