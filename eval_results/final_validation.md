# Final candidate evidence checkpoint

Recorded 2026-10-25T01:36:30+05:30. Task `1733e486db3c2fd68eff119b`.

- Complete implementation source: `c988685ccc5ec3ed637a4b384df94a8d51886492df7e3b766a7c030ab16bc27b`.
- Exact task diff: `4b688cd47b6f8f56733c90c10ceb4b2b69b5db48eda7aa30c55e3f00de76961d`.
- Source-bound content (27 traffic + 5 goldens), scope, signature, prefix and repository-test gates pass. The preflight ran all 147 Python tests; its actual output checksum remains in current_fix_verify.json. Ruff and the production web typecheck/lint/build also passed before collection.
- Actual fresh five-case BEFORE/AFTER collection: all AFTER assertions, required schema and completion checks pass. All five outputs changed. No human review or exact-diff approval is recorded; overall verification correctly remains false with `review_required`.
- Immutable paired measured replay uses 27 requests in each of three repetitions. See benchmark_summary.md for generated numbers and measurement limits. current_benchmark_binding.json proves identical rendered traffic and prompt-producing components at this current source; fresh quality separately binds the complete source. The older measured source identity is preserved.
- Final synthetic snapshot export passed its focused typed identity/byte-hash regression test after the new outputs were attached (1 passed).
- Actual UI inspected: measured table, current AFTER heatmap, five-case guard and disabled approval. Desktop table and 390-pixel mobile benchmark fit. Narrow fix-page long hash overflows; this cosmetic limitation is recorded in screenshots/README.md.
- Saved fallback checked by blocking only the browser's local API requests. Actual saved five-case checks remain visible and verification/approval writes stay disabled. Browser API access restored afterward.
- Modal confirmed the final allocation stopped at 01:32:11 IST with zero tasks. No extra Devin session was created for the calendar work or final collection.

[Changed outputs for human review](quality_review_packet.md), [verification](current_fix_verify.json), [run provenance](current_fix_verify.run.json), [screenshots](../screenshots/README.md).

This is a data-only checkpoint. It does not alter audited implementation files or claim human approval.
