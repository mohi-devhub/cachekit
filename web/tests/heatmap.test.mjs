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

test("grouping covers each original bin once and never hides variation", async () => {
  const { groupStability, tileBoundary } = await import("../src/lib/heatmap.ts");
  const values = [1, 1, 1, 0.9, 1, 1, 1];
  const groups = groupStability(values, 3);
  assert.deepEqual(groups, [{ start: 0, end: 2, stability: 1 }, { start: 2, end: 4, stability: 0.9 }, { start: 4, end: 7, stability: 1 }]);
  assert.equal(groups.reduce((n, g) => n + g.end - g.start, 0), values.length);
  assert.deepEqual(groupStability([], 160), []);
  assert.equal(groupStability(values, 160).length, values.length);
  assert.throws(() => groupStability(values, 0));
  assert.deepEqual(tileBoundary(1, 64, 16, 62.5), { x: 1000, y: 187.5 });
  for (const report of [saved.report.report, saved.after.report]) {
    const { fraction } = prefixBoundary(report, "helpdesk.answer");
    for (const [count, columns, size] of [[64, 16, 62.5], [32, 8, 125]]) {
      const { x, y } = tileBoundary(fraction, count, columns, size);
      assert.ok(Math.abs((y / size * columns + x / size) / count - fraction) < 1e-12);
      const grouped = groupStability(report.heatmaps['helpdesk.answer'], count);
      for (const g of grouped) if (tokenColor(g.stability, g.end - 1, 2000, fraction) === tokenColors.reusable) {
        assert.equal(g.stability, 1);
        assert.ok(g.end / 2000 <= fraction);
      }
    }
  }
});

test("stale live candidate permits labeled recorded playback only for the matching BEFORE", async () => {
  const { candidate } = await import("../src/lib/workspace.ts");
  const original = globalThis.fetch;
  try {
    globalThis.fetch = async url => Response.json(String(url).endsWith('/demo/workspace.json') || String(url)==='/demo/workspace.json' ? saved : null);
    const result = await candidate(saved.report.id, saved.report.report.input_sha256);
    assert.equal(result.source, 'SAVED');
    assert.deepEqual(result.data, saved.after);
    assert.equal(await candidate(saved.report.id, '0'.repeat(64)), null);
    assert.equal(await candidate('another-workload', saved.report.report.input_sha256), null);
    globalThis.fetch = async () => Response.json(saved.after);
    assert.equal((await candidate(saved.report.id, saved.report.report.input_sha256)).source, 'API');
  } finally { globalThis.fetch = original; }
});
