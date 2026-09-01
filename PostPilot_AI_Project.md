# PostPilot AI
## Predictive Social Media Analytics for Pre-Publish Content Performance

**Demo Deadline:** September 4, 2026  
**Primary Stack:** Python, Pandas, Scikit-learn, Matplotlib, Power BI  
**Primary Model:** Random Forest Classifier  
**Project Type:** Social Media Analytics + Predictive Modeling + BI Dashboard

---

# 1. Project Summary

**PostPilot AI** is a predictive social-media analytics project that analyzes historical post-performance data and estimates whether a future social-media post is likely to achieve high engagement.

Most social-media analytics dashboards are retrospective: they explain what already happened.

PostPilot AI adds a predictive layer by answering:

> **Before publishing a post, can we estimate whether it is likely to perform well based on its platform, topic, posting time, sentiment, emotion, and campaign context?**

The project combines:

1. Data cleaning and preprocessing
2. Exploratory Data Analysis (EDA)
3. Feature engineering
4. Machine-learning classification
5. Prediction probability generation
6. Power BI dashboarding
7. Simple posting-strategy recommendations

The goal is to create a polished, working end-to-end project that is easy to demonstrate and explain.

---

# 2. Problem Statement

Content creators, student builders, startups, and technical teams frequently publish content across multiple social-media platforms.

However, choosing what to post, where to post, when to post, and what tone to use is often based on guesswork.

Social-media analytics tools usually show post-performance data after publication. PostPilot AI attempts to make this process predictive by learning from historical engagement patterns and estimating whether a planned post is likely to become a high-performing post.

---

# 3. Main Research Question

> **Can pre-publish characteristics of a social-media post be used to predict whether the post will become a high-performing post?**

---

# 4. Project Objectives

1. Analyze historical social-media performance.
2. Identify the best-performing platforms, topics, weekdays, and posting hours.
3. Create a consistent engagement metric.
4. Build a high-performance target variable.
5. Train a Random Forest Classifier.
6. Prevent target leakage by excluding post-publication metrics from model inputs.
7. Generate prediction probabilities.
8. Create a two-page Power BI dashboard.
9. Generate simple posting-strategy recommendations.

---

# 5. Dataset

Use a public **Social Media Engagement Dataset** containing multiple platforms and post-performance attributes.

Recommended fields include:

- Timestamp
- Platform
- Topic Category
- Campaign Phase
- Brand Name
- Likes Count
- Comments Count
- Shares Count
- Impressions
- Sentiment Label
- Sentiment Score
- Emotion Type
- Location

The exact available fields may differ slightly depending on the dataset version.

---

# 6. Important ML Design Decision: Prevent Target Leakage

The following values are only known **after the post has been published**:

- Likes
- Comments
- Shares
- Impressions
- Engagement Rate

These fields must **not** be used as model inputs.

They are used only to calculate historical post performance and create the target variable.

The predictive model should use only information that is available before publishing:

- Platform
- Topic
- Campaign Phase
- Sentiment
- Emotion
- Posting Hour
- Posting Weekday
- Posting Month

This allows PostPilot AI to legitimately claim that it predicts content performance using pre-publish information.

---

# 7. Target Variable

## Total Engagement

```python
df["Total_Engagement"] = (
    df["Likes Count"]
    + df["Comments Count"]
    + df["Shares Count"]
)
```

## Engagement Rate

```python
df["Engagement_Rate"] = (
    df["Total_Engagement"] / df["Impressions"]
) * 100
```

## High-Performance Threshold

Use the 75th percentile:

```python
threshold = df["Engagement_Rate"].quantile(0.75)

df["High_Performance"] = (
    df["Engagement_Rate"] >= threshold
).astype(int)
```

Target meaning:

```text
0 = Normal Performance
1 = High Performance
```

---

# 8. Technology Stack

| Component | Technology |
|---|---|
| Programming | Python |
| Data Processing | Pandas |
| Numerical Processing | NumPy |
| Visualization | Matplotlib |
| Machine Learning | Scikit-learn |
| Model | Random Forest |
| Notebook | Jupyter Notebook |
| Dashboard | Power BI |
| Data Exchange | CSV |
| Report | Markdown / PDF |

---

# 9. Project Workflow

```text
Social Media Dataset
        |
        v
Data Cleaning
        |
        v
Feature Engineering
        |
        v
Exploratory Data Analysis
        |
        v
Engagement Rate Calculation
        |
        v
High-Performance Target
        |
        v
Train/Test Split
        |
        v
Categorical Encoding
        |
        v
Random Forest Classifier
        |
        v
Model Evaluation
        |
        v
Prediction Probability
        |
        v
Export CSV
        |
        v
Power BI Dashboard
        |
        v
Content Strategy Recommendations
```

