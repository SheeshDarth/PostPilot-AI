# PostPilot AI — Chart and Visual Guide

Use this guide when presenting the dashboards. Every visual should answer a specific question.

The Power BI page `Complete Analysis Dashboard` is the main presentation page. It combines the KPI cards, category and traffic-source comparisons, upload timing, prediction segments, probability comparisons, duration/watch-time relationship, and category decision table in one view.

| Visual | Question it answers | How to read it |
|---|---|---|
| Watch time by category | Which content categories generate more watch time? | Higher bars indicate higher average total watch time. |
| CTR by traffic source | Where do viewers click more often? | Higher bars indicate stronger average CTR for that discovery source. |
| Upload volume by hour | When were the videos uploaded? | Peaks show the hours represented most often in the dataset. |
| Watch time by weekday | Which days are associated with stronger watch time? | Compare the weekday bars; this is association, not proof of causation. |
| High-performance rate by source | Which sources have more predicted high-performance videos? | The percentage is the share of filtered videos predicted as high performance. |
| Duration versus watch time | Does video length relate to watch time? | Each point is a video; color identifies category and size represents impressions. |
| Category comparison table | How do categories compare across several metrics? | Use Videos, watch time, CTR, probability, and predicted-high count together. |
| Predicted high videos by category | Which categories contain the most predicted high performers? | Higher bars mean more videos cross the model decision threshold. |
| Prediction segment distribution | How confident is the model overall? | Low, Medium, and High Intent show probability bands, not guaranteed outcomes. |
| Probability by traffic source | Where is model confidence higher? | Compare average predicted probability across sources. |
| Probability distribution | How concentrated are predictions? | The bars show whether predictions are mostly low, medium, or high probability. |
| Feature importance | Which input fields influence the Random Forest most? | Larger importance means greater model usage, not causal impact. |
| Hashtag relevance by source | Which hashtag method returns more relevant suggestions? | Higher scores indicate stronger lexical relevance in this dataset. |
| Hashtags per category | Which categories receive more suggestions? | Compare average recommendation counts by category. |

## Recommended presentation order

1. Start with KPIs to establish scale.
2. Compare categories and traffic sources.
3. Explain timing and duration patterns.
4. Show the predicted-high rate and probability distribution.
5. Explain feature importance and the leakage rule.
6. Finish with hashtag relevance and the recommendation table.

## Important interpretation rule

The charts describe patterns in the historical academic dataset. They do not prove that a category, source, duration, or hashtag causes performance. The model estimates the likelihood of belonging to the historical top-watch-time group.
