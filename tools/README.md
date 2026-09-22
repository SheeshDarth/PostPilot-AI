# Project tools

The bundled `powerbi-report-mcp` source is included for the Power BI PBIP report-authoring workflow.

From the project root, run:

```powershell
Set-Location .\tools\powerbi-report-mcp
npm install
npm run build
Set-Location ..\..
```

Then restart the MCP client. The workspace configuration in `.vscode/mcp.json` uses `${workspaceFolder}` so the project can be moved to another teammate's computer without editing absolute paths.

The semantic model MCP is installed on demand through `npx`.
