"use client";

import Link from "next/link";
import { BenchmarkResults } from "@/components/benchmark-results";
import { ReportSwitcher } from "@/components/report-switcher";
import { PrefixMap } from "@/components/prefix-map";
import { HeatmapMetrics } from "@/components/heatmap-metrics";
import { prefixBoundary, matchingMeasurement, formatMetric } from "@/lib/heatmap";
import { OverviewMotion } from "@/components/overview-motion";
import { SummaryReveal } from "@/components/summary-reveal";
import { FadeContent } from "@/components/react-bits/fade-content";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, candidate, demo, report, number, percent, words, type CandidateView, type BenchView, type Dataset,
  type Finding, type Loaded, type ReportBundle, type TaskView } from "@/lib/workspace";
import { currentReportState, type ReportState } from "@/lib/report-selection";

function Badge({ children, tone = "neutral" }: { children: React.ReactNode; tone?: string }) {
  return <span className={`badge ${tone}`}>{children}</span>;
}
function ErrorState({ message }: { message: string }) {
  return <section className="notice error" role="alert"><h2>Could not load this workspace</h2><p>{message}</p><Link href="/report/demo-before">Open the saved report</Link></section>;
}
function Loading() { return <p className="loading" role="status">Loading saved evidence…</p>; }
function Metadata({ data }: { data: ReportBundle }) {
  return <details className="metadata"><summary>Run provenance</summary><dl>
    <div><dt>Report ID</dt><dd><code>{data.id}</code></dd></div>
    <div><dt>Dataset</dt><dd>{data.metadata.dataset.join(" · ") || "Unrecorded"}</dd></div>
    <div><dt>Saved</dt><dd>{data.metadata.timestamp}</dd></div>
    <div><dt>Model</dt><dd>{data.metadata.model}</dd></div>
    <div><dt>Tokenizer revision</dt><dd><code>{data.metadata.tokenizer.revision}</code></dd></div>
    <div><dt>Git revision</dt><dd>{data.metadata.git_sha || "Unrecorded · pre-Git run"}{data.metadata.git_dirty ? " · working tree had changes" : ""}</dd></div>
    <div><dt>Input SHA-256</dt><dd><code>{data.report.input_sha256}</code></dd></div>
    <div><dt>Configuration SHA-256</dt><dd><code>{data.report.config_sha256}</code></dd></div>
    <div><dt>Evidence</dt><dd>{data.metadata.note}</dd></div>
  </dl></details>;
}
function useReport(id: string) {
  const [state, setState] = useState<ReportState>({ id });
  useEffect(() => { let active = true; report(id).then(loaded => { if (active) setState({ id, loaded }); })
    .catch(error => { if (active) setState({ id, error: error.message }); }); return () => { active = false; }; }, [id]);
  return currentReportState(id, state);
}
function useBench() {
  const [loaded, setLoaded] = useState<Loaded<BenchView>>(); const [error, setError] = useState("");
  useEffect(() => { let active = true; api<BenchView>("/bench").then(data => ({ data, source: "API" as const })).catch(async () => ({ data: (await demo()).bench, source: "SAVED" as const })).then(data => { if (active) setLoaded(data); }).catch(e => { if (active) setError(e.message); }); return () => { active = false; }; }, []);
  return { loaded, error };
}
function Reuse({ data }: { data: ReportBundle }) {
  const profile = data.report.backends.find(b => b.backend === "vllm");
  if (!profile) return <p>No vLLM result is available.</p>;
  return <section className="reuse" aria-labelledby="reuse-title">
    <div className="section-heading"><h2 id="reuse-title">A longer reusable prefix</h2><Badge>SIMULATED</Badge></div>
    <div className="reuse-row"><span>Current reuse</span><div className="bar-track"><span style={{ width: `${profile.actual_hit_rate * 100}%` }} /></div><strong>{percent(profile.actual_hit_rate)}</strong></div>
    <div className="reuse-row projected"><span>Projected reuse</span><div className="bar-track"><span style={{ width: `${profile.achievable_hit_rate * 100}%` }} /></div><strong>{percent(profile.achievable_hit_rate)}</strong></div>
    <p className="supporting-text">Projection reorders eligible content. It is not a measured speedup or an approved application fix.</p>
  </section>;
}

