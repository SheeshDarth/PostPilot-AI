# Power BI Modeling MCP workflow for PostPilot AI

The repository configuration in `.vscode/mcp.json` registers both the Power BI Modeling MCP and the local Power BI Report MCP. The modeling server handles the semantic model; the report server handles PBIR pages, visuals, themes, filters, and layout.

## Before connecting

1. Save and close unrelated Power BI reports.
2. Open the PostPilot AI `.pbix` file in Power BI Desktop.
3. Save a backup copy of the `.pbix` before making model changes.
4. Open this repository in VS Code.
5. Ensure GitHub Copilot Chat and the Power BI Modeling MCP extension/server are enabled.

## Connect

In Copilot Chat, use:

```text
Connect to '[exact Power BI file name]' in Power BI Desktop.
```

Use the exact title/file name shown by Power BI Desktop. The MCP server searches for the matching local Analysis Services instance.

The report-authoring server is preconfigured for:

```text
C:\Users\Siddharth\Desktop\PE3 project\powerbi\PostPilot_AI_YouTube\Power BI Project.Report
```

## Safe validation prompts

Run read-only checks first:

```text
List the connected semantic model tables, columns, measures, and relationships. Do not modify anything.
```

```text
Validate the relationship between YouTube[post_id] and YouTubeHashtags[post_id]. Do not modify anything.
```

```text
Run a DAX query that returns the row count of YouTube, the row count of YouTubeHashtags, and the average High_Performance_Probability. Do not modify anything.
```

## Model changes for PostPilot AI

Only after reviewing the read-only results, ask the MCP server to create these measures:

```text
Create the following measures in the appropriate tables: Total Videos, Predicted High Videos, Predicted High Rate, Average Prediction Probability, Average Hashtag Relevance, Average Hashtags per Video, Average Watch Time, Average CTR, Total Impressions, Subscribers Gained, Test Accuracy, Test F1, Test ROC AUC, and Decision Threshold. Show the generated DAX and ask for confirmation before applying changes.
```

The canonical DAX is in `dashboard/PostPilot_AI_Measures.dax`.

## Report-authoring prompt

After restarting the MCP client, use:

```text
Inspect the connected PBIR report and semantic model. Do not modify anything yet.
```

After the inspection succeeds, use:

```text
Create the complete PostPilot AI YouTube dashboard. Use the exact semantic model tables YouTube, YouTubeHastags, and FeatureImportance and the existing measures. Add KPI cards, category/watch-time chart, traffic-source/CTR chart, weekday upload-coverage chart, duration/watch-time scatter chart, prediction segment donut, probability-by-source chart, actual-versus-predicted comparison, feature-importance chart, hashtag table, slicers, titles, spacing, and a dark navy/teal theme. Validate bindings and layout before saving. The source has one upload hour only, so do not present an hourly timing recommendation.
```

The local Streamlit dashboard remains available at `http://127.0.0.1:8501` as a fully automated alternative.

## Safety

Keep the MCP in read/write mode with confirmation prompts. Do not use `--skipconfirmation` for this project. Do not expose credentials, access tokens, or the `.pbix` file in chat. Review every proposed model change before applying it.
