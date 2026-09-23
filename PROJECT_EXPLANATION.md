# PostPilot AI — Complete Project Explanation

## 1. What the project does

PostPilot AI is a YouTube analytics and prediction system. It takes historical YouTube Studio-style records and answers two questions:

1. Which categories, traffic sources, timings, and video characteristics are associated with stronger performance?
2. Given information known at upload time, how likely is a video to become a high-performing video?

It also produces practical hashtag suggestions. The hashtag module currently uses the video's content category and traffic source because the dataset does not include titles, descriptions, or transcripts.

This is a decision-support prototype. It identifies useful patterns; it does not guarantee virality and it does not connect to live YouTube data.

## 2. End-to-end workflow

```text
YouTube analytics CSV
        |
        v
Clean dates, remove duplicates, validate numeric fields
        |
        v
Create upload hour, weekday, month, day-of-month, and ISO week
        |
        +--> Descriptive analysis: categories, traffic sources, timing, watch time, CTR
        |
        v
Create target: top 25% of total watch time = high performance
        |
        v
Chronological train / validation / test split
        |
        v
Encode categories + train Random Forest classifier
        |
        v
Select decision threshold on validation data
        |
        v
Generate probability, prediction, segment, metrics, and feature importance
        |
        +--> Python dashboard: interactive analysis and filtered downloads
        |
        +--> Power BI PBIP: presentation-ready report pages
        |
        v
Content strategy interpretation and hashtag recommendations
```

## 3. Data used

The primary input is `data/youtube_analytics/YouTube_Video.csv`. The current dataset contains 29,999 simulated YouTube video records with fields such as:

- `post_id`: unique video identifier
- `upload_date`: publication timestamp
- `video_duration_min`: video length
- `content_category`: category such as Education, Comedy, Tech, or Gaming
- `traffic_source`: Browse, Search, Suggested, External, and similar sources
- `impressions`, `ctr_percentage`, `likes`, `comments`, and `shares`
- `avg_view_duration_sec`, `avg_view_percentage`, and `total_watch_time_hours`
- `subscribers_gained`

The dataset is synthetic/academic. It is suitable for demonstrating the workflow, but it should not be described as live YouTube Studio data.

## 4. Data preparation

The Python pipeline:

1. Loads and de-duplicates the CSV.
2. Converts `upload_date` to a real datetime.
3. Removes rows without a valid date, duration, or watch-time value.
4. Derives `upload_hour`, `upload_month`, `upload_dayofmonth`, `upload_weekofyear`, and `upload_weekday`.
5. Calculates the 75th percentile of `total_watch_time_hours`.
6. Labels videos at or above that percentile as `High_Performance = 1`; all others are `0`.

The high-performance label is historical ground truth. It is not an input to the model.

## 5. Leakage prevention

The model only uses information available when a video is uploaded:

- traffic source
- content category
- upload weekday
- video duration
- upload hour
- upload month
- upload day of month
- upload week of year

It does **not** use impressions, CTR, likes, comments, shares, view duration, retention, subscribers gained, or total watch time as model features. Those are outcomes observed after publication. Excluding them prevents target leakage and makes the prediction claim technically defensible.

## 6. Predictive model

The model is a `RandomForestClassifier` with 600 trees, maximum depth 18, minimum leaf size 2, and parallel training. Categorical columns are one-hot encoded and numerical columns are median-imputed.

The data is ordered chronologically:

- 64% training data
- 16% validation data
- 20% final test data

The validation set selects the probability threshold. The final test set is used only for reporting performance. This is more realistic than randomly mixing future videos into the training data.

The current test results are approximately:

- Accuracy: 73.25%
- Precision: 46.08%
- Recall: 38.80%
- F1: 42.16%
- ROC-AUC: 77.16%
- Decision threshold: 0.42

F1 and ROC-AUC are more informative than accuracy because only the top quartile is labelled high performance and the classes are imbalanced.

## 7. Prediction outputs

For each video, the pipeline exports:

- `Predicted_High_Performance`: 0 or 1
- `High_Performance_Probability`: model confidence from 0 to 1
- `Performance_Segment`:
  - Low Intent: 0–35%
  - Medium Intent: 35–65%
  - High Intent: 65–100%

The output files are:

- `output/youtube_predictions.csv`: row-level predictions and source metrics
- `output/youtube_model_metrics.csv`: accuracy, precision, recall, F1, ROC-AUC, threshold
- `output/youtube_feature_importance.csv`: model feature contributions
- `output/youtube_hashtags.csv`: recommended hashtags and relevance scores

## 8. Hashtag generation