export function AnalyzeWorkspace() {
  const router = useRouter();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [connected, setConnected] = useState(false);
  const [saved, setSaved] = useState<ReportBundle>();
  const [selected, setSelected] = useState("demo-before");
  const [file, setFile] = useState<File>();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    api<Dataset[]>("/datasets").then(data => { if (active) { setDatasets(data); setConnected(true); } }).catch(() => {});
    demo().then(data => { if (active) setSaved(data.report); }).catch(() => {});
    return () => { active = false; };
  }, []);
  async function analyze(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      const result = file
        ? await api<{ report_id: string }>("/analyze/upload", { method: "POST", body: file, headers: { "Content-Type": "application/x-ndjson" } }, 120000)
        : await api<{ report_id: string }>("/analyze", { method: "POST", body: JSON.stringify({ dataset_id: selected }), headers: { "Content-Type": "application/json" } }, 120000);
      router.push(`/report/${result.report_id}`);
    } catch (error) { setError(error instanceof Error ? error.message : "Analysis could not finish."); setBusy(false); }
  }
  return <>
    <OverviewMotion /><section className="page-intro"><FadeContent><h1>Find what breaks prompt caching. Verify the fix before you ship.</h1></FadeContent>
      <p className="lede">A timestamp, user ID or changing tool order can invalidate a reusable prompt prefix. cachekit finds these breaks in your request logs and shows the stable content being recomputed.</p>
      <div className="actions"><Link className="button primary" href="/report/demo-before">Explore saved demo</Link><Link className="button outline" href="#analyze-log">Analyze a log</Link></div>
    </section>
    <SummaryReveal className="analyze-grid"><section className="saved-panel"><h2>The saved helpdesk run</h2><p>A fictional support agent mixes changing context into its reusable instructions. Inspect the actual saved findings.</p>
      {saved && <><p className="run-line"><strong>{number(saved.report.n_requests)}</strong> requests <span aria-hidden="true">·</span> <strong>{number(saved.report.findings.length)}</strong> findings <Badge>SAVED</Badge></p><Reuse data={saved} /></>}
      <Link className="text-link" href="/report/demo-before">Open saved report <span aria-hidden="true">→</span></Link>
    </section><section className="input-panel" id="analyze-log"><div className="section-heading"><h2>Analyze a request log</h2><Badge tone={connected ? "good" : "neutral"}>{connected ? "LOCAL API" : "SAVED DEMO"}</Badge></div>
      <form onSubmit={analyze}><label htmlFor="dataset">Local dataset</label><select id="dataset" value={selected} onChange={e => { setSelected(e.target.value); setFile(undefined); }} disabled={!connected || busy}>
        {datasets.length ? datasets.map(d => <option key={d.id} value={d.id} disabled={!d.available}>{d.name}{d.available ? "" : " · unavailable"}</option>) : <option value="demo-before">Fictional helpdesk · BEFORE</option>}
      </select><label htmlFor="upload">Or choose your JSONL file</label><input id="upload" type="file" accept=".jsonl,.ndjson" disabled={!connected || busy} onChange={e => setFile(e.target.files?.[0])} />
      <p className="supporting-text">Logs stay on your local API or your Modal workspace. No inference runs during analysis.</p>
      <details className="metadata"><summary>Analysis profile</summary><p>vLLM · pinned Qwen tokenizer. Analysis is local and deterministic.</p></details>
      <button className="button primary" disabled={!connected || busy} type="submit">{busy ? "Analyzing locally…" : "Analyze log"}</button>
      {!connected && <p className="supporting-text">Start the local API to analyze files. The saved report works without it.</p>}
      {error && <p className="notice error" role="alert">{error}</p>}</form>
    </section></SummaryReveal>

  </>;
}

