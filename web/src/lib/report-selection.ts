import type { Loaded, ReportBundle } from "./workspace";

export type ReportSummary = {
  id: string;
  n_requests: number;
  n_findings: number;
  routes: string[];
  timestamp: string;
};

export type ReportState = { id: string; loaded?: Loaded<ReportBundle>; error?: string };

// Effects run after render. Hide the previous ID's result immediately, including errors.
export function currentReportState(id: string, state: ReportState): ReportState {
  return state.id === id ? state : { id };
}

const namedReports: Record<string, string> = {
  "demo-before": "Fictional helpdesk · saved demo",
  ce11d0af6410ce36da21753cd86cdd73101d41bc266236de24b8e4fa8adf5327: "GPT Researcher · controlled inputs",
  c8bcc8d8b47ea53c0b58b6a8e0552638aad82e9fae65471b905f90c5d24fd160: "SWE-agent · historical trajectories",
};

function optionLabel(id: string, summary?: ReportSummary): string {
  const name = namedReports[id] || summary?.routes.join(" · ") || "Report";
  const identity = id === "demo-before" ? [] : [id.slice(0, 12)];
  if (!summary) return [name, ...identity].join(" · ");
  const date = new Date(summary.timestamp);
  const timestamp = Number.isNaN(date.getTime()) ? summary.timestamp
    : `${date.toISOString().slice(0, 19).replace("T", " ")} UTC`;
  return [name, `${summary.n_requests} requests`, `${summary.n_findings} findings`, timestamp, ...identity].filter(Boolean).join(" · ");
}

export function reportOptions(reports: ReportSummary[], id: string, bundle?: ReportBundle): { id: string; label: string }[] {
  const available = new Map<string, ReportSummary | undefined>(reports.map(report => [report.id, report]));
  // This is the one public offline report. Local reports enter only through discovery or their own URL.
  if (!available.has("demo-before")) available.set("demo-before", undefined);
  if (bundle?.id === id) available.set(id, {
    id, n_requests: bundle.report.n_requests, n_findings: bundle.report.findings.length,
    routes: bundle.report.routes, timestamp: bundle.metadata.timestamp,
  });
  if (!available.has(id)) available.set(id, undefined);
  return Array.from(available, ([id, summary]) => ({ id, label: optionLabel(id, summary) }));
}
