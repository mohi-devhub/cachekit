import { number, percent, type BenchView, type BenchmarkRun } from "@/lib/workspace";

const seconds = (n: number) => `${n.toFixed(3)} s`;
const usd = (n: number) => new Intl.NumberFormat("en", { style: "currency", currency: "USD", maximumFractionDigits: 4 }).format(n);
const metrics: [string, string, (n: number) => string][] = [
  ["Measured cache-hit rate", "measured_hit_rate", percent],
  ["Simulated cache-hit rate", "simulated_hit_rate", percent],
  ["Absolute prediction error", "absolute_hit_rate_error", percent],
  ["Client TTFT p50", "ttft_p50_s", seconds],
  ["Client TTFT p95", "ttft_p95_s", seconds],
  ["Request latency p50", "latency_p50_s", seconds],
  ["Request latency p95", "latency_p95_s", seconds],
  ["Completed requests / second", "throughput_requests_s", n => n.toFixed(3)],
  ["Allocated GPU-seconds / 1k requests", "allocated_gpu_seconds_per_1000", n => n.toFixed(2)],
  ["GPU-window USD / 1k requests", "gpu_window_usd_per_1000", usd],
];
function value(run: BenchmarkRun | undefined, key: string, format: (n: number) => string) {
  const result = run?.summary[key];
  return result ? format(result.median) : "<pending>";
}
export function BenchmarkResults({ data }: { data: BenchView }) {
  const before = data.benchmarks.find(x => x.run.variant === "before")?.run;
  const after = data.benchmarks.find(x => x.run.variant === "after")?.run;
  const title = data.comparison_ready ? "Paired sequential replay" : before && after ? "Runs are not a matched pair" : before ? "BEFORE baseline · AFTER pending" : after ? "AFTER candidate · BEFORE pending" : "Performance replay pending";
  return <section className="report-section">
    <div className="section-heading"><h2>{title}</h2><span className="badge">MEASURED EVIDENCE</span></div>
    <p>{data.note}</p>
    {data.benchmarks.length > 0 && <><div className="table-scroll"><table>
      <caption>Median across the repetitions saved in each artifact. AFTER is a candidate measurement; behavioral approval is separate.</caption>
      <thead><tr><th>Metric</th><th>BEFORE</th><th>AFTER</th></tr></thead><tbody>
        <tr><td>Requests per repetition</td><td>{before ? number(before.n_requests) : "<pending>"}</td><td>{after ? number(after.n_requests) : "<pending>"}</td></tr>
        <tr><td>Repetitions</td><td>{before ? number(before.runs.length) : "<pending>"}</td><td>{after ? number(after.runs.length) : "<pending>"}</td></tr>
        {metrics.map(([label, key, format]) => <tr key={key}><td>{label}</td><td>{value(before, key, format)}</td><td>{value(after, key, format)}</td></tr>)}
      </tbody></table></div>
      <p className="supporting-text">One request is in flight at a time. Bursts wait at the client; TTFT and request latency start at send time and exclude that queue delay. GPU-window cost excludes startup, warmup, reset, idle, CPU, memory and storage. It is not the full Modal bill.</p>
      {data.benchmarks.map(({ source, sha256, run }) => <details className="metadata" key={source}>
        <summary>{run.variant.toUpperCase()} repetitions and provenance</summary>
        <div className="table-scroll"><table><thead><tr><th>Repetition</th><th>Queried tokens</th><th>Cached tokens</th><th>TTFT p50</th><th>TTFT p95</th><th>Max client lag</th></tr></thead><tbody>
          {run.runs.map(r => <tr key={r.repetition}><td>{number(r.repetition)}</td><td>{number(r.queried_tokens)}</td><td>{number(r.cached_tokens)}</td><td>{seconds(r.ttft_p50_s)}</td><td>{seconds(r.ttft_p95_s)}</td><td>{seconds(Math.max(...r.requests.map(x => x.scheduling_delay_s)))}</td></tr>)}
        </tbody></table></div>
        <dl><div><dt>Saved source</dt><dd><code>{source}</code></dd></div><div><dt>Artifact SHA-256</dt><dd><code>{sha256}</code></dd></div><div><dt>Recorded</dt><dd>{run.timestamp}</dd></div><div><dt>Model / GPU</dt><dd>{run.deployment.model} · {run.deployment.gpu}</dd></div><div><dt>Source SHA-256</dt><dd><code>{run.source_sha256}</code></dd></div><div><dt>Scope and limitations</dt><dd>{run.note}</dd></div></dl>
      </details>)}
    </>}
  </section>;
}
