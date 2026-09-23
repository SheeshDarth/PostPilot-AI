# PostPilot AI Dashboard Specification

The final dashboard domain is YouTube video analytics. The Python pipeline and Power BI report use the same generated outputs, so their values can be compared directly.

## Sources

- `output/youtube_predictions.csv`
- `output/youtube_hashtags.csv`
- `output/youtube_model_metrics.csv`
- `output/youtube_feature_importance.csv`

The semantic-model table names are `YouTube`, `YouTubeHastags`, and `FeatureImportance`. Keep the spelling `YouTubeHastags` because it is already part of the PBIP model.

## Canonical Power BI report

Open:

```text
powerbi\PostPilot_AI_YouTube\Power BI Project.pbip
```

The report contains:

1. `Channel Overview` — KPI cards, watch time by category, CTR by traffic source, weekday upload coverage, duration/watch-time scatter, and slicers.
2. `Complete Analysis Dashboard` — presentation-ready comparison page.
3. `Model Evidence & Diagnostics` — test metrics, feature importance, actual-versus-predicted labels, probability/source comparisons, and review tables.
4. `Prediction and Hashtag Strategy` — prediction metrics, performance segments, probabilities, and hashtag table.
5. `Strategy Deep Dive` — timing, duration, category, source, and decision-guide comparisons.
6. `Hashtag Prediction & Action Plan` — explicit hashtag relevance, hashtag counts, source comparison, recommendations, and filters.

## Python dashboard

Run from the project root:

```powershell
streamlit run dashboard/app.py
```

Open `http://127.0.0.1:8501`. The three tabs are `Overview`, `Predictions`, and `Hashtags`. The sidebar filters dynamically update all cards, charts, tables, and downloads.

## Reproduction

```powershell
python src/youtube_postpilot.py --input data/youtube_analytics/YouTube_Video.csv --output output
python src/hashtag_generator.py --input data/youtube_analytics/YouTube_Video.csv --output output/youtube_hashtags.csv
```

For exact visual bindings and page layout, read `dashboard/PowerBI_Setup.md`. For interpretation rules, read `CHART_GUIDE.md` and `report/YouTube_PostPilot_Report.md`.
