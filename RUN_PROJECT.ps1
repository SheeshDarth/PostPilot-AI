$ErrorActionPreference = 'Stop'
python -m pip install -r requirements.txt
python src/youtube_postpilot.py --input data/youtube_analytics/YouTube_Video.csv --output output
python src/hashtag_generator.py --input data/youtube_analytics/YouTube_Video.csv --output output/youtube_hashtags.csv
Write-Host 'Done. Import output\youtube_predictions.csv and output\youtube_hashtags.csv into Power BI.'