The hashtag generator creates several recommendations using the combination of `content_category` and `traffic_source`. For example, a Comedy video from Browse traffic receives category/source combinations such as `#ComedyBrowse` plus related category tags.

The relevance score is a ranking signal, not a probability of virality. Specific title/transcript-based hashtags require adding title, description, or transcript columns in a future version.

## 9. Python dashboard guide

Run `RUN_DASHBOARD.ps1` or start Streamlit with:

```powershell
streamlit run dashboard/app.py
```

Open `http://127.0.0.1:8501`.

The dashboard has three tabs:

### Overview

- KPI cards for filtered videos, watch time, CTR, impressions, and subscribers
- Watch time by category
- CTR by traffic source
- Upload volume by weekday
- Watch time by weekday
- Predicted high-performance rate by traffic source
- Duration versus total watch time scatter plot
- Category comparison table
- Dynamic category comparison selector

### Predictions

- Predicted high-video count
- Average probability
- Accuracy, F1, and ROC-AUC
- High-performance videos by category
- Prediction segment distribution
- Probability by traffic source
- Probability distribution bands
- Top model features
- Highest-probability video table

### Hashtags

- Average hashtag relevance
- Average hashtags per video
- Relevance by generation source
- Hashtag count by category
- Filtered hashtag recommendation table

All visuals respond to the sidebar filters. The app also detects changed output-file timestamps, has a refresh button, supports filter reset, shows the active row count, and allows filtered CSV downloads.

## 10. Power BI report guide

Open `powerbi/PostPilot_AI_YouTube/Power BI Project.pbip`.

The report contains:

1. `Channel Overview`: KPIs, category watch-time comparison, traffic-source CTR, weekday upload coverage, duration/watch-time scatter, and slicers.
2. `Complete Analysis Dashboard`: one-page presentation view combining the main KPIs, category comparison, traffic-source comparison, timing, prediction segments, probability, scatter analysis, and decision table.
3. `Model Evidence & Diagnostics`: test metrics, decision threshold, prediction agreement, feature importance, actual-versus-predicted category comparison, traffic-source comparisons, and review table.
4. `Prediction and Hashtag Strategy`: prediction KPIs, predicted high-performance comparison, segment distribution, probability comparisons, hashtag table, and slicers.
5. `Strategy Deep Dive`: weekday watch-time, weekday upload coverage, category/source probability, duration/watch-time, and decision-guide visuals.
6. `Hashtag Prediction & Action Plan`: explicitly shows predicted high-performance rate, prediction confidence, hashtag relevance, hashtag counts, generation source, slicers, and the recommended hashtag table.

The semantic model also contains a `FeatureImportance` table and two evidence measures, `Actual High Videos` and `Prediction Agreement`, so the report can compare what happened historically with what the classifier predicted.

Use slicers to compare categories, traffic sources, performance segments, and hashtag-generation sources. Tables are included because they expose the exact values behind the charts and make the dashboard easier to explain during a presentation.

## 11. How to interpret the project

- A high probability means the model sees a stronger likelihood of belonging to the historical top-watch-time group; it is not a guarantee.
- A high CTR means a larger share of impressions generated clicks, but CTR alone does not prove strong watch time.
- A high watch-time value indicates stronger viewing duration and is the target-related outcome used to label high-performance videos.
- A traffic source comparison shows where discovery is associated with stronger outcomes; it does not prove that the source caused the result.
- Feature importance describes what the Random Forest used most in this dataset; it is not causal evidence.

## 12. Recommended presentation flow

1. Introduce the problem: normal dashboards explain past performance, while PostPilot AI adds a pre-publication estimate.
2. Show the input fields and explain the leakage rule.
3. Explain the top-quartile high-performance target.
4. Show the chronological train/validation/test design.
5. Present F1 and ROC-AUC, not accuracy alone.
6. Use the Python dashboard to compare categories, sources, timing, probability, and hashtags.
7. Use Power BI for the polished executive view and slicer-driven comparisons.
8. Close with limitations: synthetic data, no live API, no title/transcript features, and no guarantee of virality.

## 13. Reproducibility

To regenerate the YouTube outputs:

```powershell
python src/youtube_postpilot.py --input data/youtube_analytics/YouTube_Video.csv --output output
python src/hashtag_generator.py --input output/youtube_predictions.csv --output output/youtube_hashtags.csv
```

Then refresh the Python dashboard or reopen/refresh the Power BI PBIP report. The dashboard automatically invalidates its data cache when the output files change.

## 14. One-sentence project statement

PostPilot AI combines YouTube analytics, leakage-safe Random Forest prediction, hashtag recommendations, Python exploration, and Power BI reporting to help creators compare content strategies before publishing.
