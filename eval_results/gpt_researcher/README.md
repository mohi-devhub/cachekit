# GPT Researcher controlled-input reorder experiment

**Behavior gate not passed; performance replay not collected; no approval.**

This executes selected real upstream request-construction functions with controlled inputs. It is not a full research-agent launch or production traffic.

Upstream commit: `5cdad9cb434754188b78bd998df18dd8d502cf7e`, Apache-2.0. [Three-line reorder patch](candidate.patch), [source/input hashes](experiment_manifest.json), [original license](UPSTREAM_LICENSE).

## What ran

- Eight fixed replay inputs and five behavior cases were declared before inference.
- The patch only moves the existing context/task block after the existing instructions. Rendered content, roles, values and paired generation settings are preserved.
- Actual BEFORE/AFTER quality generations used pinned Qwen3-4B/vLLM 0.31.0 on L4, temperature 0 and seed 42. Upstream temperature 0.35 was explicitly overridden.
- The initial 512-token attempt truncated all ten outputs and remains failed/incomplete.
- A separately recorded 2,048-token evaluation used identical candidate, cases and assertions. All ten outputs finished naturally. Facts/references, French and Markdown table pass; missing-data and untrusted-context checks fail in BOTH variants.
- The failed checks block a passing-fix claim. The performance stage was not run.
- Both allocations were stopped. Modal subsequently reported zero tasks and no containers.

## Evidence

- [Initial 512-token outputs/checks](behavior/quality.json).
- [Complete 2,048-token outputs/checks](extended_budget/behavior/quality.json).
- [Full BEFORE/AFTER review packet](review_packet.md).
- [Offline exact-match context inspection](offline_diagnosis.json).
- [Pinned deployment](extended_budget/deployment.json) and [frozen source manifest](extended_budget/source_manifest.json).
- Teardown: [first attempt](teardown.json), [extended budget](extended_budget/teardown.json).

## Limits and next decision

Percentage/marker presence is conservative and can flag a hypothetical example or rejection of a quoted instruction. Original failed artifacts are retained; these are not automatically proven behavioral regressions. Human review should also check unsupported elaboration and invented example.com URLs. No raw output is relabeled as approved.

This source was frozen in an isolated copy while the main UI changed concurrently. These checks do not approve the current checkout or the helpdesk candidate. Any future checker repair must retain the original failures, add meaningful negative cases and re-evaluate all saved outputs before requesting further measurement.

## Local analysis reports

- BEFORE: <http://localhost:3000/report/d506c32178c2e6d8166456bd0979e5c1ac391d4d04f76cebf5e4692158e2ee4e>
- AFTER candidate: <http://localhost:3000/report/600d24c1c05b2cc2711d4e2f12d83d4a38c38b95d5de5dee1b7f40bb75d889ed>

Both are available through the findings saved-report selector with the local API. Their cache reuse figures are SIMULATED; no latency or dollar result exists for this experiment.
