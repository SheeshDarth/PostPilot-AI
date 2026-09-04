$ErrorActionPreference = 'Stop'
python -m pip install -r requirements.txt
python src/youtube_postpilot.py --input data/youtube_analytics/YouTube_Video.csv --output output
Write-Host 'Done. Open output\youtube_model_metrics.csv and import output\youtube_predictions.csv into Power BI.'
