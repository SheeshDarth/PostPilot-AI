"""Local PostPilot AI dashboard for YouTube predictions and hashtags."""

from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"

st.set_page_config(page_title="PostPilot AI", page_icon="▶", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(135deg, #08111f 0%, #10243d 52%, #123c4c 100%); }
    [data-testid="stHeader"] { background: rgba(8, 17, 31, 0.85); }
    [data-testid="stMetric"] { background: linear-gradient(135deg, #183653, #155667); border: 1px solid #2bd5d8; border-radius: 12px; padding: 12px; box-shadow: 0 6px 18px rgba(0,0,0,.25); }
    [data-testid="stMetricLabel"] { color: #bfe8ee; }
    [data-testid="stMetricValue"] { color: #ffffff; }
    h1, h2, h3 { color: #f7fbff; }
    .comparison-note { background: #183653; border-left: 5px solid #2bd5d8; border-radius: 8px; padding: 12px 16px; color: #eafcff; }
    </style>
    """,
    unsafe_allow_html=True,
)


def data_signature(required_files: list[Path]) -> tuple[int, ...]:
    """Return a cache key that changes whenever pipeline outputs change."""
    return tuple(path.stat().st_mtime_ns for path in required_files)


@st.cache_data
def load_data(signature: tuple[int, ...]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the latest pipeline outputs; signature makes the cache refresh-aware."""
    predictions = pd.read_csv(OUTPUT / "youtube_predictions.csv")
    hashtags = pd.read_csv(OUTPUT / "youtube_hashtags.csv")
    metrics = pd.read_csv(OUTPUT / "youtube_model_metrics.csv")
    feature_importance = pd.read_csv(OUTPUT / "youtube_feature_importance.csv")
    return predictions, hashtags, metrics, feature_importance


st.title("PostPilot AI")
st.caption("YouTube performance prediction and pre-publication hashtag recommendations")

required = [
    OUTPUT / "youtube_predictions.csv",
    OUTPUT / "youtube_hashtags.csv",
    OUTPUT / "youtube_model_metrics.csv",
    OUTPUT / "youtube_feature_importance.csv",
]
missing = [str(path) for path in required if not path.exists()]
if missing:
    st.error("Dashboard data is missing. Run RUN_PROJECT.ps1 first.")
    st.code("powershell -ExecutionPolicy Bypass -File .\\RUN_PROJECT.ps1", language="powershell")
    st.stop()

signature = data_signature(required)

with st.sidebar:
    st.header("Filters")
    if st.button("Refresh latest pipeline data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    latest_update = max(path.stat().st_mtime for path in required)
    st.caption(f"Data refreshed: {datetime.fromtimestamp(latest_update):%d %b %Y, %H:%M:%S}")

predictions, hashtags, metrics, feature_importance = load_data(signature)
merged = predictions.merge(hashtags, on="post_id", how="left")

with st.sidebar:
    categories = sorted(merged["content_category"].dropna().unique())
    sources = sorted(merged["traffic_source"].dropna().unique())
    segments = sorted(merged["Performance_Segment"].dropna().unique())
    if st.button("Reset all filters", use_container_width=True):
        st.session_state["category_filter"] = categories
        st.session_state["source_filter"] = sources
        st.session_state["segment_filter"] = segments
        st.session_state["probability_filter"] = 0.0
        st.rerun()

    selected_categories = st.multiselect("Content category", categories, default=categories, key="category_filter")
    selected_sources = st.multiselect("Traffic source", sources, default=sources, key="source_filter")
    selected_segments = st.multiselect("Performance segment", segments, default=segments, key="segment_filter")
    min_probability = st.slider("Minimum prediction probability", 0.0, 1.0, 0.0, 0.01, key="probability_filter")

filtered = merged[
    merged["content_category"].isin(selected_categories)
    & merged["traffic_source"].isin(selected_sources)
    & merged["Performance_Segment"].isin(selected_segments)
    & (merged["High_Performance_Probability"] >= min_probability)
].copy()

if filtered.empty:
    st.warning("No videos match the selected filters.")
    st.stop()

st.info(f"Showing {len(filtered):,} of {len(merged):,} videos after filters. Change a filter or refresh the pipeline outputs to update every visual.")

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
        st.caption("Compares the typical total watch time for each content category.")
        category_chart = filtered.groupby("content_category")["total_watch_time_hours"].mean().sort_values(ascending=False)
        st.bar_chart(category_chart, color="#27d3d8")
    with right:
        st.write("### Average CTR by traffic source")
        st.caption("Shows which discovery sources are associated with stronger click-through rates.")
        source_chart = filtered.groupby("traffic_source")["ctr_percentage"].mean().sort_values(ascending=False)
        st.bar_chart(source_chart, color="#ffbf69")

    st.write("### Upload volume by weekday")
    unique_hours = filtered["upload_hour"].nunique(dropna=True)
    if unique_hours <= 1:
        st.caption("The source contains one upload hour only, so weekday coverage is the more informative timing comparison.")
    else:
        st.caption("Counts videos by weekday; use this to compare the dataset's timing coverage without overstating causality.")
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_volume = filtered.groupby("upload_weekday").size().reindex(weekday_order, fill_value=0)
    st.bar_chart(weekday_volume.rename("Videos"), color="#7c9cff")

    left, right = st.columns(2)
    with left:
        st.write("### Average watch time by weekday")
        st.caption("Compares typical watch time across Monday–Sunday.")
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_chart = filtered.groupby("upload_weekday")["total_watch_time_hours"].mean().reindex(weekday_order).dropna()
        st.bar_chart(weekday_chart, color="#b78cff", height=280)
    with right:
        st.write("### High-performance rate by traffic source")
        st.caption("Shows the percentage of filtered videos predicted as high performance for each source.")
        source_rate = filtered.groupby("traffic_source")["Predicted_High_Performance"].mean().sort_values(ascending=False).mul(100)
        st.bar_chart(source_rate.rename("Predicted high rate (%)"), color="#39e39b", height=280)

    st.write("### Video duration versus total watch time")
    st.caption("Each point is a video; color is category and point size represents impressions.")
    scatter_columns = ["video_duration_min", "total_watch_time_hours", "content_category", "impressions"]
    st.scatter_chart(
        filtered[scatter_columns].rename(columns={"video_duration_min": "Video duration (min)", "total_watch_time_hours": "Total watch time (hours)"}),
        x="Video duration (min)",
        y="Total watch time (hours)",
        color="content_category",
        size="impressions",
        height=360,
    )

    st.write("### Compare content categories")
    category_compare = filtered.groupby("content_category").agg(
        Videos=("post_id", "count"),
        Avg_Watch_Hours=("total_watch_time_hours", "mean"),
        Avg_CTR=("ctr_percentage", "mean"),
        Avg_Probability=("High_Performance_Probability", "mean"),
    ).sort_values("Avg_Probability", ascending=False)
    st.dataframe(
        category_compare.style.background_gradient(cmap="YlGnBu", subset=["Avg_Watch_Hours", "Avg_CTR", "Avg_Probability"])
        .format({"Avg_Watch_Hours": "{:,.0f}", "Avg_CTR": "{:.2f}%", "Avg_Probability": "{:.1%}"}),
        use_container_width=True,
    )

    st.write("### Dynamic category comparison")
    comparison_options = {
        "Average watch time (hours)": "total_watch_time_hours",
        "Average CTR (%)": "ctr_percentage",
        "Average prediction probability": "High_Performance_Probability",
        "Predicted high-performance videos": "Predicted_High_Performance",
    }
    selected_metric_label = st.selectbox("Metric to compare", list(comparison_options), key="overview_compare_metric")
    selected_metric = comparison_options[selected_metric_label]
    dynamic_comparison = (
        filtered.groupby("content_category")[selected_metric]
        .mean()
        .sort_values(ascending=False)
        .rename(selected_metric_label)
    )
    st.bar_chart(dynamic_comparison, color="#7c9cff", height=280)

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
        st.caption("Counts the videos classified as high performance in each category.")
        high_by_category = filtered.groupby("content_category")["Predicted_High_Performance"].sum().sort_values(ascending=False)
        st.bar_chart(high_by_category, color="#39e39b")
    with right:
        st.write("### Prediction segment distribution")
        st.caption("Groups videos into low-, medium-, and high-intent probability bands.")
        segment_counts = filtered["Performance_Segment"].value_counts()
        st.bar_chart(segment_counts, color="#ff7a9e")

    st.write("### Actual versus predicted high-performance videos by category")
    st.caption("Compares the historical top-quartile label with the model's high-performance flag; the gap shows classification error.")
    actual_predicted = (
        filtered.groupby("content_category")[["High_Performance", "Predicted_High_Performance"]]
        .sum()
        .rename(columns={
            "High_Performance": "Actual high videos",
            "Predicted_High_Performance": "Predicted high videos",
        })
        .sort_values("Actual high videos", ascending=False)
    )
    st.bar_chart(actual_predicted, color=["#f7b955", "#18c5c9"], height=320)

    left, right = st.columns(2)
    with left:
        st.write("### Average prediction probability by traffic source")
        st.caption("Compares model confidence across discovery sources.")
        source_probability = filtered.groupby("traffic_source")["High_Performance_Probability"].mean().sort_values(ascending=False).mul(100)
        st.bar_chart(source_probability.rename("Average probability (%)"), color="#7c9cff", height=280)
    with right:
        st.write("### Prediction probability distribution")
        st.caption("Shows how many videos fall into each probability range.")
        probability_bins = pd.cut(
            filtered["High_Performance_Probability"],
            bins=[0, .2, .4, .6, .8, 1.0],
            labels=["0–20%", "20–40%", "40–60%", "60–80%", "80–100%"],
            include_lowest=True,
        ).value_counts().reindex(["0–20%", "20–40%", "40–60%", "60–80%", "80–100%"], fill_value=0)
        st.bar_chart(probability_bins.rename("Videos"), color="#ffbf69", height=280)

    st.write("### What drives the model? Top feature importance")
    st.caption("Higher importance means the Random Forest used that feature more often when splitting the training data; it is not causal evidence.")
    top_features = feature_importance.head(12).copy()
    top_features["Feature"] = top_features["Feature"].str.replace(r"^(categorical|numerical)__", "", regex=True).str.replace("_", " ")
    st.bar_chart(top_features.set_index("Feature")["Importance"].sort_values(), color="#2bd5d8", height=360)

    st.markdown(
        '<div class="comparison-note"><b>How to read this page:</b> use the probability cards for overall confidence, then compare categories and traffic sources to identify where high-performance videos are most likely.</div>',
        unsafe_allow_html=True,
    )

    st.write("### Highest-probability videos")
    prediction_columns = ["post_id", "content_category", "traffic_source", "video_duration_min", "High_Performance_Probability", "Predicted_High_Performance"]
    st.dataframe(filtered[prediction_columns].sort_values("High_Performance_Probability", ascending=False).head(100), use_container_width=True, hide_index=True)
    st.download_button(
        "Download filtered predictions CSV",
        filtered[prediction_columns].to_csv(index=False).encode("utf-8"),
        file_name="postpilot_filtered_predictions.csv",
        mime="text/csv",
        use_container_width=True,
    )

with hashtags_tab:
    st.subheader("Hashtag recommendations")
    cards = st.columns(3)
    cards[0].metric("Videos shown", f"{len(filtered):,}")
    cards[1].metric("Avg hashtag relevance", f"{filtered['hashtag_relevance_score'].mean():.3f}")
    cards[2].metric("Avg hashtags/video", f"{filtered['hashtag_count'].mean():.1f}")

    st.info("These are relevance suggestions, not a guarantee of virality. The current dataset uses category/traffic-source fallback metadata because it has no titles or transcripts.")
    left, right = st.columns(2)
    with left:
        st.write("### Average hashtag relevance by source")
        st.caption("Compares the average relevance score produced by each hashtag-generation method.")
        source_relevance = filtered.groupby("hashtag_generation_source")["hashtag_relevance_score"].mean().sort_values(ascending=False)
        st.bar_chart(source_relevance, color="#39e39b", height=280)
    with right:
        st.write("### Average hashtags per video by category")
        st.caption("Shows how many recommendations are returned for each category on average.")
        category_hashtags = filtered.groupby("content_category")["hashtag_count"].mean().sort_values(ascending=False)
        st.bar_chart(category_hashtags, color="#ff7a9e", height=280)
    hashtag_columns = ["post_id", "content_category", "traffic_source", "recommended_hashtags", "hashtag_relevance_score", "hashtag_generation_source"]
    st.dataframe(
        filtered[hashtag_columns].sort_values("hashtag_relevance_score", ascending=False)
        .style.background_gradient(cmap="PuBuGn", subset=["hashtag_relevance_score"])
        .format({"hashtag_relevance_score": "{:.3f}"}),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download filtered hashtag recommendations CSV",
        filtered[hashtag_columns].to_csv(index=False).encode("utf-8"),
        file_name="postpilot_filtered_hashtags.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.divider()
st.caption("PostPilot AI • Generated from local pipeline outputs • Refresh-aware academic dataset")
