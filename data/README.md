# Dataset

The working file `social_media_engagement.csv` is downloaded from the Kaggle dataset by SubashMaster0411:

<https://www.kaggle.com/datasets/subashmaster0411/social-media-engagement-dataset>

It is intentionally ignored by Git because it is raw data. The pipeline normalizes its lowercase column names and excludes `engagement_rate`, `user_engagement_growth`, and `buzz_change_rate` from predictive features because they are outcome-derived or potentially post-publication signals.
