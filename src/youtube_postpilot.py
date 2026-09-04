"""PostPilot AI: YouTube video performance analysis and prediction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


CATEGORICAL = ["traffic_source", "content_category", "upload_weekday"]
NUMERICAL = ["video_duration_min", "upload_hour"]
OUTCOMES = ["avg_view_duration_sec", "avg_view_percentage", "subscribers_gained", "ctr_percentage", "impressions", "likes", "comments", "shares", "total_watch_time_hours"]


def prepare(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path).drop_duplicates().copy()
    required = {"post_id", "upload_date", "video_duration_min", "traffic_source", "content_category", *OUTCOMES}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")
    df = df.dropna(subset=["upload_date", "video_duration_min", "total_watch_time_hours"]).copy()
    df["upload_hour"] = df["upload_date"].dt.hour
    df["upload_weekday"] = df["upload_date"].dt.day_name()
    df["total_watch_time_hours"] = pd.to_numeric(df["total_watch_time_hours"], errors="coerce")
    threshold = df["total_watch_time_hours"].quantile(0.75)
    df["High_Performance"] = (df["total_watch_time_hours"] >= threshold).astype(int)
    for column in CATEGORICAL:
        df[column] = df[column].astype("string").fillna("missing").astype(object)
    return df


def train(df: pd.DataFrame):
    features = CATEGORICAL + NUMERICAL
    ordered = df.sort_values("upload_date")
    cut = int(len(ordered) * 0.8)
    train_df, test_df = ordered.iloc[:cut], ordered.iloc[cut:]
    categorical = Pipeline([("imputer", SimpleImputer(strategy="constant", fill_value="missing")), ("encoder", OneHotEncoder(handle_unknown="ignore"))])
    numerical = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    preprocessor = ColumnTransformer([("categorical", categorical, CATEGORICAL), ("numerical", numerical, NUMERICAL)])
    model = Pipeline([("preprocessor", preprocessor), ("classifier", RandomForestClassifier(n_estimators=400, max_depth=16, min_samples_leaf=2, class_weight="balanced", random_state=42, n_jobs=-1))])
    model.fit(train_df[features], train_df["High_Performance"])
    pred = model.predict(test_df[features])
    probability = model.predict_proba(test_df[features])[:, 1]
    y = test_df["High_Performance"]
    metrics = {"accuracy": accuracy_score(y, pred), "precision": precision_score(y, pred, zero_division=0), "recall": recall_score(y, pred, zero_division=0), "f1": f1_score(y, pred, zero_division=0), "roc_auc": roc_auc_score(y, probability)}
    names = model.named_steps["preprocessor"].get_feature_names_out()
    importance = pd.DataFrame({"Feature": names, "Importance": model.named_steps["classifier"].feature_importances_}).sort_values("Importance", ascending=False)
    return model, metrics, importance


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()
    df = prepare(args.input)
    model, metrics, importance = train(df)
    features = CATEGORICAL + NUMERICAL
    result = df.copy()
    result["Predicted_High_Performance"] = model.predict(result[features])
    result["High_Performance_Probability"] = model.predict_proba(result[features])[:, 1]
    result["Performance_Segment"] = pd.cut(result["High_Performance_Probability"], [0, .35, .65, 1], labels=["Low Intent", "Medium Intent", "High Intent"], include_lowest=True)
    args.output.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output / "youtube_predictions.csv", index=False)
    pd.DataFrame([metrics]).to_csv(args.output / "youtube_model_metrics.csv", index=False)
    importance.to_csv(args.output / "youtube_feature_importance.csv", index=False)
    (args.output / "youtube_model_metrics.json").write_text(json.dumps({"rows": len(df), "high_performance_rate": float(df["High_Performance"].mean()), **metrics}, indent=2), encoding="utf-8")
    print(json.dumps({"rows": len(df), **metrics}, indent=2))


if __name__ == "__main__":
    main()
