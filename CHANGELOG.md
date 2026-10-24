# Change log

## 2026-10-24T23:53:51+05:30 — Connect real replay and candidate evidence to the UI

- Changed: shared pure benchmark contracts power the read-only API, real replay
  table and deterministic saved-results formatter. Paired status requires the
  same original inputs, schedule, settings, price and serving profile. Missing or
  mismatched runs stay explicit; GPU-window costs exclude the rest of the bill.
- Changed: AFTER heatmaps require a current-source candidate with checksum-bound
  report/verification provenance. The fix page displays actual public synthetic
  golden outputs and preserves the identity of a referenced original Devin task.
  Export can select a registered current task; stale network fallbacks are labeled.
- Evidence: saved real BEFORE benchmark is exported; actual desktop/mobile report
  and benchmark captures are in screenshots/. Browser Analyze completed against
  the local engine. Root generated captures are excluded from code identity;
  exporter/UI source and tests remain audited. README includes the architecture.
- Validation: all 133 Python tests passed, including stale/tampered candidate,
  golden-output identity and paired-run cases. Ruff, web typecheck, lint and
  production build passed. No mock measurements were published.
- Review: PR #2 was updated normally at 4979634, with all recorded history kept;
  its combined candidate passes 131 tests and Ruff. Human review is pending. The
  next live AFTER/golden collection requires a fresh baseline after these source
  changes. This milestone starts no new Devin session and claims no quality pass.

## 2026-10-24T23:27:29+05:30 — Repair verification fixtures exposed by the actual fixer PR

- Changed: isolated test repos now initialize the prompt target from frozen
  `before.py`, independently of the live app's candidate. Added a regression
  case with a deliberately unusable live builder to verify this separation.
  Declared Jinja2 in the tokenizer extra; its requirement is present in the built
  engine wheel. Exported public demo JSON is treated as generated evaluation
  data, while its exporter and UI source remain audited.
- Why: PR #2's source/content/prefix checks passed, but fixture setup incorrectly
  required every fixed live builder to remain equal to BEFORE. Public demo
  export must not itself invalidate the source-bound checks it displays.
- Validation: reproduced the original PR's failed verification in an isolated
  exact-source copy (`eval_results/pr2_preflight.*`). With these framework fixes,
  that candidate passes 131 Python tests. Root focused workflow tests and Ruff
  pass; engine wheel built and its Jinja2 extra inspected. No production gate or
  golden assertion was removed or weakened.
- Limitations: a fresh baseline is required after the framework change. The
  original PR still truncates history and has no actual golden inference; it is
  not approved or merged. One Devin session was used with a one-ACU creation cap;
  creation/handoff evidence is sanitized and contains no raw request logs.


## 2026-10-24T23:09:55+05:30 — Save actual BEFORE replay and fix startup/teardown behavior

- Changed: saved the real synthetic BEFORE benchmark and live deployment profile,
  plus checksum-bound dataset/seed provenance. Added a baseline-only README table.
  Kept original measurement bytes immutable and saved no prompt/answer text.
- Observed: all three repetitions completed; measured token-cache reuse matched
  the sequential simulator for this traffic/profile. TTFT excludes client queue
  delay; the saved scheduling lag is disclosed, not described as open-loop load.
- Fixed: startup readiness now uses bounded backoff. Earlier frequent 503 health
  probes appeared as dashboard errors during model startup; inference proceeded
  only after readiness. Non-interactive teardown uses `modal app stop --yes`;
  the initial stop lacked that flag and was retried successfully by app ID.
- Validation: actual stream/usage/cache/reset/source checks passed during the run;
  benchmark schema and dataset/input hashes verified afterward. All 21 focused
  benchmark tests and Ruff passed after the backoff change; the full harness
  suite previously passed 129 tests. Modal confirms stopped with zero tasks.
- Limitations: BEFORE-only; no application fix, AFTER performance or quality pass
  is claimed. GPU-window cost remains narrower than the complete Modal invoice.


## 2026-10-24T22:54:51+05:30 — Implement the MUST measurement harness

- Changed: added strict token-counter/config parsing, streaming completion
  timing/usage checks, scheduled sequential replay, warmup/reset/settling,
  repetition summaries and immutable source-bound artifacts in `bench/`.
  Added pinned single-L4 Modal serving with a benchmark-route allowlist.
  Quality inference now accepts Modal's documented `.modal.direct` hostnames.
