"""Train and evaluate a unified three-class PostPilot benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


CATEGORICAL = ["source_dataset", "platform", "account_type", "media_type", "topic", "campaign_phase", "sentiment_label", "emotion_type", "language", "posting_weekday", "denominator_type", "is_verified"]
NUMERICAL = ["audience_size", "posting_hour", "caption_length", "hashtags_count"]


def train(df: pd.DataFrame):
    df = df.copy()
    for column in CATEGORICAL:
        df[column] = df[column].astype("string").fillna("missing").astype(object)
    for column in NUMERICAL:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    features = CATEGORICAL + NUMERICAL
    ordered = df.sort_values(["source_dataset", "posting_timestamp"]).copy()
    position = ordered.groupby("source_dataset").cumcount()
    size = ordered.groupby("source_dataset")["source_dataset"].transform("size")
    test_mask = position >= (size * 0.8).astype(int)
    train_df, test_df = ordered.loc[~test_mask], ordered.loc[test_mask]
    categorical = Pipeline([("imputer", SimpleImputer(strategy="constant", fill_value="missing")), ("encoder", OneHotEncoder(handle_unknown="ignore"))])
    numerical = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    preprocessor = ColumnTransformer([("categorical", categorical, CATEGORICAL), ("numerical", numerical, NUMERICAL)])
    model = Pipeline([("preprocessor", preprocessor), ("classifier", RandomForestClassifier(n_estimators=400, max_depth=16, min_samples_leaf=2, class_weight="balanced", random_state=42, n_jobs=-1))])
    model.fit(train_df[features], train_df["performance_class"])
    pred = model.predict(test_df[features])
    metrics = {
        "accuracy": accuracy_score(test_df["performance_class"], pred),
        "macro_f1": f1_score(test_df["performance_class"], pred, average="macro"),
        "weighted_f1": f1_score(test_df["performance_class"], pred, average="weighted"),
    }
    by_source = {}
    scored = test_df[["source_dataset", "performance_class"]].copy()
    scored["prediction"] = pred
    for source, group in scored.groupby("source_dataset"):
        by_source[source] = {"accuracy": accuracy_score(group["performance_class"], group["prediction"]), "macro_f1": f1_score(group["performance_class"], group["prediction"], average="macro")}
    return model, metrics, by_source


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("output/unified_model_metrics.json"))
    args = parser.parse_args()
    df = pd.read_csv(args.input, low_memory=False)
    _, metrics, by_source = train(df)
    payload = {"rows": len(df), **metrics, "by_source": by_source}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