---

# 10. Recommended Folder Structure

```text
PostPilot-AI/
|
|-- data/
|   |-- social_media_engagement.csv
|
|-- notebooks/
|   |-- PostPilot_AI.ipynb
|
|-- output/
|   |-- postpilot_predictions.csv
|   |-- model_metrics.csv
|   |-- feature_importance.csv
|
|-- dashboard/
|   |-- PostPilot_AI.pbix
|
|-- report/
|   |-- PostPilot_AI_Report.md
|   |-- PostPilot_AI_Report.pdf
|
|-- README.md
|-- requirements.txt
```

---

# 11. Python Implementation

## Import Libraries

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)
```

---

# 12. Load Dataset

```python
df = pd.read_csv("data/social_media_engagement.csv")

print(df.head())
print(df.shape)
print(df.info())
```

---

# 13. Data Quality Checks

```python
print(df.isnull().sum())
print("Duplicates:", df.duplicated().sum())
print(df.describe())
```

---

# 14. Data Cleaning

```python
df = df.drop_duplicates()

df["Timestamp"] = pd.to_datetime(
    df["Timestamp"],
    errors="coerce"
)

df = df.dropna(
    subset=["Timestamp", "Impressions"]
)

df = df[df["Impressions"] > 0]
```

Fill missing engagement values:

```python
for col in [
    "Likes Count",
    "Comments Count",
    "Shares Count"
]:
    df[col] = df[col].fillna(0)
```

---

# 15. Time-Based Feature Engineering

```python
df["Posting_Hour"] = df["Timestamp"].dt.hour

df["Posting_Weekday"] = (
    df["Timestamp"].dt.day_name()
)

df["Posting_Month"] = (
    df["Timestamp"].dt.month_name()
)
```

---

# 16. Exploratory Data Analysis

Keep the demo focused on a few meaningful questions.

## Platform Performance

```python
platform_analysis = (
    df.groupby("Platform")["Engagement_Rate"]
      .mean()
      .sort_values(ascending=False)
)

print(platform_analysis)
```

Question:

> Which platform receives the highest average engagement?

---

## Topic Performance

```python
topic_analysis = (
    df.groupby("Topic Category")["Engagement_Rate"]
      .mean()
      .sort_values(ascending=False)
)

print(topic_analysis)
```

Question:

> Which topics perform best?

---

## Best Posting Hour

```python
hour_analysis = (
    df.groupby("Posting_Hour")["Engagement_Rate"]
      .mean()
)

hour_analysis.plot(
    kind="line",
    marker="o"
)

plt.title("Engagement Rate by Posting Hour")
plt.xlabel("Posting Hour")
plt.ylabel("Average Engagement Rate")
plt.show()
```

---

## Best Weekday

```python
weekday_analysis = (
    df.groupby("Posting_Weekday")["Engagement_Rate"]
      .mean()
      .sort_values(ascending=False)
)

print(weekday_analysis)
```

---

## Sentiment vs Engagement

```python
sentiment_analysis = (
    df.groupby("Sentiment Label")["Engagement_Rate"]
      .mean()
      .sort_values(ascending=False)
)

print(sentiment_analysis)
```

---

## Emotion vs Engagement

```python
emotion_analysis = (
    df.groupby("Emotion Type")["Engagement_Rate"]
      .mean()
      .sort_values(ascending=False)
)

print(emotion_analysis)
```

---

## Platform + Topic Combination

```python
combo_analysis = (
    df.groupby([
        "Platform",
        "Topic Category"
    ])["Engagement_Rate"]
      .mean()
      .sort_values(ascending=False)
)

print(combo_analysis.head(10))
```

---

# 17. Machine-Learning Features

Possible categorical features:

```python
categorical_features = [
    "Platform",
    "Topic Category",
    "Campaign Phase",
    "Sentiment Label",
    "Emotion Type",
    "Posting_Weekday",
    "Posting_Month"
]
```

Possible numerical features:

```python
numerical_features = [
    "Posting_Hour",
    "Sentiment Score"
]
```

Do not include:

```text
Likes
Comments
Shares
Impressions
Total Engagement
Engagement Rate
```

because those values reveal post-publication outcomes.

---

# 18. Prepare Features and Target

```python
features = (
    categorical_features
    + numerical_features
)

X = df[features]

