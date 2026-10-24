# Actual UI captures

The current captures come from the running production web app with the local API
and external services blocked. They show saved public synthetic evidence, never
private logs or generated mock screens. Capture identity, viewport checks and
offline/reduced-motion results are recorded in
[the browser check](../eval_results/setup/step3_browser.json).

| Surface | Desktop | Mobile |
| --- | --- | --- |
| Overview | [Open](overview-desktop.png) | [Open](overview-mobile.png) |
| Findings | [Open](findings-desktop.png) | [Open](findings-mobile.png) |
| Heatmap BEFORE | [Open](heatmap-before-polished-desktop.png) | [Open](heatmap-before-polished-mobile.png) |
| Heatmap AFTER | [Open](heatmap-after-polished-desktop.png) | [Open](heatmap-after-polished-mobile.png) |
| Fix / verify | [Open](fix-verify-desktop.png) | [Open](fix-verify-mobile.png) |
| Benchmarks | [Open](bench-desktop.png) | [Open](bench-mobile.png) |

The heatmap grid and marker are SIMULATED from saved aligned bins and the earliest
divergence finding. The cards below it are MEASURED only for matching request bytes;
latency and dollar values are not inferred from token colors. Saved approval belongs
to its recorded source, and offline write actions remain disabled.

Earlier files in this folder retain previous interfaces and blocked/review-required
states. They are historical captures, not the current status. Original failed runs
remain in eval_results/attempts. Generated screenshots do not enter source identity;
UI/exporter code stays audited. Final frozen-source checks are recorded separately.