function FindingRow({ finding }: { finding: Finding }) {
  const [expanded, setExpanded] = useState(false);
  return <><tr><td><button className="finding-toggle" aria-expanded={expanded} onClick={() => setExpanded(!expanded)}>{words(finding.breaker)} <span aria-hidden="true">{expanded ? "−" : "+"}</span></button></td>
    <td><Badge tone={finding.severity === "high" ? "warn" : "neutral"}>{finding.severity}</Badge></td><td>{number(finding.requests_affected)}</td><td>{number(finding.stable_tokens_after)}</td><td>{finding.safe_to_move ? "Eligible for projection" : "Review required"}</td></tr>
    {expanded && <tr><td colSpan={5} className="finding-detail"><p>{finding.fix_hint}</p><dl className="inline-data"><div><dt>First observed divergence</dt><dd>Token {number(finding.first_divergence_token)}</dd></div><div><dt>Potential stable-token recomputation</dt><dd>{number(finding.tokens_wasted)} · overlapping attribution</dd></div></dl>{finding.evidence.map((text, i) => <p className="evidence" key={i}>{text}</p>)}</td></tr>}
  </>;
}

export function ReportWorkspace({ id }: { id: string }) {
  const { loaded, error } = useReport(id);
  return <><Link href="/" className="back-link">← Workspace</Link>
    <ReportSwitcher id={id} bundle={loaded?.data} />
    {error ? <ErrorState message={error} /> : loaded ? <ReportContents key={id} id={id} loaded={loaded} /> : <Loading />}
  </>;
}

