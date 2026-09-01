"""Normalize the three project datasets into one comparable analytical table."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


CANONICAL = [
    "source_dataset", "post_id", "account_id", "platform", "account_type", "media_type",
    "topic", "campaign_phase", "sentiment_label", "emotion_type", "language",
    "posting_timestamp", "posting_hour", "posting_weekday", "audience_size",
    "denominator_type", "likes", "comments", "shares", "saves", "reach", "impressions",
    "total_engagement", "engagement_rate", "engagement_percentile", "performance_class",
    "text_content", "caption_length", "hashtags_count", "is_verified",
]


def _base(df: pd.DataFrame, source: str) -> pd.DataFrame:
    result = pd.DataFrame(index=df.index)
    result["source_dataset"] = source
    result["post_id"] = df.get("post_id", pd.Series(df.index, index=df.index)).astype(str)
    result["account_id"] = df.get("user_id", df.get("account_id", pd.Series(pd.NA, index=df.index))).astype("string")
    result["platform"] = df.get("platform", pd.Series(pd.NA, index=df.index)).astype("string")
    result["account_type"] = df.get("account_type", pd.Series(pd.NA, index=df.index)).astype("string")
    result["media_type"] = df.get("media_type", pd.Series(pd.NA, index=df.index)).astype("string")
    result["topic"] = df.get("topic", df.get("topic_category", pd.Series(pd.NA, index=df.index))).astype("string")
    result["campaign_phase"] = df.get("campaign_phase", pd.Series(pd.NA, index=df.index)).astype("string")
    result["sentiment_label"] = df.get("sentiment_label", pd.Series(pd.NA, index=df.index)).astype("string")
    result["emotion_type"] = df.get("emotion_type", pd.Series(pd.NA, index=df.index)).astype("string")
    result["language"] = df.get("language", pd.Series(pd.NA, index=df.index)).astype("string")
    result["posting_timestamp"] = pd.to_datetime(df.get("post_datetime", df.get("timestamp", df.get("post_date"))), errors="coerce")
    result["posting_hour"] = result["posting_timestamp"].dt.hour
    result["posting_weekday"] = result["posting_timestamp"].dt.day_name()
    follower_values = df.get("follower_count", df.get("followers_count", pd.Series(pd.NA, index=df.index)))
    result["audience_size"] = pd.to_numeric(follower_values if ("follower_count" in df or "followers_count" in df) else df.get("impressions", pd.Series(pd.NA, index=df.index)), errors="coerce")
    result["denominator_type"] = "followers" if ("follower_count" in df or "followers_count" in df) else "impressions"
    for name in ["likes", "comments", "shares", "saves", "reach", "impressions"]:
        result[name] = pd.to_numeric(df.get(name, df.get(f"{name}_count", pd.Series(0, index=df.index))), errors="coerce").fillna(0)
    result["total_engagement"] = result[["likes", "comments", "shares", "saves"]].sum(axis=1)
    result["engagement_rate"] = result["total_engagement"] / result["audience_size"] * 100
    result["text_content"] = df.get("post_content", df.get("text_content", pd.Series("", index=df.index))).fillna("").astype(str)
    result["caption_length"] = pd.to_numeric(df.get("caption_length", pd.Series(pd.NA, index=df.index)), errors="coerce").fillna(result["text_content"].str.len())
    result["hashtags_count"] = pd.to_numeric(df.get("hashtags_count", pd.Series(pd.NA, index=df.index)), errors="coerce").fillna(df.get("hashtags", pd.Series("", index=df.index)).fillna("").astype(str).str.count("#"))
    result["is_verified"] = df.get("is_verified", pd.Series(pd.NA, index=df.index))
    return result


def unify(original: Path, social_2025: Path, instagram: Path) -> pd.DataFrame:
    tables = [
        _base(pd.read_csv(original), "social_engagement_12000"),
        _base(pd.read_csv(social_2025), "social_engagement_2025_20000"),
        _base(pd.read_csv(instagram), "instagram_analytics_29999"),
    ]
    derived = ["engagement_percentile", "performance_class"]
    unified = pd.concat(tables, ignore_index=True)[[column for column in CANONICAL if column not in derived]]
    unified = unified.dropna(subset=["posting_timestamp", "audience_size"])
    unified = unified[unified["audience_size"] > 0].copy()
    unified["engagement_percentile"] = unified.groupby("source_dataset")["engagement_rate"].rank(pct=True, method="average")
    unified["performance_class"] = pd.cut(
        unified["engagement_percentile"], bins=[0, .5, .75, 1], labels=["Low", "Medium", "High"], include_lowest=True
    ).astype("string")
    unified = unified[CANONICAL]
    return unified


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--social-2025", type=Path, required=True)
    parser.add_argument("--instagram", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("output/unified_social_media.csv"))
    args = parser.parse_args()
    unified = unify(args.original, args.social_2025, args.instagram)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    unified.to_csv(args.output, index=False)
    print(unified.groupby(["source_dataset", "performance_class"], observed=True).size().to_string())
    print(f"rows={len(unified)} columns={len(unified.columns)} output={args.output}")


if __name__ == "__main__":
    main()
