"""Local PostPilot AI dashboard for YouTube predictions and hashtags."""

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"

st.set_page_config(page_title="PostPilot AI", page_icon="▶", layout="wide")


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    predictions = pd.read_csv(OUTPUT / "youtube_predictions.csv")
    hashtags = pd.read_csv(OUTPUT / "youtube_hashtags.csv")
    metrics = pd.read_csv(OUTPUT / "youtube_model_metrics.csv")
    return predictions, hashtags, metrics


st.title("PostPilot AI")
st.caption("YouTube performance prediction and pre-publication hashtag recommendations")

required = [OUTPUT / "youtube_predictions.csv", OUTPUT / "youtube_hashtags.csv", OUTPUT / "youtube_model_metrics.csv"]
missing = [str(path) for path in required if not path.exists()]
if missing:
    st.error("Dashboard data is missing. Run RUN_PROJECT.ps1 first.")
    st.code("powershell -ExecutionPolicy Bypass -File .\\RUN_PROJECT.ps1", language="powershell")
    st.stop()

predictions, hashtags, metrics = load_data()
merged = predictions.merge(hashtags, on="post_id", how="left")

with st.sidebar:
    st.header("Filters")
    categories = sorted(merged["content_category"].dropna().unique())
    selected_categories = st.multiselect("Content category", categories, default=categories)
    sources = sorted(merged["traffic_source"].dropna().unique())
    selected_sources = st.multiselect("Traffic source", sources, default=sources)
    segments = sorted(merged["Performance_Segment"].dropna().unique())
    selected_segments = st.multiselect("Performance segment", segments, default=segments)
    min_probability = st.slider("Minimum prediction probability", 0.0, 1.0, 0.0, 0.01)

filtered = merged[
    merged["content_category"].isin(selected_categories)
    & merged["traffic_source"].isin(selected_sources)
    & merged["Performance_Segment"].isin(selected_segments)
    & (merged["High_Performance_Probability"] >= min_probability)
].copy()

if filtered.empty:
    st.warning("No videos match the selected filters.")
    st.stop()

metric_row = metrics.iloc[0]
overview, predictions_tab, hashtags_tab = st.tabs(["Overview", "Predictions", "Hashtags"])

with overview:
    st.subheader("Channel overview")
    cards = st.columns(5)
    cards[0].metric("Videos", f"{len(filtered):,}")
    cards[1].metric("Avg watch time", f"{filtered['total_watch_time_hours'].mean():,.0f} h")
    cards[2].metric("Avg CTR", f"{filtered['ctr_percentage'].mean():.2f}%")
    cards[3].metric("Impressions", f"{filtered['impressions'].sum():,.0f}")
    cards[4].metric("Subscribers gained", f"{filtered['subscribers_gained'].sum():,.0f}")

    left, right = st.columns(2)
    with left:
        st.write("### Average watch time by category")
        category_chart = filtered.groupby("content_category")["total_watch_time_hours"].mean().sort_values(ascending=False)
        st.bar_chart(category_chart)
    with right:
        st.write("### Average CTR by traffic source")
        source_chart = filtered.groupby("traffic_source")["ctr_percentage"].mean().sort_values(ascending=False)
        st.bar_chart(source_chart)

    st.write("### Upload volume by hour")
    hourly = filtered.groupby("upload_hour").size().reindex(range(24), fill_value=0)
    st.line_chart(hourly)

with predictions_tab:
    st.subheader("Prediction performance")
    cards = st.columns(5)
    cards[0].metric("Predicted high videos", f"{int(filtered['Predicted_High_Performance'].sum()):,}")
    cards[1].metric("Avg probability", f"{filtered['High_Performance_Probability'].mean():.1%}")
    cards[2].metric("Test accuracy", f"{metric_row['accuracy']:.2%}")
    cards[3].metric("Test F1", f"{metric_row['f1']:.2%}")
    cards[4].metric("Test ROC-AUC", f"{metric_row['roc_auc']:.2%}")

    left, right = st.columns(2)
    with left:
        st.write("### Predicted high-performance videos by category")
        high_by_category = filtered.groupby("content_category")["Predicted_High_Performance"].sum().sort_values(ascending=False)
        st.bar_chart(high_by_category)
    with right:
        st.write("### Prediction segment distribution")
        segment_counts = filtered["Performance_Segment"].value_counts()
        st.bar_chart(segment_counts)

    st.write("### Highest-probability videos")
    prediction_columns = ["post_id", "content_category", "traffic_source", "video_duration_min", "High_Performance_Probability", "Predicted_High_Performance"]
    st.dataframe(filtered[prediction_columns].sort_values("High_Performance_Probability", ascending=False).head(100), use_container_width=True, hide_index=True)

with hashtags_tab:
    st.subheader("Hashtag recommendations")
    cards = st.columns(3)
    cards[0].metric("Videos shown", f"{len(filtered):,}")
    cards[1].metric("Avg hashtag relevance", f"{filtered['hashtag_relevance_score'].mean():.3f}")
    cards[2].metric("Avg hashtags/video", f"{filtered['hashtag_count'].mean():.1f}")

    st.info("These are relevance suggestions, not a guarantee of virality. The current dataset uses category/traffic-source fallback metadata because it has no titles or transcripts.")
    hashtag_columns = ["post_id", "content_category", "traffic_source", "recommended_hashtags", "hashtag_relevance_score", "hashtag_generation_source"]
    st.dataframe(filtered[hashtag_columns].sort_values("hashtag_relevance_score", ascending=False), use_container_width=True, hide_index=True)

st.divider()
st.caption("PostPilot AI • Generated from the local Python pipeline • Static academic dataset")
