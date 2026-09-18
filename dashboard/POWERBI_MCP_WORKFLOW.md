# Power BI Modeling MCP workflow for PostPilot AI

The repository configuration in `.vscode/mcp.json` registers Microsoft's official Power BI Modeling MCP server for VS Code/Copilot. It is intended for semantic-model operations, not visual report-page authoring.

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

## Important limitation

This MCP can modify the semantic model—tables, columns, measures, relationships, and DAX queries—but it does not create or arrange report pages, charts, cards, slicers, or themes. Those visual steps remain in Power BI Desktop. The local Streamlit dashboard is available at `http://127.0.0.1:8501` as the fully automated alternative.

## Safety

Keep the MCP in read/write mode with confirmation prompts. Do not use `--skipconfirmation` for this project. Do not expose credentials, access tokens, or the `.pbix` file in chat. Review every proposed model change before applying it.
