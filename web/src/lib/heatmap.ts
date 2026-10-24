import type { BenchView, ReportBundle } from "./workspace";

export const tokenColors = { reusable: "#006d5b", variable: "#ffe066", recomputed: "#e03131" };

export function prefixBoundary(report: ReportBundle["report"], route: string) {
  const offsets = report.findings.filter(f => f.route === route).map(f => f.first_divergence_token);
  const total = report.backends.find(b => b.backend === "vllm")?.params.heatmap_reference_tokens?.[route];
  const first = offsets.length ? Math.min(...offsets) : null;
  return { first, total, fraction: first !== null && total ? Math.min(1, Math.max(0, first / total)) : null };
}

export function tokenColor(stability: number, index: number, count: number, boundary: number | null) {
  if (stability < 1) return tokenColors.variable;
  // Stability alone is insufficient: a static token after a broken prefix is recomputed.
  return boundary !== null && (index + 1) / count <= boundary ? tokenColors.reusable : tokenColors.recomputed;
}

export function matchingMeasurement(bench: BenchView | undefined, report: ReportBundle["report"], variant: "before" | "after") {
  if (!bench?.comparison_ready) return undefined;
  return bench.benchmarks.find(b => b.run.variant === variant && b.run.input_sha256 === report.input_sha256);
}

export function groupStability(values: number[], maximumGroups: number) {
  if (!Number.isInteger(maximumGroups) || maximumGroups < 1) throw new Error("Invalid display group count");
  const count = Math.min(values.length, maximumGroups);
  return Array.from({ length: count }, (_, i) => {
    const start = Math.floor(i * values.length / count);
    const end = Math.floor((i + 1) * values.length / count);
    return { start, end, stability: Math.min(...values.slice(start, end)) };
  });
}

export function tileBoundary(boundary: number, count: number, columns: number, size: number) {
  if (count < 1) return { x: 0, y: 0 };
  const index = Math.min(Math.max(boundary, 0), 1) * count;
  const row = Math.min(Math.floor(index / columns), Math.ceil(count / columns) - 1);
  return { x: (index - row * columns) * size, y: row * size };
}

export type MetricUnit = "percent" | "seconds" | "usd";
export const formatMetric = (value: number, unit: MetricUnit) => unit === "percent" ? `${(value * 100).toFixed(3)}%` : unit === "seconds" ? `${value.toFixed(3)} s` : `$${value.toFixed(4)}`;
