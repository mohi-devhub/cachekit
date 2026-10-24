# Actual UI captures

Captured from the running local production web app with the local API and saved
synthetic evidence. Desktop and mobile views were inspected; the Analyze action
also completed against the local deterministic engine. These captures show the
BEFORE report and measured baseline, with AFTER/quality still pending at capture
time. They establish rendered UI behavior, not approval of an application fix.

- [Measured baseline, desktop](benchmark-before-desktop.png)
- [Measured baseline, mobile](benchmark-before-mobile.png)
- [Synthetic report, desktop](report-before-desktop.png)
- [Synthetic report, mobile](report-before-mobile.png)

Generated captures do not enter source identity. UI and exporter code remain
audited; actual evaluation artifacts supply the displayed values.

The latest unapproved candidate is also captured from actual source-bound data:

- [Candidate AFTER heatmap](heatmap-after-desktop.png)
- [Blocked behavioral guard with actual outputs](fix-quality-blocked-desktop.png)

The date output is syntactically valid JSON but violates the fixed expected
schema: it marks a 34-day-old delivery as inside the 30-day window. Both BEFORE
and AFTER fail that case. Four other AFTER cases pass, and approval stays disabled.
[Saved diagnosis](../eval_results/date_quality_diagnosis.json) and
[current verification](../eval_results/current_fix_summary.md) contain the evidence.
