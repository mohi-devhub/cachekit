"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { CopyHash } from "./copy-hash";
import { api, fix, words, type Loaded, type TaskView, type Verification } from "@/lib/workspace";
function Badge({ children, tone = "neutral" }: { children: React.ReactNode; tone?: string }) { return <span className={`badge ${tone}`}>{children}</span>; }
function Loading() { return <p role="status">Loading saved evidence…</p>; }
function ErrorState({ message }: { message: string }) { return <p role="alert" className="notice error">{message}</p>; }

export function FixWorkspace({ id }: { id?: string }) {
  const [loaded, setLoaded] = useState<Loaded<TaskView>>(); const [error, setError] = useState("");
  const [busy, setBusy] = useState(false); const [verificationId, setVerificationId] = useState("");
  const [qualityId, setQualityId] = useState(""); const [reviews, setReviews] = useState("");
  const [reviewer, setReviewer] = useState(""); const [confirmation, setConfirmation] = useState(""); const [approved, setApproved] = useState(false);
  useEffect(() => { let active = true; fix(id).then(data => { if (active) setLoaded(data); }).catch(e => { if (active) setError(e.message); }); return () => { active = false; }; }, [id]);
  if (!loaded) return error ? <ErrorState message={error} /> : <Loading />;
  const view = loaded.data; const v = view.verification;
  const hasApproval = approved || Boolean(view.approval && view.verification_current);
  const canApprove = !hasApproval && loaded.source === "API" && view.verification_current && v?.passed && v.quality_guard.status === "passed" && !!verificationId;
  async function verify() { if (!loaded) return; setBusy(true); setError(""); try {
    const response = await api<{ id: string; result: Verification }>("/verify", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ task_id: loaded.data.task.id, quality_run_id: qualityId.trim() || null, review_ids: reviews.trim().split(/\s+/).filter(Boolean) }) }, 180000);
    setVerificationId(response.id); setApproved(false);
    const current = await api<TaskView>(`/fix/${loaded.data.task.id}`, {}, 15000);
    setLoaded({ source: "API", data: current });
  } catch (e) { setError(e instanceof Error ? e.message : "Verification failed."); } finally { setBusy(false); } }
  async function approve() { if (!loaded || !v) return; setBusy(true); setError(""); try {
    const recorded = await api<NonNullable<TaskView["approval"]>>("/approve", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ task_id: view.task.id, verification_id: verificationId, diff_sha256: confirmation, reviewer, review_ids: reviews.trim().split(/\s+/).filter(Boolean) }) }, 180000); setLoaded({ source: "API", data: { ...view, approval: recorded } }); setApproved(true);
  } catch (e) { setError(e instanceof Error ? e.message : "Approval failed."); } finally { setBusy(false); } }
  function download() { const url = URL.createObjectURL(new Blob([view.markdown], { type: "text/markdown" })); const a = document.createElement("a"); a.href = url; a.download = "fix_task.md"; a.click(); URL.revokeObjectURL(url); }
  return <><Link href="/report/demo-before" className="back-link">← Findings</Link>
    <header className="report-header"><div><h1>Fix and verify.</h1><p className="lede">A scoped code change, checked against the same inputs and expected behavior.</p></div><Badge>{loaded.source}</Badge></header>
    <p className="notice">{loaded.source === "SAVED" ? "Saved demo evidence. These checks belong to the recorded source; they do not verify this checkout." : view.state === "stale" ? "Source changed since this recorded run. Its results are historical; verify the final source before approving a new change." : view.note}</p>
    <section className="report-section"><div className="section-heading"><h2>Fix task and pull request</h2><Badge>{view.handoff?.status || "NOT STARTED"}</Badge></div><p>Give your coding agent the redacted findings and constraints. Raw request logs stay out of the handoff.</p><div className="actions">{view.handoff?.pr_url && <a className="button primary" href={view.handoff.pr_url} target="_blank" rel="noopener noreferrer">View Devin PR</a>}<button className="button" onClick={download}>Download fix task</button></div><details className="task-document"><summary>Read the redacted task</summary><pre>{view.markdown}</pre></details></section>
    <section className="report-section"><h2>What verification checked</h2><div className="gate-list">{[
      ["Prompt content preserved", v?.content_check?.passed], ["Cache reuse target met", v?.prefix_check.passed], ["Project tests passed", v ? v.tests.status === "passed" : undefined],
    ].map(([label, passed]) => <div key={String(label)}><span>{label}</span><Badge tone={view.verification_current && passed ? "good" : "neutral"}>{passed === undefined ? "NOT RUN" : passed ? view.verification_current ? "PASS" : "RECORDED PASS" : "NOT PASSED"}</Badge></div>)}</div></section>
    <section className="report-section"><div className="section-heading"><h2>Did the behavior stay correct?</h2><Badge>{words(v?.quality_guard.status || "not_run")}{!view.verification_current && v ? " · recorded" : ""}</Badge></div><p>Check the response, not just the cache hit. Open a case to inspect the actual BEFORE and AFTER answers.</p><div className="golden-list">{view.golden_cases.map(c => {
      const result = v?.quality_guard.cases.find(r => r.id === c.id);
      const output = view.quality_outputs?.find(o => o.id === c.id);
      const passed = result && Object.values(result.after_assertions).every(Boolean) && result.json_after_valid !== false && !result.truncated;
      return <details className="golden-case" key={c.id}><summary>{words(c.category)} <Badge>{!result ? "NOT RUN" : passed ? view.verification_current ? "CHECKS PASS" : "RECORDED PASS" : "CHECK FAILED"}</Badge></summary><p className="supporting-text">{c.assertions.map(a => a.replaceAll("-", " ")).join(" · ")}</p>{result && <p className="supporting-text">{result.exact_match ? "Exact output match" : result.reviewed ? "Changed output reviewed" : "Changed output requires review"} · JSON {result.json_after_valid === null ? "not applicable" : result.json_after_valid ? "valid" : "invalid"}</p>}{output && <><h4>BEFORE</h4><pre className="prompt-view">{output.before.text}</pre><h4>AFTER</h4><pre className="prompt-view">{output.after.text}</pre></>}</details>;
    })}</div><p className="supporting-text">These fixed cases support the tested behaviors; they do not prove universal equivalence.</p></section>
    <details className="metadata"><summary>Advanced: run verification and record approval</summary>
      <p>For the local workflow. Verification reads existing quality evidence and runs the configured project tests; it does not start model inference or a Devin session.</p>
      <label htmlFor="quality-id">Quality run SHA-256 (optional)</label><input id="quality-id" value={qualityId} onChange={e => { setQualityId(e.target.value); setVerificationId(""); }} disabled={loaded.source !== "API" || busy} spellCheck={false} />
      <label htmlFor="review-ids">Review artifact identities (space separated)</label><input id="review-ids" value={reviews} onChange={e => { setReviews(e.target.value); setVerificationId(""); }} disabled={loaded.source !== "API" || busy} spellCheck={false} />
      <button className="button" onClick={verify} disabled={loaded.source !== "API" || busy || view.state === "stale"}>{busy ? "Checking…" : "Run local verification"}</button>
      <div className="gate-list"><div><span>Allowed source scope</span><Badge>{v?.scope_check.passed ? "Recorded pass" : "Not passed"}</Badge></div><div><span>Public signature</span><Badge>{v?.signature_check.passed ? "Recorded pass" : "Not passed"}</Badge></div></div>
      <h3>Approve the exact verified diff</h3><p>{hasApproval ? "An approval is recorded for this verified diff." : canApprove ? "Review the changes, enter your name and confirm the complete diff hash." : "Approval requires current verification and passing behavioral evidence."}</p><CopyHash value={v?.diff_sha256} />
      <label htmlFor="reviewer">Reviewer name</label><input id="reviewer" disabled={!canApprove || busy} value={reviewer} onChange={e => setReviewer(e.target.value)} />
      <label htmlFor="diff-confirm">Confirm diff SHA-256</label><input id="diff-confirm" disabled={!canApprove || busy} value={confirmation} onChange={e => setConfirmation(e.target.value)} />
      <button className="button primary" disabled={!canApprove || busy || !reviewer.trim() || confirmation !== v?.diff_sha256 || hasApproval} onClick={approve}>{hasApproval ? "Approval recorded" : "Record approval"}</button><p className="supporting-text">Recording approval does not merge the PR. Missing, stale or failed evidence stays blocked.</p>
    </details>{error && <p className="notice error" role="alert">{error}</p>}
  </>;
}
