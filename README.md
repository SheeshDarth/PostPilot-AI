# PostPilot AI

PostPilot AI predicts whether a social-media post is likely to be in the top engagement quartile using only attributes available before publication.

## Current status

This repository contains the reproducible Python pipeline. The source dataset is intentionally not included because the workspace only contained the project brief. Place it at `data/social_media_engagement.csv`.

## Expected input columns

`Timestamp`, `Platform`, `Topic Category`, `Campaign Phase`, `Sentiment Label`, `Emotion Type`, `Sentiment Score`, `Likes Count`, `Comments Count`, `Shares Count`, and `Impressions`.

The engagement columns create the historical target but are excluded from model features to prevent target leakage.

## Run

```powershell
python -m pip install -r requirements.txt
python src/postpilot_pipeline.py --input data/social_media_engagement.csv --output output
```

The command writes cleaned/predicted data, model metrics, feature importance, and a strategy summary to `output/`.

## Outputs

- `postpilot_predictions.csv` — cleaned rows, derived features, predictions, probabilities, and segments.
- `model_metrics.csv` — accuracy, precision, recall, F1, and ROC-AUC.
- `feature_importance.csv` — Random Forest importances.
- `strategy_summary.json` — best historical platform, topic, weekday, hour, sentiment, and emotion.

Power BI can load `postpilot_predictions.csv` and `feature_importance.csv` after the pipeline completes.
