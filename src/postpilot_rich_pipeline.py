"""PostPilot experiment using the richer 20,000-row engagement dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


CATEGORICAL = ["user_gender", "topic", "is_verified", "has_media", "device", "language"]
NUMERICAL = [
    "user_age", "followers_count", "following_count", "content_length",
    "Posting_Hour", "Hashtag_Count", "Account_Age_Days",
    "Prior_User_Engagement_Rate", "Prior_User_Post_Count",
    "Prior_User_Topic_Rate", "Prior_Device_Topic_Rate",
]
TEXT = "post_content"
OUTCOMES = ["likes", "comments", "shares", "engagement_rate"]


def prepare(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path).drop_duplicates().copy()
    required = set(CATEGORICAL + NUMERICAL[:4] + ["account_creation_date", "post_date", TEXT, *OUTCOMES])
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    df["post_date"] = pd.to_datetime(df["post_date"], errors="coerce")
    df["account_creation_date"] = pd.to_datetime(df["account_creation_date"], errors="coerce")
    df = df.dropna(subset=["post_date", "followers_count", "likes", "comments", "shares"])
    df = df[df["followers_count"] > 0].copy()
    df[TEXT] = df[TEXT].fillna("").astype(str)
    for column in CATEGORICAL:
        df[column] = df[column].astype("string")
    df["Hashtag_Count"] = df["hashtags"].fillna("").astype(str).str.count("#")
    df["Posting_Hour"] = df["post_date"].dt.hour
    df["Account_Age_Days"] = (df["post_date"] - df["account_creation_date"]).dt.days.clip(lower=0)
    df["Engagement_Rate"] = (df["likes"] + df["comments"] + df["shares"]) / df["followers_count"] * 100
    ordered = df.sort_values("post_date").copy()
    ordered["Prior_User_Engagement_Rate"] = ordered.groupby("user_id")["Engagement_Rate"].transform(
        lambda values: values.shift().expanding().mean()
    )
    ordered["Prior_User_Post_Count"] = ordered.groupby("user_id").cumcount()
    ordered["Prior_User_Topic_Rate"] = ordered.groupby(["user_id", "topic"])["Engagement_Rate"].transform(
        lambda values: values.shift().expanding().mean()
    )
    ordered["Prior_Device_Topic_Rate"] = ordered.groupby(["device", "topic"])["Engagement_Rate"].transform(
        lambda values: values.shift().expanding().mean()
    )
    df = ordered.sort_index()
    df["Prior_User_Engagement_Rate"] = df["Prior_User_Engagement_Rate"].fillna(df["Engagement_Rate"].median())
    for column in ["Prior_User_Topic_Rate", "Prior_Device_Topic_Rate"]:
        df[column] = df[column].fillna(df["Engagement_Rate"].median())
    threshold = df["Engagement_Rate"].quantile(0.75)
    df["High_Performance"] = (df["Engagement_Rate"] >= threshold).astype(int)
    return df


def train(df: pd.DataFrame):
    features = CATEGORICAL + NUMERICAL + [TEXT]
    ordered = df.sort_values("post_date")
    cut = int(len(ordered) * 0.8)
    train_df, test_df = ordered.iloc[:cut], ordered.iloc[cut:]
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])
    numerical = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    preprocessor = ColumnTransformer([
        ("categorical", categorical, CATEGORICAL),
        ("numerical", numerical, NUMERICAL),
        ("text", TfidfVectorizer(lowercase=True, strip_accents="unicode", ngram_range=(1, 2), min_df=2, max_features=8000, sublinear_tf=True), TEXT),
    ])
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=400, max_depth=16, min_samples_leaf=2, class_weight="balanced", random_state=42, n_jobs=-1)),
    ])
    model.fit(train_df[features], train_df["High_Performance"])
    pred = model.predict(test_df[features])
    probability = model.predict_proba(test_df[features])[:, 1]
    metrics = {
        "accuracy": accuracy_score(test_df["High_Performance"], pred),
        "precision": precision_score(test_df["High_Performance"], pred, zero_division=0),
        "recall": recall_score(test_df["High_Performance"], pred, zero_division=0),
        "f1": f1_score(test_df["High_Performance"], pred, zero_division=0),
        "roc_auc": roc_auc_score(test_df["High_Performance"], probability),
    }
    return model, metrics, features


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    df = prepare(args.input)
    _, metrics, _ = train(df)
    print({"rows": len(df), "positive_rate": float(df["High_Performance"].mean()), **metrics})


if __name__ == "__main__":
    main()
