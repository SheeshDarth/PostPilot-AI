$ErrorActionPreference = 'Stop'
python src/youtube_postpilot.py --input data/youtube_analytics/YouTube_Video.csv --output output
python src/hashtag_generator.py --input data/youtube_analytics/YouTube_Video.csv --output output/youtube_hashtags.csv
python -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8501
