import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { currentReportState, reportOptions } from "../src/lib/report-selection.ts";
import { report } from "../src/lib/workspace.ts";

const saved = JSON.parse(readFileSync(new URL("../public/demo/workspace.json", import.meta.url)));
const gpt = "ce11d0af6410ce36da21753cd86cdd73101d41bc266236de24b8e4fa8adf5327";
const swe = "c8bcc8d8b47ea53c0b58b6a8e0552638aad82e9fae65471b905f90c5d24fd160";
const summary = (id, routes, timestamp = "2026-10-24T22:39:57.190696+00:00") => ({
  id, routes, timestamp, n_requests: 8, n_findings: 2,
});

test("discovered named reports distinguish controlled inputs from historical trajectories", () => {
  const options = reportOptions([
    summary(gpt, ["gpt-researcher.generate_report"]),
    { ...summary(swe, ["swe-agent.step"]), n_requests: 136, n_findings: 6 },
  ], gpt);
  assert.match(options.find(option => option.id === gpt).label, /GPT Researcher · controlled inputs · 8 requests · 2 findings/);
  assert.match(options.find(option => option.id === swe).label, /SWE-agent · historical trajectories · 136 requests · 6 findings/);
  assert.ok(options.some(option => option.id === "demo-before"));
});

test("new runs retain their actual route, count, timestamp and identity without borrowing known labels", () => {
  const ids = ["1".repeat(64), "2".repeat(64), "3".repeat(64)];
  const options = reportOptions([
    summary(ids[0], ["gpt-researcher.generate_report"]),
    summary(ids[1], ["gpt-researcher.generate_report"], "2026-10-25T00:00:00Z"),
    summary(ids[2], ["custom.route", "another.route"]),
  ], ids[0]);
  assert.match(options[0].label, /gpt-researcher.generate_report · 8 requests · 2 findings · 2026-10-24 22:39:57 UTC · 111111111111/);
  assert.match(options[1].label, /2026-10-25 00:00:00 UTC · 222222222222/);
  assert.match(options[2].label, /custom.route · another.route/);
  assert.ok(options.every(option => !/controlled inputs|historical trajectories/.test(option.label)));
});

test("offline options contain only the helpdesk and the requested URL, with no fabricated local counts", () => {
  assert.deepEqual(reportOptions([], "demo-before"), [{ id: "demo-before", label: "Fictional helpdesk · saved demo" }]);
  const options = reportOptions([], gpt);
  assert.deepEqual(options.map(option => option.id), ["demo-before", gpt]);
  assert.doesNotMatch(options[1].label, /requests|findings/);
});

test("the selected bundle supplies its own counts and a mismatched bundle never supplies another report's evidence", () => {
  const options = reportOptions([], saved.report.id, saved.report);
  assert.match(options[0].label, new RegExp(`${saved.report.report.n_requests} requests`));
  assert.match(options[0].label, new RegExp(`${saved.report.report.findings.length} findings`));
  assert.doesNotMatch(reportOptions([], gpt, saved.report).find(option => option.id === gpt).label, /requests|findings/);
});

test("changing report IDs immediately hides old evidence and errors while the next request is pending", () => {
  const loaded = { data: saved.report, source: "SAVED" };
  const previous = { id: saved.report.id, loaded };
  assert.equal(currentReportState(saved.report.id, previous).loaded, loaded);
  assert.deepEqual(currentReportState(gpt, previous), { id: gpt });
  assert.deepEqual(currentReportState(swe, { id: gpt, error: "Unavailable" }), { id: swe });
  assert.deepEqual(currentReportState(swe, previous), { id: swe });
  assert.equal(currentReportState(gpt, { id: gpt, error: "Unavailable" }).error, "Unavailable");
});

test("an unavailable local report rejects offline instead of showing the helpdesk bundle", async () => {
  const original = globalThis.fetch;
  try {
    globalThis.fetch = async url => {
      if (url === "/demo/workspace.json") return Response.json(saved);
      throw new Error("API offline");
    };
    assert.deepEqual(await report(saved.report.id), { source: "SAVED", data: saved.report });
    for (const id of [gpt, swe, "4".repeat(64)]) {
      await assert.rejects(report(id), /This report needs your local API/);
    }
  } finally { globalThis.fetch = original; }
});
