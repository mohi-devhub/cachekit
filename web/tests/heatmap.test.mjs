import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { prefixBoundary, tokenColor, tokenColors, matchingMeasurement } from "../src/lib/heatmap.ts";

const saved = JSON.parse(readFileSync(new URL("../public/demo/workspace.json", import.meta.url)));

test("marker follows actual finding offsets and reference lengths in both saved views", () => {
  const before = prefixBoundary(saved.report.report, "helpdesk.answer");
  const after = prefixBoundary(saved.after.report, "helpdesk.answer");
  assert.equal(before.first, 7);
  assert.equal(after.first, 4270);
  assert.equal(before.fraction, before.first / before.total);
  assert.equal(after.fraction, after.first / after.total);
  assert.ok(before.fraction < after.fraction);
  assert.equal(prefixBoundary({ findings: [], backends: [] }, "missing").fraction, null);
});

test("stable tokens after a broken prefix stay red; variable bins stay amber", () => {
  assert.equal(tokenColor(1, 0, 100, 0.5), tokenColors.reusable);
  assert.equal(tokenColor(1, 70, 100, 0.5), tokenColors.recomputed);
  assert.equal(tokenColor(0.95, 0, 100, 0.5), tokenColors.variable);
  assert.equal(tokenColor(1, 0, 100, null), tokenColors.recomputed);
});

test("measured view requires matched replay pair, variant and exact request bytes", () => {
  for (const [variant, report] of [["before", saved.report.report], ["after", saved.after.report]]) {
    const match = matchingMeasurement(saved.bench, report, variant);
    assert.ok(match);
    assert.equal(match.run.input_sha256, report.input_sha256);
    assert.equal(matchingMeasurement(saved.bench, { ...report, input_sha256: "0".repeat(64) }, variant), undefined);
    assert.equal(matchingMeasurement({ ...saved.bench, comparison_ready: false }, report, variant), undefined);
  }
});