y = df["High_Performance"]
```

---

# 19. Train-Test Split

```python
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)
```

Use:

```text
80% Training
20% Testing
```

---

# 20. Categorical Encoding

```python
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        )
    ],
    remainder="passthrough"
)
```

---

# 21. Random Forest Model

```python
classifier = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
```

Pipeline:

```python
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", classifier)
    ]
)

model.fit(
    X_train,
    y_train
)
```

---

# 22. Predictions

```python
y_pred = model.predict(X_test)

y_probability = (
    model.predict_proba(X_test)[:, 1]
)
```

---

# 23. Model Evaluation

```python
accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred
)

recall = recall_score(
    y_test,
    y_pred
)

f1 = f1_score(
    y_test,
    y_pred
)

auc = roc_auc_score(
    y_test,
    y_probability
)

print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1:", f1)
print("ROC-AUC:", auc)
```

Also print:

```python
print(
    classification_report(
        y_test,
        y_pred
    )
)
```

Because only the top 25% of posts are classified as high-performing, do not judge the model only using accuracy.

Focus on:

- Precision
- Recall
- F1 Score
- ROC-AUC

---

# 24. Confusion Matrix

```python
cm = confusion_matrix(
    y_test,
    y_pred
)

print(cm)
```

Explain during the demo:

- True Positive
- False Positive
- True Negative
- False Negative

---

# 25. Feature Importance

```python
feature_names = (
    model
    .named_steps["preprocessor"]
    .get_feature_names_out()
)

importance = (
    model
    .named_steps["classifier"]
    .feature_importances_
)

feature_importance = (
    pd.DataFrame({
        "Feature": feature_names,
        "Importance": importance
    })
    .sort_values(
        "Importance",
        ascending=False
    )
)

print(
    feature_importance.head(15)
)
```

Possible influential variables could include:

- Platform
- Topic
- Posting Hour
- Sentiment
- Emotion
- Weekday
- Campaign Phase

Do not claim which is strongest until the model is actually run.

---

# 26. Generate Prediction Probabilities for the Dataset

```python
df["Predicted_High_Performance"] = (
    model.predict(
        df[features]
    )
)

df["High_Performance_Probability"] = (
    model.predict_proba(
        df[features]
    )[:, 1]
)
```

---

# 27. Performance Segmentation

```python
df["Performance_Segment"] = pd.cut(
    df[
        "High_Performance_Probability"
    ],
    bins=[
        0,
        0.35,
        0.65,
        1
    ],
    labels=[
        "Low Intent",
        "Medium Intent",
        "High Intent"
    ],
    include_lowest=True
)
```

Interpretation:

```text
0–35%   = Low Intent
35–65%  = Medium Intent
65–100% = High Intent
```

---

# 28. Export Data for Power BI

```python
df.to_csv(
    "output/postpilot_predictions.csv",
    index=False
)

feature_importance.to_csv(
    "output/feature_importance.csv",
    index=False
)
```

---

# 29. Simple Recommendation Layer

This does not require another ML model.

Use historical averages.

## Best Platform

```python
best_platform = (
    df.groupby("Platform")["Engagement_Rate"]
      .mean()
      .idxmax()
)
```

## Best Posting Hour

```python
best_hour = (
    df.groupby("Posting_Hour")["Engagement_Rate"]
      .mean()
      .idxmax()
)
```

## Best Weekday

```python
best_day = (
    df.groupby("Posting_Weekday")["Engagement_Rate"]
      .mean()
      .idxmax()
)
```

## Best Topic

```python
best_topic = (
    df.groupby("Topic Category")["Engagement_Rate"]
      .mean()
      .idxmax()
)
```

## Best Sentiment

```python
best_sentiment = (
    df.groupby("Sentiment Label")["Engagement_Rate"]
      .mean()
      .idxmax()
)
```

---

# 30. Recommendation Output

The notebook can display:

```text
POSTPILOT CONTENT STRATEGY

Best Platform:
<actual result>

Best Topic:
<actual result>

Best Posting Day:
<actual result>

Best Posting Hour:
<actual result>

Best Sentiment:
<actual result>

Best Emotion:
<actual result>
```

Only replace placeholders with actual results from the dataset.

---

# 31. Live Prediction Function

```python
def predict_post(post_data):

    sample = pd.DataFrame(
        [post_data]
    )

    probability = (
        model.predict_proba(
            sample
        )[0, 1]
    )

    prediction = (
        probability >= 0.50
    )

    return {
        "Prediction":
            "High Performance"
            if prediction
            else "Normal Performance",

        "Probability":
            round(
                probability * 100,
                2
            )
    }
