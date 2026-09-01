# PostPilot AI

PostPilot AI predicts whether a social-media post is likely to be in the top engagement quartile using only attributes available before publication.

## Current status

This repository contains the reproducible Python pipeline. The working dataset is downloaded locally from Kaggle and is intentionally not included in Git because it is raw data. See `data/README.md` for provenance.

## Expected input columns

`Timestamp`, `Platform`, `Topic Category`, `Campaign Phase`, `Sentiment Label`, `Emotion Type`, `Sentiment Score`, `Likes Count`, `Comments Count`, `Shares Count`, and `Impressions`.

The engagement columns create the historical target but are excluded from model features to prevent target leakage.

## Run

```powershell
python -m pip install -r requirements.txt
python src/postpilot_pipeline.py --input data/social_media_engagement.csv --output output
```

The command writes cleaned/predicted data, model metrics, feature importance, and a strategy summary to `output/`.

The chronological leakage-safe metadata baseline produced ROC-AUC 0.489 and F1 0.132. The current version adds TF-IDF word/bigram features from pre-publication text and produces F1 0.202 with recall 0.169; ROC-AUC remains 0.489, confirming that the synthetic dataset has weak ranking signal. Use `--split random` only for comparison; the default is the more realistic time split.

## Outputs

- `postpilot_predictions.csv` — cleaned rows, derived features, predictions, probabilities, and segments.
- `model_metrics.csv` — accuracy, precision, recall, F1, and ROC-AUC.
- `feature_importance.csv` — Random Forest importances.
- `strategy_summary.json` — best historical platform, topic, weekday, hour, sentiment, and emotion.

Power BI can load `postpilot_predictions.csv` and `feature_importance.csv` after the pipeline completes.

## Rich dataset experiment

The richer 20,000-row experiment is available through `src/postpilot_rich_pipeline.py` and uses followers, account age, media presence, demographics, device, hashtags, content, and timing. Run it with:

```powershell
python src/postpilot_rich_pipeline.py --input data/dataset_2025/synthetic_social_media_engagement.csv
```

Its chronological baseline produced ROC-AUC 0.516 and F1 0.217. Adding creator-history, creator/topic-history, and device/topic-history features computed only from earlier posts improved ROC-AUC to 0.532 and F1 to 0.244. The improvement is measurable but not sufficient for an 85% claim; the dataset is synthetic and its pre-publication fields contain limited signal.
