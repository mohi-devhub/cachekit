"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { reportOptions, type ReportSummary } from "@/lib/report-selection";
import { api, type ReportBundle } from "@/lib/workspace";

export function ReportSwitcher({ id, bundle }: { id: string; bundle?: ReportBundle }) {
  const router = useRouter();
  const [list, setList] = useState<{ reports?: ReportSummary[]; error?: string }>({});
  useEffect(() => {
    let active = true;
    api<ReportSummary[]>("/reports").then(reports => {
      if (active) setList({ reports });
    }).catch(() => {
      if (active) setList({ error: "Local report list unavailable. Reconnect the API and reload to discover local reports. The helpdesk demo is available offline." });
    });
    return () => { active = false; };
  }, [id]);

  return <section aria-label="Report selection">
    <label htmlFor="findings-report">Saved report</label>
    <select id="findings-report" value={id} aria-describedby="report-list-status"
      onChange={event => router.push(`/report/${encodeURIComponent(event.target.value)}`)}>
      {reportOptions(list.reports || [], id, bundle).map(option => <option key={option.id} value={option.id}>{option.label}</option>)}
    </select>
    <p id="report-list-status" className="supporting-text" role="status">{list.error || (list.reports
      ? "Select a report to inspect its findings and routes. Local reports require the API."
      : "Checking saved local reports…")}</p>
    {bundle && <p className="supporting-text">Dataset: {bundle.metadata.dataset.join(" · ") || "Unrecorded"}</p>}
  </section>;
}
