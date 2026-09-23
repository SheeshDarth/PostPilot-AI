# PostPilot AI — YouTube Predictive Analytics and Hashtag Strategy

## Abstract

PostPilot AI is an academic decision-support system for YouTube creators. It combines descriptive analytics, a leakage-safe machine-learning model, and a hashtag recommendation layer. The system analyzes 29,999 YouTube Studio-style records, compares content categories and traffic sources, estimates the probability that a video belongs to the historical top-watch-time quartile, and presents the results through Python/Streamlit and Power BI.

The reference reports supplied with this project were used as presentation benchmarks: an executive KPI page, a model-evidence page, a performance/comparison page, and an actionable recommendation view. Their platform-specific facts were not copied into PostPilot AI; all figures below are from this YouTube project.

## 1. Problem statement

Most analytics dashboards explain performance after a video is published. The project asks whether information available at upload time can be used to estimate high watch-time performance before publication, while still showing the evidence and limitations behind the estimate.

The system answers four practical questions:

1. Which content categories and traffic sources are associated with stronger watch time and CTR?
2. Which upload-time characteristics are most useful to the model?
3. Which videos cross the model's decision threshold for high performance?
4. Which category/source-based hashtag recommendations can be shown alongside the prediction?

## 2. Data and preparation

The primary input is `data/youtube_analytics/YouTube_Video.csv`. It contains 29,999 simulated/academic YouTube records with video identifiers, upload dates, duration, content category, traffic source, impressions, CTR, views/watch-time outcomes, engagement counts, retention fields, and subscribers gained.

The Python pipeline de-duplicates records, parses `upload_date`, removes rows without a valid date/duration/watch-time value, and derives:

- upload hour
- upload month
- upload day of month
- ISO week of year
- upload weekday

The historical target is defined as:

```text
High_Performance = 1 when total_watch_time_hours is at or above its 75th percentile
High_Performance = 0 otherwise
```

This is a top-quartile classification problem, not a regression claim about exact future watch hours.

## 3. Leakage control

The model uses only fields available at upload time:

- `traffic_source`
- `content_category`
- `upload_weekday`
- `video_duration_min`
- `upload_hour`
- `upload_month`
- `upload_dayofmonth`
- `upload_weekofyear`

It excludes post-publication outcomes such as impressions, CTR, likes, comments, shares, average view duration, retention, subscribers gained, and total watch time. Those fields are used for historical analysis and target construction only. This separation is essential: using them as predictors would leak the answer into the model.

## 4. Predictive method

The records are ordered chronologically and split into 64% training, 16% validation, and 20% final test data. Categorical variables are one-hot encoded and numerical variables are median-imputed. The classifier is a 600-tree `RandomForestClassifier` with maximum depth 18, minimum leaf size 2, and fixed random state 42.

The validation set selects the probability threshold from 0.20–0.80 while requiring at least 0.40 recall. The current selected threshold is 0.42. The final test set is held out from threshold selection.

## 5. Model evidence

Current saved test metrics:

| Metric | Value |
|---|---:|
| Accuracy | 73.25% |
| Precision | 46.10% |
| Recall | 38.84% |
| F1 | 42.16% |
| ROC-AUC | 77.16% |
| Decision threshold | 0.42 |
| Majority-class accuracy baseline | 74.90% |

Accuracy is not sufficient by itself because only the historical top quartile is positive. F1, recall, and ROC-AUC are shown beside accuracy so the report does not overstate model quality. A prediction probability indicates similarity to the learned high-performance pattern; it is not a guarantee of virality.

The Power BI model now includes `FeatureImportance`, loaded from `output/youtube_feature_importance.csv`, so the report can show which encoded inputs the Random Forest used most. Feature importance is model usage, not causal proof.

## 6. Hashtag recommendation module

The hashtag layer joins each video to `output/youtube_hashtags.csv` using `post_id`. It displays:

- recommended hashtag string
- relevance score
- hashtag count
- generation source

Because the source data has no video title, description, keywords, or transcript, the current generator uses category/source fallback metadata. The recommendations are useful for demonstrating the workflow and ranking logic, but they are not semantic, transcript-aware, or a guarantee of reach. Adding title and transcript features is the correct next step for genuinely video-specific hashtag suggestions.

