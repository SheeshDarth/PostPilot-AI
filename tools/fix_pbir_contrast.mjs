import fs from "node:fs";
import path from "node:path";

const report = "powerbi/PostPilot_AI_YouTube/Power BI Project.Report/definition/pages";
const white = "#FFFFFF";
const light = "#DDE7F3";
const muted = "#B8C8DA";
const grid = "#35516D";
const cardBg = "#152A45";
const cardTitleBg = "#203653";

const lit = (value) => ({ expr: { Literal: { Value: value } } });
const color = (hex) => ({ solid: { color: lit(`'${hex}'`) } });
const number = (n) => lit(`${n}D`);
const bool = (v) => lit(v ? "true" : "false");
const prop = (value) => value;
const setObject = (objects, category, properties) => {
  objects[category] ??= [{}];
  objects[category][0].properties ??= {};
  Object.assign(objects[category][0].properties, properties);
};

for (const page of fs.readdirSync(report, { withFileTypes: true }).filter((e) => e.isDirectory())) {
  const visualsDir = path.join(report, page.name, "visuals");
  if (!fs.existsSync(visualsDir)) continue;
  for (const visual of fs.readdirSync(visualsDir, { withFileTypes: true }).filter((e) => e.isDirectory())) {
    const file = path.join(visualsDir, visual.name, "visual.json");
    if (!fs.existsSync(file)) continue;
    const json = JSON.parse(fs.readFileSync(file, "utf8"));
    const type = json.visual?.visualType;
    const objects = (json.visual.objects ??= {});
    const container = (json.visual.visualContainerObjects ??= {});

    if (type === "card") {
      setObject(objects, "labels", { color: color(white), fontSize: number(22), bold: bool(true) });
      setObject(container, "title", { fontColor: color(white), fontSize: number(13), bold: bool(true), background: color(cardTitleBg) });
      setObject(container, "background", { show: bool(true), color: color(cardBg), transparency: number(0) });
    }

    if (["columnChart", "clusteredColumnChart", "barChart", "lineChart", "scatterChart", "donutChart"].includes(type)) {
      setObject(container, "title", { fontColor: color(white), fontSize: number(14), bold: bool(true) });
      for (const axis of ["categoryAxis", "valueAxis"]) {
        setObject(objects, axis, { labelColor: color(light), titleColor: color(muted), fontSize: number(11), gridlineColor: color(grid), gridlineTransparency: number(25) });
      }
    }

    if (type === "tableEx") {
      setObject(objects, "values", { fontColorPrimary: color(white), fontColorSecondary: color(light), backColorPrimary: color(cardBg), backColorSecondary: color(cardTitleBg), fontSize: number(11) });
      setObject(container, "title", { fontColor: color(white), fontSize: number(14), bold: bool(true) });
    }

    if (type === "slicer") {
      setObject(objects, "items", { fontColor: color(white), textSize: number(12), background: color(cardBg) });
      setObject(objects, "header", { fontColor: color(white), textSize: number(12), bold: bool(true), background: color(cardTitleBg) });
    }

    fs.writeFileSync(file, JSON.stringify(json, null, 2) + "\n", "utf8");
  }
}
console.log("Applied explicit PBIR high-contrast foreground and background properties.");