- Why: collect real E2/E3 evidence independently of the deterministic engine,
  reject invalid/contaminated runs, and make GPU teardown reproducible.
- Pricing: verified the base L4 rate against Modal's current pricing page;
  GPU-window estimates explicitly exclude startup/idle, CPU/memory and other
  charges. Existing analysis cost fields remain unset.
- Validation: full suite passed 129 tests, including 21 benchmark protocol,
  accounting and readiness cases; CLI help and Ruff checks passed. Modal
  definition imports with the installed SDK without starting a deployment.
- Limitations: no actual benchmark or golden inference is claimed by this
  implementation commit. Dedicated-server use is an operator assertion;
  revision/GPU identity comes from the pinned deployment manifest. Concurrency
  and generated-token cache pressure are outside the simulator's model.


## 2026-10-24T22:39:55+05:30 — Resolve PR #1 against the implemented project

- Changed: integrated corrected Devin Hack Kochi guidance and optional AI-tool
  wording across the seven documentation files in PR #1. Preserved the cachekit
  README, setup/demo commands, submission details, changelog and AI usage history.
- Why: PR #1 started from the old template and conflicts with newer project docs.
  No particular template or AI provider is an event requirement.
- Validation: reviewed exact downloaded PR head d361d19d50d6589966e349804d0654730e3b7940; checked local Markdown
  links, whitespace and preservation of all application files. Current main had
  passed 108 Python tests before this documentation-only resolution; those tests
  are not a new runtime claim for the PR.
- Limitations: remote publication must succeed before the PR is conflict-free
  on GitHub. No application behavior or quality-approval state is changed.

## 2026-10-24T21:53:05+05:30 — Correct Devin Hack Kochi event guidance

- Changed: corrected the current event name and AI tool guidance in `.github/pull_request_template.md`, `AGENTS.md`, `AI_USAGE.md`, `CHANGELOG.md`, `README.md`, `RULES.md`, `SUBMISSION.md`.
- Why: the organizer shared an older event template; Devin Hack Kochi has no
  major AI usage constraints and the template must not require a particular AI provider.
- Scope: preserved project implementation and historical assistance records.
- Removed obsolete template logistics, participation limits, and credit promises; current organizer instructions remain authoritative.
- Validation: reviewed documentation diffs, checked whitespace with `git diff --check`, and checked local Markdown links for new breakage.
- Limitations: maintainer review is pending; application tests were not run for this documentation-only correction.

Record each meaningful project change during the event, newest first. Update this file in the same commit as the change. Use a real timestamp with timezone, for example `YYYY-MM-DDTHH:MM:SS+05:30`.

## Event build log

### 2026-10-24T22:32:02+05:30 — feat: connect local analysis and verification to the report workspace

- Changed: Added bounded local API ingestion, saved report identities/provenance,
  redacted task creation, source freshness, offline verification and exact-diff
  approval. Connected Analyze, Report, Heatmap, Fix and Bench UI routes; exported
  only reviewed synthetic evidence for API-free demo mode. Updated README,
  submission notes, web instructions and screenshot status.
- Why: Make the existing deterministic engine and fail-closed quality workflow
  reviewable through one local workspace, with explicit SIMULATED/MEASURED labels.
- Affected: `engine/cachekit/api*`, workspace persistence, CLI approval helper,
  report heatmap metadata, `web/src/`, public synthetic snapshot and exporter.
  Private uploads/results remain ignored; optional private planning is no longer
  required to generate a fix task from a public checkout.
- Validation: 108 Python tests passed, including 10 API/evidence cases; Ruff passed;
  web typecheck, ESLint and production build passed. Regenerated the actual local
  synthetic report and checked exported values against saved evidence. UI source
  detector warning corrected; diff whitespace and exporter syntax checked.
- Limitations: Browser screenshots/visual validation are unverified because both
  API and Next server binds are denied (EPERM) in this sandbox. No actual fixer
  PR, golden inference, BEFORE/AFTER benchmark, cost or speedup is claimed. The
  historical fix task is stale and unapproved. Publication is recorded separately
  after a successful commit/push; no shared history is rewritten. Staging here
  failed because .git/index.lock creation is denied. A reviewed local incremental
  publisher is prepared for normal Terminal execution.


### 2026-10-24T22:11:13+05:30 — chore: add run scripts and reviewed submission evidence

- Changed: Publish this logical source checkpoint on top of the organizer template.
- Why: Record previously local work with honest current commit timestamps.
- Validation: Public-file allowlist, credential patterns and preserved organizer bytes
  checked before staging; code checks for the complete local workspace are recorded above.