## 7. Dashboard design aligned to the reference reports

The reference reports support a decision-oriented dashboard rather than a collection of unrelated charts. The Power BI report therefore uses these views:

### Executive Overview

- KPI cards: total videos, total impressions, average watch time, average CTR, predicted-high rate
- average watch time by content category
- average CTR by traffic source
- upload volume by weekday
- duration versus watch time scatter
- category decision table with count, watch time, CTR, probability, and predicted-high count

### Prediction and Hashtag Strategy

- predicted-high count and rate
- average prediction probability
- average hashtag relevance and hashtags per video
- test accuracy, F1, and ROC-AUC
- predicted-high videos by category
- prediction-segment distribution
- probability by traffic source
- recommended hashtag table with filtering

### Model Evidence and Recommendations

- test metric cards and decision threshold
- feature-importance ranking
- actual versus predicted high-performance comparison by category
- prediction probability by traffic source/category
- highest-probability video table
- explanation of leakage control and interpretation limits

### Strategy Deep Dive

- weekday watch-time comparison
- weekday upload coverage
- predicted high videos by category
- average probability by traffic source
- duration/watch-time relationship
- category/source decision table

### Hashtag Prediction and Action Plan

- explicit hashtag relevance comparison
- hashtag count by category
- prediction segment distribution
- recommended tags beside probability and relevance values
- content, source, segment, and hashtag-source slicers

The Python dashboard mirrors the same analytical story in three tabs: Overview, Predictions, and Hashtags. It is the exploratory/diagnostic interface; Power BI is the presentation and comparison interface.

## 8. How to interpret the most important charts

- **Watch time by category:** identifies categories associated with higher average watch time; it does not prove category causes watch time.
- **CTR by traffic source:** compares discovery-source click-through rates; it does not prove source placement caused the CTR.
- **Upload volume by weekday:** describes the weekday coverage in the source; it is a descriptive comparison, not proof that one day causes stronger performance.
- **Duration versus watch time:** shows the relationship between video length and watch time at row level; extreme points should be investigated rather than blindly recommended.
- **Prediction segment distribution:** explains how many videos fall into low, medium, and high probability bands.
- **Actual versus predicted comparison:** compares historical labels with model flags; the gap is evidence of model error and is more informative than a single accuracy card.
- **Feature importance:** ranks model inputs; it is not a causal ranking.
- **Hashtag relevance:** compares the recommendation layer's ranking score, not future views.

## 9. Reproduction

From the project root:

```powershell
python src/youtube_postpilot.py --input data/youtube_analytics/YouTube_Video.csv --output output
python src/hashtag_generator.py --input output/youtube_predictions.csv --output output/youtube_hashtags.csv
streamlit run dashboard/app.py
```

Then open `powerbi/PostPilot_AI_YouTube/Power BI Project.pbip` in Power BI Desktop and refresh the model if required. The CSV outputs are the shared source for Python and Power BI, so both dashboards can be compared against the same rows and metrics.

## 10. Limitations

- The dataset is simulated/static and is not live YouTube Studio or YouTube Analytics API data.
- The model does not use titles, descriptions, thumbnails, transcripts, creator history, subscribers, or audience demographics.
- The dataset's time distribution is narrow: every source row uses upload hour 7. The report therefore uses weekday coverage and does not present a false hourly timing recommendation.
- Hashtag recommendations are category/source fallback tags until text features are added.
- Power BI report values are descriptive summaries of the academic dataset and saved model artifacts.
- The model estimates membership in a historical top-watch-time group; it does not forecast exact views or guarantee virality.

## 11. Conclusion

PostPilot AI converts a YouTube analytics CSV into a reproducible decision-support workflow: clean and describe the data, label the historical top-watch-time group, train and evaluate a leakage-safe classifier, rank model evidence, recommend category/source-based hashtags, and expose the results in Python and Power BI. Its strongest academic contribution is the connection between descriptive BI, defensible predictive evaluation, and an actionable recommendation layer without presenting associations as causal or predictions as guarantees.
