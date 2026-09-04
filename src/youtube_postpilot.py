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
NUMERICAL = ["video_duration_min", "upload_hour", "upload_month", "upload_dayofmonth", "upload_weekofyear"]
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
    df["upload_month"] = df["upload_date"].dt.month
    df["upload_dayofmonth"] = df["upload_date"].dt.day
    df["upload_weekofyear"] = df["upload_date"].dt.isocalendar().week.astype(int)
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
    train_cut = int(len(ordered) * 0.64)
    validation_cut = int(len(ordered) * 0.80)
    train_df = ordered.iloc[:train_cut]
    validation_df = ordered.iloc[train_cut:validation_cut]
    test_df = ordered.iloc[validation_cut:]
    categorical = Pipeline([("imputer", SimpleImputer(strategy="constant", fill_value="missing")), ("encoder", OneHotEncoder(handle_unknown="ignore"))])
    numerical = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    preprocessor = ColumnTransformer([("categorical", categorical, CATEGORICAL), ("numerical", numerical, NUMERICAL)])
    model = Pipeline([("preprocessor", preprocessor), ("classifier", RandomForestClassifier(n_estimators=600, max_depth=18, min_samples_leaf=2, class_weight=None, random_state=42, n_jobs=-1))])
    model.fit(train_df[features], train_df["High_Performance"])
    validation_probability = model.predict_proba(validation_df[features])[:, 1]
    threshold_scores = []
    for threshold_candidate in [i / 100 for i in range(20, 81)]:
        validation_pred = (validation_probability >= threshold_candidate).astype(int)
        validation_recall = recall_score(validation_df["High_Performance"], validation_pred, zero_division=0)
        if validation_recall >= 0.40:
            threshold_scores.append((accuracy_score(validation_df["High_Performance"], validation_pred), f1_score(validation_df["High_Performance"], validation_pred, zero_division=0), threshold_candidate))
    _, _, threshold = max(threshold_scores)
    probability = model.predict_proba(test_df[features])[:, 1]
    pred = (probability >= threshold).astype(int)
    y = test_df["High_Performance"]
    metrics = {"accuracy": accuracy_score(y, pred), "precision": precision_score(y, pred, zero_division=0), "recall": recall_score(y, pred, zero_division=0), "f1": f1_score(y, pred, zero_division=0), "roc_auc": roc_auc_score(y, probability), "decision_threshold": threshold, "majority_baseline_accuracy": float(max(y.mean(), 1 - y.mean()))}
    names = model.named_steps["preprocessor"].get_feature_names_out()
    importance = pd.DataFrame({"Feature": names, "Importance": model.named_steps["classifier"].feature_importances_}).sort_values("Importance", ascending=False)
    return model, metrics, importance, threshold


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()
    df = prepare(args.input)
    model, metrics, importance, threshold = train(df)
    features = CATEGORICAL + NUMERICAL
    result = df.copy()
    result["Predicted_High_Performance"] = (model.predict_proba(result[features])[:, 1] >= threshold).astype(int)
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