- Limitations: This is a publication checkpoint, not a backdated development record;
  actual fixer/quality/benchmark completion and final screenshots remain pending.


### 2026-10-24T22:11:13+05:30 — feat: scaffold the cachekit web interface

- Changed: Publish this logical source checkpoint on top of the organizer template.
- Why: Record previously local work with honest current commit timestamps.
- Validation: Public-file allowlist, credential patterns and preserved organizer bytes
  checked before staging; code checks for the complete local workspace are recorded above.
- Limitations: This is a publication checkpoint, not a backdated development record;
  actual fixer/quality/benchmark completion and final screenshots remain pending.


### 2026-10-24T22:11:12+05:30 — feat: add fixer handoff and source-bound behavioral verification

- Changed: Publish this logical source checkpoint on top of the organizer template.
- Why: Record previously local work with honest current commit timestamps.
- Validation: Public-file allowlist, credential patterns and preserved organizer bytes
  checked before staging; code checks for the complete local workspace are recorded above.
- Limitations: This is a publication checkpoint, not a backdated development record;
  actual fixer/quality/benchmark completion and final screenshots remain pending.


### 2026-10-24T22:11:12+05:30 — feat: define redacted fix tasks and fail-closed verification gates

- Changed: Publish this logical source checkpoint on top of the organizer template.
- Why: Record previously local work with honest current commit timestamps.
- Validation: Public-file allowlist, credential patterns and preserved organizer bytes
  checked before staging; code checks for the complete local workspace are recorded above.
- Limitations: This is a publication checkpoint, not a backdated development record;
  actual fixer/quality/benchmark completion and final screenshots remain pending.


### 2026-10-24T22:11:12+05:30 — feat: implement offline cache analysis and vLLM simulation

- Changed: Publish this logical source checkpoint on top of the organizer template.
- Why: Record previously local work with honest current commit timestamps.
- Validation: Public-file allowlist, credential patterns and preserved organizer bytes
  checked before staging; code checks for the complete local workspace are recorded above.
- Limitations: This is a publication checkpoint, not a backdated development record;
  actual fixer/quality/benchmark completion and final screenshots remain pending.


### 2026-10-24T22:11:11+05:30 — feat: scaffold Python contracts and reproducible helpdesk fixtures

- Changed: Publish this logical source checkpoint on top of the organizer template.
- Why: Record previously local work with honest current commit timestamps.
- Validation: Public-file allowlist, credential patterns and preserved organizer bytes
  checked before staging; code checks for the complete local workspace are recorded above.
- Limitations: This is a publication checkpoint, not a backdated development record;
  actual fixer/quality/benchmark completion and final screenshots remain pending.


Entries below are retrospective records written at the displayed time. Earlier
implementation was not committed from the coding sandbox because Git metadata
writes were denied. Commit timestamps will reflect actual publication time;
the event timeline is not backdated or reconstructed.

### 2026-10-24T21:54:46+05:30 — Prepare template-preserving publication

- Changed: Restored organizer files from the repository's existing initial commit;
  retained private CacheKit notes under ignored local storage; added run scripts,
  submission details and an honest screenshot status.
- Why: Build on the participant template's history and provide reproducible entry
  points while keeping credentials, raw data and private planning out of Git.
- Validation: Organizer file paths and original contents inspected from
  `origin/main`; shell syntax checked for all run scripts. The implemented engine
  and fix workflow passed the full local Python suite (98 tests) and Ruff.
  Isolated publication-prefix checks passed: foundation tests; analysis tests
  with exact-tokenizer integration skipped because private tokenizer data is not
  included in a public checkpoint. Public allowlist and credential checks passed;
  organizer instructions/rules/checklist match the existing template bytes.
- Limitations: Publication is pending. The API and UI are foundations, no actual
  fixer PR or golden inference exists, and UI screenshots remain pending.

## Template setup — 10 October 2026

- Changed: Added the event README, rules, agent guide, change log, AI usage record, submission checklist, Git ignore rules, and pull request checklist.
- Why: Give participants a consistent starting point for event rules, basic coding patterns, documented changes, and regular commits.
- Validation: Checked local Markdown links, event detail consistency, required documents, and diff whitespace before publishing.
- Limitations: Documentation scaffolding only; no participant project, application, or working demo is included. GitHub publication and template status are verified separately after creation.