function ReportContents({ id, loaded }: { id: string; loaded: Loaded<ReportBundle> }) {
  const { loaded: bench, error: benchError } = useBench();
  const router = useRouter();
  const [busy, setBusy] = useState(false); const [taskError, setTaskError] = useState("");
  const { data, source } = loaded;
  const backend = data.report.backends.find(b => b.backend === "vllm");
  const measuredCost = matchingMeasurement(bench?.data, data.report, "before")?.run.summary.gpu_window_usd_per_1000;
  async function createTask() {
    setBusy(true); setTaskError("");
    try { const task = await api<TaskView>(`/reports/${encodeURIComponent(id)}/task`, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" }, 120000); router.push(`/fix/${task.task.id}`); }
    catch (error) { setTaskError(error instanceof Error ? error.message : "The task could not be prepared."); setBusy(false); }
  }
  return <><header className="report-header"><div><h1>Prompt reuse, explained.</h1><p className="lede">{data.report.routes.join(" · ")}</p></div><div className="badges"><Badge>{source}</Badge><Badge>SIMULATED</Badge></div></header>
    <SummaryReveal className="run-facts"><div><span>Requests</span><strong>{number(data.report.n_requests)}</strong></div><div><span>Routes</span><strong>{number(data.report.routes.length)}</strong></div><div><span>Findings</span><strong>{number(data.report.findings.length)}</strong></div><div><span>Profile</span><strong>vLLM</strong></div></SummaryReveal>
    <Reuse data={data} />
    {backend && <div className="recomputed"><p><span>Tokens recomputed · current</span><strong>{number(backend.tokens_recomputed_actual)}</strong></p><p><span>Tokens recomputed · projection</span><strong>{number(backend.tokens_recomputed_achievable)}</strong></p><p><span>GPU-window USD / 1k</span><strong className="cost-value">{measuredCost ? formatMetric(measuredCost.median, "usd") : benchError ? "Replay unavailable" : bench ? "No matching measured replay" : "Loading replay…"}</strong>{measuredCost && <><Badge>MEASURED</Badge><span className="measure-range">min {formatMetric(measuredCost.min, "usd")} · max {formatMetric(measuredCost.max, "usd")}</span></>}<Link className="cost-note" href="/bench">Replay details →</Link></p></div>}
    <section className="report-section"><div className="section-heading"><h2>Follow a route</h2><span className="supporting-text">Inspect the prompt and aligned stability</span></div><div className="route-list">{data.report.routes.map(route => <Link key={route} href={`/report/${encodeURIComponent(id)}/heatmap/${encodeURIComponent(route)}`}><code>{route}</code><span>Open heatmap →</span></Link>)}</div></section>
    <section className="report-section"><h2>Findings</h2><p className="supporting-text">Ordered by potential recomputation. Estimates overlap and cannot be added as causal savings.</p><div className="table-scroll"><table><caption className="sr-only">Detected cache breakers and simulated downstream impact</caption><thead><tr><th>Breaker</th><th>Severity</th><th>Requests</th><th>Stable tokens after</th><th>Movement</th></tr></thead><tbody>{data.report.findings.map(f => <FindingRow key={f.id} finding={f} />)}</tbody></table></div>{!data.report.findings.length && <p className="notice">No breakers were detected in this run. Sampling and heuristics can miss variants.</p>}</section>
    <section className="action-panel"><div><h2>Turn findings into a fix task</h2><p>Export redacted requirements, preserve the recorded baseline, and verify the resulting code change.</p></div><div className="actions"><button className="button primary" onClick={createTask} disabled={source !== "API" || busy}>{busy ? "Preparing baseline…" : "Generate fix task"}</button><Link className="button" href="/fix">Saved fix status</Link></div>{source === "SAVED" && <p className="supporting-text">Task generation needs the local API and recorded helpdesk inputs.</p>}{taskError && <p role="alert" className="notice error">{taskError}</p>}</section>
    <Metadata data={data} />
  </>;
}

export function HeatmapWorkspace({ id, route }: { id: string; route: string }) {
  const { loaded, error } = useReport(id); const [full, setFull] = useState(false);
  const [after, setAfter] = useState<Loaded<CandidateView> | null>(null);
  const [afterStatus, setAfterStatus] = useState("loading");
  const [version, setVersion] = useState<"before" | "after">("before");
  const { loaded: bench } = useBench();
  useEffect(() => { if (!loaded) return; let active = true; candidate(id, loaded.data.report.input_sha256).then(value => { if (active) { setAfter(value); setAfterStatus(value ? "ready" : "unavailable"); } }).catch(() => { if (active) setAfterStatus("unavailable"); }); return () => { active = false; }; }, [id, loaded]);
  if (error) return <ErrorState message={error} />;
  if (!loaded) return <Loading />;
  const { data, source } = loaded; const shown = version === "after" && after ? after.data.report : data.report; const values = shown.heatmaps[route];
  if (!values) return <ErrorState message="This route is not part of the saved report." />;
  const { first, total, fraction } = prefixBoundary(shown, route);
  const preview = shown.template_preview[route] || "";
  const text = full ? preview : preview.slice(0, 12000);
  return <><Link className="back-link" href={`/report/${id}`}>← Report</Link><header className="report-header"><div><h1>Where the prefix breaks.</h1><p className="lede"><code>{route}</code></p></div><div className="badges"><Badge>{version === "after" && after ? after.source : source}</Badge><Badge>SIMULATED</Badge></div></header>
    <div className="heatmap-toolbar"><div className="segmented"><button aria-pressed={version === "before"} onClick={() => setVersion("before")}>BEFORE</button><button aria-pressed={version === "after"} disabled={!after} title={after ? after.source === "SAVED" ? "Read-only recorded AFTER run; current-source approval is separate" : "Current re-rendered candidate; approval is separate" : "No matching AFTER evidence is available"} onClick={() => setVersion("after")}>{after ? after.source === "SAVED" ? "AFTER · saved run" : "AFTER · current" : afterStatus === "loading" ? "Loading AFTER…" : "AFTER unavailable"}</button></div><div className="legend"><span><i className="legend-stable" />Reusable prefix</span><span><i className="legend-variable" />Variable</span><span><i className="legend-recomputed" />Recomputed</span></div></div>
    {after?.source === "SAVED" && <p className="saved-run-note">Saved AFTER replay · read-only. Current-source approval is separate. <Link href="/fix">Verification status →</Link></p>}
    {afterStatus === "unavailable" && <p className="supporting-text">No matching AFTER run is saved for this workload. Prepare and verify a candidate to compare it.</p>}
    <section className="heatmap-panel"><div className="section-heading"><h2>Prompt prefix</h2><Badge>SIMULATED</Badge></div>
      <p className="supporting-text">The probe moves along the prompt to its first recorded divergence.</p>
      <PrefixMap values={values} boundary={fraction} first={first} total={total} />
      <p className="supporting-text">Deep green: reusable prefix. Yellow: variation. Red: static content recomputed after the break. This scanner is SIMULATED.</p>
    </section>
    <HeatmapMetrics bench={bench?.data} report={shown} variant={version} />
    {version === "after" && after && <p className="supporting-text">{after.source} · {after.data.approval ? "Exact-diff approval recorded for this saved source." : "Unapproved candidate; visual reuse does not establish behavioral safety."} Recorded {after.data.metadata.timestamp}.</p>}
    <details className="report-section"><summary>Inspect the redacted prompt</summary><p className="supporting-text">Variable spans are marked. This text view is aligned structurally; its character positions are not token offsets.</p><pre className="prompt-view">{text.split(/(⟦[^⟧]*⟧)/g).map((part, i) => part.startsWith("⟦") ? <mark key={i}>{words(part)}</mark> : <span key={i}>{part}</span>)}</pre>{preview.length > 12000 && <button className="text-button" onClick={() => setFull(!full)}>{full ? "Collapse template" : "Show full redacted template"}</button>}</details>{version === "after" && after ? <details className="metadata"><summary>Candidate verification provenance</summary><dl><div><dt>Task</dt><dd><code>{after.data.task_id}</code></dd></div><div><dt>Source SHA-256</dt><dd><code>{after.data.metadata.source_sha256}</code></dd></div><div><dt>Candidate input SHA-256</dt><dd><code>{after.data.report.input_sha256}</code></dd></div><div><dt>Recorded</dt><dd>{after.data.metadata.timestamp}</dd></div></dl></details> : <Metadata data={data} />}
  </>;
}

export { FixWorkspace } from "./fix-workspace";

export function BenchWorkspace() {
  const { loaded, error } = useBench();
  if (error) return <ErrorState message={error} />;
  if (!loaded) return <Loading />;
  const smoke = loaded.data.smoke;
  return <><header className="report-header"><div><h1>Measured results.</h1><p className="lede">The same recorded requests, replayed before and after the change.</p></div><Badge>{loaded.source}</Badge></header><BenchmarkResults data={loaded.data} />{smoke && <details className="report-section"><summary>Serving smoke test</summary><Badge>MEASURED · SMOKE</Badge><p>{smoke.model} · {smoke.gpu} · vLLM {smoke.vllm_version}</p><div className="table-scroll"><table><caption>Observed token-counter changes after each synthetic request</caption><thead><tr><th>Request</th><th>Prompt tokens</th><th>Cache hits</th><th>Cache queries</th></tr></thead><tbody>{smoke.requests.map(r => <tr key={r.request}><td>{number(r.request)}</td><td>{number(r.prompt_tokens)}</td><td>{number(r.cached_tokens)}</td><td>{number(r.queried_tokens)}</td></tr>)}</tbody></table></div><p className="supporting-text">Counters count tokens; only whole blocks are reused. Profile: {number(smoke.block_size)} tokens per block, {number(smoke.capacity_tokens)} KV tokens. These are smoke-test observations, not a BEFORE/AFTER benchmark.</p><details className="metadata"><summary>Smoke run provenance</summary><dl><div><dt>Recorded</dt><dd>{smoke.timestamp}</dd></div><div><dt>Model revision</dt><dd><code>{smoke.revision}</code></dd></div><div><dt>Saved source</dt><dd><code>{smoke.source}</code></dd></div><div><dt>Artifact SHA-256</dt><dd><code>{smoke.sha256}</code></dd></div></dl></details></details>}</>;
}
