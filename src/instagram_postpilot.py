"""End-to-end Instagram analytics, prediction, and dashboard export pipeline."""

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


CATEGORICAL = ["account_type", "media_type", "content_category", "traffic_source", "has_call_to_action", "day_of_week"]
NUMERICAL = ["follower_count", "post_hour", "caption_length", "hashtags_count", "prior_account_rate", "prior_account_posts"]
OUTCOME_COLUMNS = ["likes", "comments", "shares", "saves", "reach", "impressions", "engagement_rate", "followers_gained", "performance_bucket_label"]


def prepare(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path).drop_duplicates().copy()
    required = {"account_id", "post_datetime", *CATEGORICAL, "follower_count", "post_hour", "caption_length", "hashtags_count", *OUTCOME_COLUMNS}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    df["post_datetime"] = pd.to_datetime(df["post_datetime"], errors="coerce")
    df = df.dropna(subset=["post_datetime", "follower_count", "likes", "comments", "shares", "saves"])
    df = df[df["follower_count"] > 0].copy()
    df["post_hour"] = df["post_datetime"].dt.hour
    df["caption_length"] = pd.to_numeric(df["caption_length"], errors="coerce")
    df["caption_length"] = df["caption_length"].fillna(df["caption_length"].median())
    df["hashtags_count"] = pd.to_numeric(df["hashtags_count"], errors="coerce").fillna(0)
    df["engagement_rate_calculated"] = (df["likes"] + df["comments"] + df["shares"] + df["saves"]) / df["follower_count"] * 100

    ordered = df.sort_values("post_datetime").copy()
    ordered["prior_account_rate"] = ordered.groupby("account_id")["engagement_rate_calculated"].transform(lambda values: values.shift().expanding().mean())
    ordered["prior_account_posts"] = ordered.groupby("account_id").cumcount()
    df = ordered.sort_index()
    df["prior_account_rate"] = df["prior_account_rate"].fillna(df["engagement_rate_calculated"].median())
    df["prior_account_posts"] = df["prior_account_posts"].fillna(0)
    for column in CATEGORICAL:
        df[column] = df[column].astype("string")
    threshold = df["engagement_rate_calculated"].quantile(0.75)
    df["High_Performance"] = (df["engagement_rate_calculated"] >= threshold).astype(int)
    return df


def train(df: pd.DataFrame):
    features = CATEGORICAL + NUMERICAL
    ordered = df.sort_values("post_datetime")
    cut = int(len(ordered) * 0.8)
    train_df, test_df = ordered.iloc[:cut], ordered.iloc[cut:]
    categorical = Pipeline([("imputer", SimpleImputer(strategy="constant", fill_value="missing")), ("encoder", OneHotEncoder(handle_unknown="ignore"))])
    numerical = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    preprocessor = ColumnTransformer([
        ("categorical", categorical, CATEGORICAL),
        ("numerical", numerical, NUMERICAL),
    ])
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=400, max_depth=16, min_samples_leaf=2, class_weight="balanced", random_state=42, n_jobs=-1)),
    ])
    features = CATEGORICAL + NUMERICAL
    model.fit(train_df[features], train_df["High_Performance"])
    predictions = model.predict(test_df[features])
    probabilities = model.predict_proba(test_df[features])[:, 1]
    y_test = test_df["High_Performance"]
    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probabilities),
    }
    names = model.named_steps["preprocessor"].get_feature_names_out()
    importance = pd.DataFrame({"Feature": names, "Importance": model.named_steps["classifier"].feature_importances_}).sort_values("Importance", ascending=False)
    return model, metrics, importance


def export_outputs(df: pd.DataFrame, model, metrics: dict, importance: pd.DataFrame, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    features = CATEGORICAL + NUMERICAL
    result = df.copy()
    result["Predicted_High_Performance"] = model.predict(result[features])
    result["High_Performance_Probability"] = model.predict_proba(result[features])[:, 1]
    result["Performance_Segment"] = pd.cut(result["High_Performance_Probability"], [0, .35, .65, 1], labels=["Low Intent", "Medium Intent", "High Intent"], include_lowest=True)
    result.to_csv(output / "instagram_predictions.csv", index=False)
    pd.DataFrame([metrics]).to_csv(output / "instagram_model_metrics.csv", index=False)
    importance.to_csv(output / "instagram_feature_importance.csv", index=False)
    analyses = {
        "media_type": result.groupby("media_type", as_index=False)["engagement_rate_calculated"].mean().sort_values("engagement_rate_calculated", ascending=False),
        "content_category": result.groupby("content_category", as_index=False)["engagement_rate_calculated"].mean().sort_values("engagement_rate_calculated", ascending=False),
        "traffic_source": result.groupby("traffic_source", as_index=False)["engagement_rate_calculated"].mean().sort_values("engagement_rate_calculated", ascending=False),
        "post_hour": result.groupby("post_hour", as_index=False)["engagement_rate_calculated"].mean().sort_values("engagement_rate_calculated", ascending=False),
    }
    for name, table in analyses.items():
        table.to_csv(output / f"instagram_analysis_{name}.csv", index=False)
    (output / "instagram_model_metrics.json").write_text(json.dumps({"rows": len(df), "high_performance_rate": float(df["High_Performance"].mean()), **metrics}, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()
    df = prepare(args.input)
    model, metrics, importance = train(df)
    export_outputs(df, model, metrics, importance, args.output)
    print(json.dumps({"rows": len(df), **metrics}, indent=2))


if __name__ == "__main__":
    main()
