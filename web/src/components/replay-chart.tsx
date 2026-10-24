"use client";

import { useState } from "react";
import { formatMetric, type MetricUnit } from "@/lib/heatmap";
import type { BenchView } from "@/lib/workspace";

const choices: { label: string; key: string; unit: MetricUnit }[] = [
  { label: "Cache hit rate", key: "measured_hit_rate", unit: "percent" },
  { label: "TTFT p95", key: "ttft_p95_s", unit: "seconds" },
  { label: "GPU $ / 1k", key: "gpu_window_usd_per_1000", unit: "usd" },
];

export function ReplayChart({ data }: { data: BenchView }) {
  const [selected, setSelected] = useState(0);
  const metric = choices[selected];
  const runs = ["before", "after"].map(variant => data.benchmarks.find(b => b.run.variant === variant)?.run);
  const points = runs.map(run => run?.summary[metric.key]);
  if (!data.comparison_ready || !points.every(p => p && [p.min, p.median, p.max].every(Number.isFinite))) return null;
  const series = points.map(p => p!);
  const maximum = Math.max(...series.map(p => p.max));
  const ceiling = metric.unit === "percent" ? 1 : maximum > 0 ? maximum * 1.15 : 1;
  const format = (n: number) => formatMetric(n, metric.unit);
  const description = series.map((p, i) => `${i ? "AFTER" : "BEFORE"}: median ${format(p.median)}, min ${format(p.min)}, max ${format(p.max)}.`).join(" ");
  return <figure className="replay-chart">
    <div className="section-heading"><h3>Compare the measured replay</h3>
      <div className="segmented" aria-label="Chart metric">{choices.map((choice, i) => <button key={choice.key} aria-pressed={selected === i} onClick={() => setSelected(i)}>{choice.label}</button>)}</div>
    </div>
    <div className="paired-plot" role="img" aria-label={`${metric.label}. ${description}`}>
      {[0, 0.25, 0.5, 0.75, 1].map(fraction => <div aria-hidden="true" key={fraction} className="plot-gridline" style={{ bottom: `${fraction * 100}%` }}><span>{format(ceiling * fraction)}</span></div>)}
      {series.map((point, i) => <div aria-hidden="true" className={`plot-series ${i ? "after" : "before"}`} key={i} style={{ left: i ? "72%" : "28%" }}>
        <div className="plot-bar" style={{ height: `${point.median / ceiling * 100}%` }} />
        <div className="plot-whisker" style={{ bottom: `${point.min / ceiling * 100}%`, height: `${(point.max - point.min) / ceiling * 100}%` }} />
        <strong className="plot-value" style={{ bottom: `calc(${point.max / ceiling * 100}% + 12px)` }}>{format(point.median)}</strong>
        <span className="plot-label">{i ? "AFTER" : "BEFORE"}</span>
      </div>)}
    </div>
    <figcaption>Median with min–max whiskers from {runs[0]?.runs.length} saved repetitions per view. {metric.unit === "usd" ? "GPU-window cost; full bill excluded." : metric.unit === "seconds" ? "Client TTFT; queue delay excluded." : "Observed prefix-cache token counters."}</figcaption>
  </figure>;
}
