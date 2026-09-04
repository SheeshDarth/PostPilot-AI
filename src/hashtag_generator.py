"""Generate ranked, pre-publication YouTube hashtags for PostPilot AI."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


TEXT_COLUMNS = ["title", "video_title", "description", "transcript", "tags", "keywords"]
STOP_WORDS = {
    "about", "after", "also", "and", "are", "because", "been", "before", "being", "but",
    "can", "could", "from", "have", "into", "just", "more", "most", "our", "that", "the",
    "their", "then", "there", "these", "this", "through", "using", "very", "what", "when",
    "where", "which", "with", "would", "your",
}


def slug(value: object) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "", str(value))
    return text[:40]


def build_text(row: pd.Series) -> tuple[str, str]:
    present = [str(row[column]) for column in TEXT_COLUMNS if column in row and pd.notna(row[column]) and str(row[column]).strip()]
    if present:
        return " ".join(present), "text metadata"
    fallback = " ".join(str(row.get(column, "")) for column in ["content_category", "traffic_source"])
    return fallback, "category metadata fallback"


def generate(df: pd.DataFrame, top_k: int = 8) -> pd.DataFrame:
    texts_and_sources = [build_text(row) for _, row in df.iterrows()]
    texts = [item[0] for item in texts_and_sources]
    source = [item[1] for item in texts_and_sources]
    vectorizer = TfidfVectorizer(
        lowercase=True,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9]{2,}\b",
        stop_words=list(STOP_WORDS),
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(texts)
    terms = vectorizer.get_feature_names_out()
    rows = []
    for row_index, (_, row) in enumerate(df.iterrows()):
        scores = matrix[row_index].toarray().ravel()
        candidates = [(terms[index], float(score)) for index, score in enumerate(scores) if score > 0]
        candidates.sort(key=lambda item: (-item[1], item[0]))
        hashtags = []
        seen = set()
        for term, score in candidates:
            tag = "#" + "".join(slug(part).capitalize() for part in term.split())
            if len(tag) < 4 or tag.lower() in seen:
                continue
            seen.add(tag.lower())
            hashtags.append((tag, score))
            if len(hashtags) == top_k:
                break
        category_tag = "#" + slug(row.get("content_category", "YouTube")).capitalize()
        if category_tag.lower() not in seen:
            hashtags.insert(0, (category_tag, 1.0))
        traffic_tag = "#" + slug(row.get("traffic_source", "Video")).capitalize()
        if traffic_tag.lower() not in {tag.lower() for tag, _ in hashtags}:
            hashtags.append((traffic_tag, 0.7))
        hashtags = hashtags[:top_k]
        output = {
            "post_id": row.get("post_id"),
            "recommended_hashtags": " ".join(tag for tag, _ in hashtags),
            "hashtag_relevance_score": round(sum(score for _, score in hashtags) / len(hashtags), 4),
            "hashtag_generation_source": source[row_index],
            "hashtag_count": len(hashtags),
        }
        for index, (tag, score) in enumerate(hashtags, start=1):
            output[f"hashtag_{index}"] = tag
            output[f"hashtag_{index}_score"] = round(score, 4)
        rows.append(output)
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("output/youtube_hashtags.csv"))
    parser.add_argument("--top-k", type=int, default=8)
    args = parser.parse_args()
    df = pd.read_csv(args.input).drop_duplicates(subset=["post_id"])
    result = generate(df, top_k=max(3, min(args.top_k, 15)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Generated hashtags for {len(result):,} videos: {args.output}")


if __name__ == "__main__":
    main()
