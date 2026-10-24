# UI regression found before publication

The actual capture showed an AFTER heatmap with the BEFORE median text still
visible, while its min/max already came from AFTER. The cards were below the
viewport when toggled. A layout-effect cleanup wrote the old value after React's
update, and IntersectionObserver had not yet started the next transition.

The fix sets the actual saved target immediately for each new view and cancels
motion without writing old text during cleanup. The fixed check compares every
visual median (including off-screen cards) against its matching saved run, then
repeats toggles with networking disabled and reduced motion. Final outcomes are
recorded in eval_results/setup/step3_browser.json. This capture is failure evidence,
not the current UI or a performance claim.
