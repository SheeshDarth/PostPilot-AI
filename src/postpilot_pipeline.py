"""Train the PostPilot AI leakage-safe engagement classifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer


ENGAGEMENT_COLUMNS = ["Likes Count", "Comments Count", "Shares Count"]
CATEGORICAL_FEATURES = [
    "Platform",
    "Topic Category",
    "Campaign Phase",
    "Sentiment Label",
    "Emotion Type",
    "Posting_Weekday",
    "Posting_Month",
    "Brand Name",
    "Product Name",
    "Campaign Name",
    "Language",
]
NUMERICAL_FEATURES = [
    "Posting_Hour",
    "Sentiment Score",
    "Toxicity Score",
    "User Past Sentiment Avg",
    "Text Length",
    "Hashtag Count",
    "Mention Count",
]
TEXT_FEATURE = "Text Content"
REQUIRED_COLUMNS = {
    "Timestamp",
    "Platform",
    "Topic Category",
    "Campaign Phase",
    "Sentiment Label",
    "Emotion Type",
    "Sentiment Score",
    "Impressions",
    *ENGAGEMENT_COLUMNS,
}


def load_and_prepare(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path).drop_duplicates().copy()
    aliases = {
        "post_id": "Post ID", "timestamp": "Timestamp", "platform": "Platform",
        "topic_category": "Topic Category", "sentiment_score": "Sentiment Score",
        "sentiment_label": "Sentiment Label", "emotion_type": "Emotion Type",
        "toxicity_score": "Toxicity Score", "likes_count": "Likes Count",
        "shares_count": "Shares Count", "comments_count": "Comments Count",
        "impressions": "Impressions", "brand_name": "Brand Name",
        "product_name": "Product Name", "campaign_name": "Campaign Name",
        "campaign_phase": "Campaign Phase", "language": "Language",
        "text_content": "Text Content", "hashtags": "Hashtags", "mentions": "Mentions",
        "user_past_sentiment_avg": "User Past Sentiment Avg",
    }
    df = df.rename(columns={column: aliases[column] for column in df.columns if column in aliases})
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df["Impressions"] = pd.to_numeric(df["Impressions"], errors="coerce")
    df = df.dropna(subset=["Timestamp", "Impressions"])
    df = df[df["Impressions"] > 0].copy()

    for column in ENGAGEMENT_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).clip(lower=0)
    df["Sentiment Score"] = pd.to_numeric(df["Sentiment Score"], errors="coerce")
    df["Sentiment Score"] = df["Sentiment Score"].fillna(df["Sentiment Score"].median())
    for column in ["Toxicity Score", "User Past Sentiment Avg"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["Posting_Hour"] = df["Timestamp"].dt.hour
    df["Posting_Weekday"] = df["Timestamp"].dt.day_name()
    df["Posting_Month"] = df["Timestamp"].dt.month_name()
    df["Text Content"] = df["Text Content"].fillna("").astype(str)
    df["Hashtags"] = df["Hashtags"].fillna("").astype(str)
    df["Mentions"] = df["Mentions"].fillna("").astype(str)
    df["Text Length"] = df["Text Content"].str.len()
    df["Hashtag Count"] = df["Hashtags"].fillna("").astype(str).str.count("#")
    df["Mention Count"] = df["Mentions"].fillna("").astype(str).str.count("@")
    df["Total_Engagement"] = df[ENGAGEMENT_COLUMNS].sum(axis=1)
    df["Engagement_Rate"] = df["Total_Engagement"] / df["Impressions"] * 100
    threshold = df["Engagement_Rate"].quantile(0.75)
    df["High_Performance"] = (df["Engagement_Rate"] >= threshold).astype(int)
    if df["High_Performance"].nunique() < 2:
        raise ValueError("The dataset does not produce both target classes.")
    return df


def train(df: pd.DataFrame, split: str = "time"):
    features = CATEGORICAL_FEATURES + NUMERICAL_FEATURES + [TEXT_FEATURE]
    if split == "time":
        ordered = df.sort_values("Timestamp")
        cut = int(len(ordered) * 0.80)
        X_train, X_test = ordered.iloc[:cut][features], ordered.iloc[cut:][features]
        y_train, y_test = ordered.iloc[:cut]["High_Performance"], ordered.iloc[cut:]["High_Performance"]
    elif split == "random":
        X, y = df[features], df["High_Performance"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y
        )
    else:
        raise ValueError("split must be 'time' or 'random'")
    categorical = Pipeline(
        [("imputer", SimpleImputer(strategy="most_frequent")),
         ("encoder", OneHotEncoder(handle_unknown="ignore"))]
    )
    numerical = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    preprocessor = ColumnTransformer(
        [("categorical", categorical, CATEGORICAL_FEATURES),
         ("numerical", numerical, NUMERICAL_FEATURES),
         ("text", TfidfVectorizer(
             lowercase=True, strip_accents="unicode", ngram_range=(1, 2),
             min_df=2, max_features=5000, sublinear_tf=True
         ), TEXT_FEATURE)]
    )
    model = Pipeline(
        [("preprocessor", preprocessor),
         ("classifier", RandomForestClassifier(
             n_estimators=300, max_depth=12, class_weight="balanced",
             random_state=42, n_jobs=-1
         ))]
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probabilities),
    }
    names = model.named_steps["preprocessor"].get_feature_names_out()
    importances = model.named_steps["classifier"].feature_importances_
    importance = pd.DataFrame({"Feature": names, "Importance": importances})
    importance = importance.sort_values("Importance", ascending=False)
    return model, metrics, importance


def add_predictions(df: pd.DataFrame, model) -> pd.DataFrame:
    features = CATEGORICAL_FEATURES + NUMERICAL_FEATURES + [TEXT_FEATURE]
    result = df.copy()
    result["Predicted_High_Performance"] = model.predict(result[features])
    result["High_Performance_Probability"] = model.predict_proba(result[features])[:, 1]
    result["Performance_Segment"] = pd.cut(
        result["High_Performance_Probability"],
        bins=[0, 0.35, 0.65, 1],
        labels=["Low Intent", "Medium Intent", "High Intent"],
        include_lowest=True,
    )
    return result


def predict_post(post_data: dict[str, object], model) -> dict[str, object]:
    """Predict one planned post using pre-publication attributes only."""
    sample = pd.DataFrame([post_data])
    probability = float(model.predict_proba(sample)[0, 1])
    return {
        "Prediction": "High Performance" if probability >= 0.50 else "Normal Performance",
        "Probability": round(probability * 100, 2),
    }


def strategy_summary(df: pd.DataFrame) -> dict[str, object]:
    choices = {
        "best_platform": "Platform",
        "best_topic": "Topic Category",
        "best_weekday": "Posting_Weekday",
        "best_hour": "Posting_Hour",
        "best_sentiment": "Sentiment Label",
        "best_emotion": "Emotion Type",
    }
    return {key: df.groupby(column)["Engagement_Rate"].mean().idxmax() for key, column in choices.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("output"))
    parser.add_argument("--split", choices=["time", "random"], default="time")
    args = parser.parse_args()
    if not args.input.exists():
        raise FileNotFoundError(f"Input dataset not found: {args.input}")
    args.output.mkdir(parents=True, exist_ok=True)

    df = load_and_prepare(args.input)
    model, metrics, importance = train(df, split=args.split)
    predictions = add_predictions(df, model)
    predictions.to_csv(args.output / "postpilot_predictions.csv", index=False)
    pd.DataFrame([metrics]).to_csv(args.output / "model_metrics.csv", index=False)
    importance.to_csv(args.output / "feature_importance.csv", index=False)
    (args.output / "strategy_summary.json").write_text(
        json.dumps(strategy_summary(df), indent=2, default=lambda value: value.item() if isinstance(value, np.generic) else value),
        encoding="utf-8",
    )
    print(json.dumps({"rows": len(df), "target_rate": float(df["High_Performance"].mean()), **metrics}, indent=2))


if __name__ == "__main__":
    main()
