import Link from "next/link";
import { matchingMeasurement, formatMetric, type MetricUnit } from "@/lib/heatmap";
import { percent, type BenchView, type ReportBundle } from "@/lib/workspace";
import { MeasuredNumber } from "@/components/measured-number";

export function HeatmapMetrics({ bench, report, variant }: {
  bench?: BenchView; report: ReportBundle["report"]; variant: "before" | "after";
}) {
  const artifact = matchingMeasurement(bench, report, variant);
  const backend = report.backends.find(b => b.backend === "vllm");
  const rows: [string, string, MetricUnit][] = artifact ? [
    ["Cache-hit rate", "measured_hit_rate", "percent"],
    ["Client TTFT p95", "ttft_p95_s", "seconds"],
    ["GPU-window USD / 1k", "gpu_window_usd_per_1000", "usd"],
  ] : [];
  return <section className="heatmap-metrics" aria-label={`${variant} evidence`}>
    <div className="section-heading"><h2>{variant.toUpperCase()} evidence</h2><span className="badge">{artifact ? "MEASURED" : "SIMULATED"}</span></div>
    <dl className="metric-grid" aria-live="polite">
      {artifact ? rows.map(([label, key, unit]) => <div key={key}><dt>{label}</dt><dd>{artifact.run.summary[key] ? <><strong><MeasuredNumber value={artifact.run.summary[key].median} unit={unit} /></strong><span className="measure-range">min {formatMetric(artifact.run.summary[key].min, unit)} · max {formatMetric(artifact.run.summary[key].max, unit)}</span></> : "Not recorded"}</dd></div>) : <>
        <div><dt>Simulated cache-hit rate</dt><dd><strong>{backend ? percent(backend.actual_hit_rate) : "Not recorded"}</strong></dd></div>
        <div><dt>Client TTFT p95</dt><dd>Not measured for this view</dd></div>
        <div><dt>GPU-window USD / 1k</dt><dd>Not measured for this view</dd></div>
      </>}
    </dl>
    <p className="supporting-text">{artifact ? <>Median (min–max) across {artifact.run.runs.length} saved repetitions with matching request bytes. Sequential replay; TTFT excludes client queueing. GPU-window cost is not the full bill. <Link href="/bench">Inspect measured provenance</Link>.</> : "No matching measured pair is available. Simulation supplies no latency or dollar claim."}</p>
  </section>;
}