```

---

# 32. Example Demo Prediction

```python
post = {
    "Platform": "Instagram",
    "Topic Category": "Technology",
    "Campaign Phase": "Launch",
    "Sentiment Label": "Positive",
    "Emotion Type": "Excited",
    "Posting_Weekday": "Friday",
    "Posting_Month": "September",
    "Posting_Hour": 19,
    "Sentiment Score": 0.8
}

predict_post(post)
```

The output format should be:

```text
Prediction: High Performance
Probability: <actual model probability>
```

---

# 33. Power BI Dashboard

Only create **two pages** before the demo.

## Page 1 — Social Media Performance Analytics

### KPI Cards

- Total Posts
- Total Impressions
- Total Engagement
- Average Engagement Rate
- High-Performance Posts

### Visualizations

1. Engagement Rate by Platform — Bar Chart
2. Engagement Rate by Topic — Horizontal Bar Chart
3. Engagement Rate by Posting Hour — Line Chart
4. Engagement Rate by Weekday — Column Chart
5. Sentiment Distribution — Donut Chart
6. Platform vs Topic — Matrix or heatmap-like table

### Slicers

- Platform
- Topic Category
- Posting Weekday
- Campaign Phase
- Sentiment
- Emotion

---

# 34. Power BI Page 2 — PostPilot Predictive Analytics

### KPI Cards

- Predicted High-Performance Posts
- Average Prediction Probability
- High Intent Posts
- F1 Score
- ROC-AUC

### Visualizations

1. Prediction Probability by Platform
2. Prediction Probability by Topic
3. Prediction Probability by Posting Hour
4. Performance Segment Distribution
5. Feature Importance
6. Best Content Combination Table

Suggested table fields:

- Platform
- Topic
- Weekday
- Hour
- Sentiment
- Engagement Rate
- Predicted Probability

---

# 35. Useful Power BI Measures

## Total Posts

```DAX
Total Posts =
COUNTROWS(PostPilot)
```

## Total Engagement

```DAX
Total Engagement =
SUM(
    PostPilot[Total_Engagement]
)
```

## Average Engagement Rate

```DAX
Avg Engagement Rate =
AVERAGE(
    PostPilot[Engagement_Rate]
)
```

## High-Performance Posts

```DAX
High Performance Posts =
CALCULATE(
    COUNTROWS(PostPilot),
    PostPilot[High_Performance] = 1
)
```

## Predicted High Posts

```DAX
Predicted High Posts =
CALCULATE(
    COUNTROWS(PostPilot),
    PostPilot[Predicted_High_Performance] = 1
)
```

## Average Prediction Probability

```DAX
Avg Prediction Probability =
AVERAGE(
    PostPilot[High_Performance_Probability]
)
```

---

# 36. Final Report Structure

The report should contain:

1. Abstract
2. Introduction
3. Problem Statement
4. Objectives
5. Dataset Description
6. Methodology
7. Data Cleaning
8. Feature Engineering
9. Exploratory Data Analysis
10. Predictive Model
11. Leakage Prevention
12. Model Evaluation
13. Feature Importance
14. Power BI Dashboard
15. Results
16. Recommendations
17. Limitations
18. Future Enhancements
19. Conclusion
20. References

---

# 37. Abstract Draft

Social-media analytics traditionally focuses on understanding content performance after publication. This project introduces PostPilot AI, a predictive social-media analytics system designed to estimate whether a post is likely to achieve high engagement before it is published. Historical social-media data containing platform, topic, time, sentiment, emotion, and engagement information is analyzed using Python. An engagement rate is calculated from historical interactions, and posts in the highest-performing quartile are classified as high-performance content. A Random Forest classifier is trained using only pre-publish features to avoid target leakage. The model outputs both a performance classification and a probability score. Results are exported to Power BI, where interactive descriptive and predictive dashboards allow users to explore engagement patterns, predicted performance, and recommended posting strategies. The project demonstrates how machine learning and business intelligence can be combined to transform retrospective social-media analytics into a practical decision-support system.

---

# 38. Key Technical Point for Presentation

Mention this explicitly:

> **Likes, comments, shares, impressions, and engagement rate are not used by the predictive model because they are only available after publication. They are used only to create the historical high-performance label.**

This is one of the strongest technical decisions in the project.

---

# 39. Limitations

PostPilot AI does not guarantee viral content.

Actual performance can also depend on:

- follower count,
- media quality,
- hashtags,
- current trends,
- platform algorithm changes,
- creator reputation,
- external events.

The current project focuses only on structured historical post metadata.

---

# 40. Future Enhancements

Possible future extensions:

- Caption NLP
- Transformer embeddings
- Image/video analysis
- Hashtag analysis
- Follower-count normalization
- Platform API integration
- Creator-specific models
- A/B testing
- Recommendation engine
- Streamlit frontend
- Automated scheduling
- LLM-generated caption suggestions

These are **future work only**.

Do not implement these before the September 4 demo.

---

# 41. Scope for September 4 Demo

The demo version should contain only:

- cleaned dataset,
- Python EDA,
- engagement-rate calculation,
- high-performance target,
- Random Forest model,
- evaluation metrics,
- feature importance,
- prediction probability,
- recommendation output,
- two Power BI pages,
- short project report.

Avoid before the demo:

- deep learning,
- APIs,
- web scraping,
- LLM integration,
- Streamlit,
- live Instagram/Twitter data,
- multiple model comparisons unless everything else is already complete.

---

# 42. Implementation Schedule

## September 1

Complete:

- dataset acquisition,
- data cleaning,
- feature engineering,
- EDA,
- target construction.

Deliverable:

```text
Clean Dataset + Working EDA Notebook
```

## September 2

Complete:

- train/test split,
- preprocessing,
- Random Forest,
- evaluation,
- feature importance,
- prediction export.

Deliverable:

```text
Working ML Model + postpilot_predictions.csv
```

## September 3

Complete:

- Power BI Page 1,
- Power BI Page 2,
- report,
- screenshots,
- recommendations,
- demo rehearsal.

Deliverable:

```text
Complete Demo-Ready Project
```

## September 4

Demo.

Before presenting:

- run the notebook once,
- refresh Power BI,
- verify metrics,
- test live prediction,
- keep CSV backup,
- keep dashboard screenshots,
- keep the final report locally.

---

# 43. 5–7 Minute Demo Flow

## 0:00–0:45 — Problem

Say:

> Social-media dashboards usually tell us what already happened. PostPilot AI attempts to estimate whether a planned post is likely to perform well before it is published.

## 0:45–1:30 — Dataset

Show:

- Platform
- Timestamp
- Topic
- Sentiment
- Emotion
- Likes
- Comments
- Shares
- Impressions

## 1:30–2:15 — Engagement Label

Explain:

```text
Total Engagement
=
Likes + Comments + Shares
```

and:

```text
Engagement Rate
=
Total Engagement / Impressions
```

Top 25%:

```text
High Performance
```

## 2:15–3:00 — Python EDA

Show:

- platform performance,
- topic performance,
- hour performance,
- weekday performance.

Only mention findings generated from the actual dataset.

## 3:00–4:00 — Machine Learning

Show:

- Random Forest,
- train/test split,
- F1 score,
- ROC-AUC,
- confusion matrix,
- feature importance.

Mention target leakage prevention.

## 4:00–5:30 — Power BI

Show:

- Page 1: Performance Analytics
- Page 2: Predictive Analytics

Use at least one slicer.

## 5:30–6:30 — Live Prediction

Enter one planned-post example and show:

```text
High / Normal Performance
+
Probability
```

## 6:30–7:00 — Conclusion

Say:

> PostPilot AI transforms historical social-media analytics into a predictive decision-support system. It does not guarantee virality, but it identifies patterns that can help users make more informed decisions about platform, topic, timing, and content strategy.

---

# 44. Success Checklist

- [ ] Dataset loads correctly
- [ ] Missing values handled
- [ ] Duplicate rows handled
- [ ] Timestamp features created
- [ ] Engagement rate calculated
- [ ] High-performance target created
- [ ] No target leakage
- [ ] EDA charts generated
- [ ] Random Forest trains successfully
- [ ] Precision/Recall/F1/ROC-AUC calculated
- [ ] Confusion matrix generated
- [ ] Feature importance available
- [ ] Prediction probabilities generated
- [ ] `postpilot_predictions.csv` exported
- [ ] Power BI Page 1 complete
- [ ] Power BI Page 2 complete
- [ ] Recommendation output works
- [ ] Live prediction works
- [ ] Report completed
- [ ] Demo rehearsed

---

# 45. Final Project Statement

**PostPilot AI is a lightweight predictive social-media analytics system that analyzes historical engagement data, learns patterns associated with high-performing content, predicts the probability that a planned post will perform well using pre-publish attributes, and presents the results through an interactive Power BI dashboard.**

The project combines:

```text
Data Analytics
+
Machine Learning
+
Predictive Analytics
+
Business Intelligence
```

while remaining realistic to complete before the September 4 demo.
