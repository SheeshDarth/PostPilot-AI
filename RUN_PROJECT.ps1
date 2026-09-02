$ErrorActionPreference = 'Stop'
python -m pip install -r requirements.txt
python src/instagram_postpilot.py --input data/instagram_analytics/Instagram_Analytics.csv --output output
Write-Host 'Done. Open output\instagram_model_metrics.csv and import output\instagram_predictions.csv into Power BI.'
