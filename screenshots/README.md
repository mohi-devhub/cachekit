# Actual UI captures

Captured from the running local production web app using actual saved public
synthetic evidence. Screenshots establish rendered behavior; human approval is
separate. They contain no private dataset logs.

## Current candidate and measured replay

- [Paired sequential replay, desktop](benchmark-paired-desktop.png)
- [Paired sequential replay, mobile](benchmark-paired-mobile.png)
- [Current candidate AFTER heatmap](heatmap-after-desktop.png)
- [Five passing case checks, human review required](fix-quality-review-required-desktop.png)

The time comparison now correctly marks the 34-day-old delivery outside the
30-day window. All five AFTER assertions, required schema and completion checks
pass. Changed outputs await human review, so the application fix remains
unapproved. See the [actual output review packet](../eval_results/quality_review_packet.md),
[current verification](../eval_results/current_fix_summary.md) and
[measured run summary](../eval_results/benchmark_summary.md).

The measured table fits desktop and a 390-pixel mobile viewport. A known cosmetic
limitation remains on the narrow fix page: its long exact-diff hash overflows the
viewport. The saved fix page was checked with API requests blocked: actual saved case checks
remain visible and write actions stay disabled. API access was then restored.

## Earlier captures

These preserve what the UI showed before the final candidate:

- [Measured baseline, desktop](benchmark-before-desktop.png)
- [Measured baseline, mobile](benchmark-before-mobile.png)
- [Synthetic BEFORE report, desktop](report-before-desktop.png)
- [Synthetic BEFORE report, mobile](report-before-mobile.png)
- [Earlier candidate blocked by the date guard](fix-quality-blocked-desktop.png)

The blocked capture shows an earlier real failed attempt: both sides returned
an incorrect within-window value. It is historical failure evidence and does
not describe the final candidate. All original raw attempts remain saved.

Generated captures do not enter source identity. UI and exporter code remain
audited; actual evaluation artifacts supply displayed values.
