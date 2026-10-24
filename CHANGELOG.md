# Change log

## 2026-10-25T00:33:50+05:30 — Append the declared calendar facts in the helpdesk prompt tail

- Changed: the builder calls the pure calendar helper with the recorded clock,
  original message/history/retrieval and handbook comparison window. It appends
  the computed block after existing time/context only when date mentions exist.
  Original instructions, values, selected examples, roles, tools and settings
  remain present. No golden ID/date/expected answer is special-cased.
- Why: delegate calendar subtraction/comparison to deterministic code, after the
  original small model failed that arithmetic in both cache layouts.
- Verification: use a fresh explicit task with calendar_window_days=30. The saved
  preflight independently checks original traffic plus the fixed goldens; status
  and repository checks are recorded in source-bound eval_results artifacts.
  Actual fixed golden collection precedes another performance replay.
- Limitations: ISO calendar dates only, unverified source mentions, and no grant
  of return eligibility or authorization. All original AFTER assertions still
  gate approval; changed model outputs require human review. No new Devin session.

## 2026-10-25T00:32:34+05:30 — Add explicitly declared deterministic calendar arithmetic

- Authorization: Mohith approved expanding the task to fix the pre-existing date
  arithmetic exposed by both failed layouts. Keep the original fixed suite,
  expected answers, pinned model, temperature and generation budget unchanged.
- Added: a pure ISO calendar-date helper using only supplied text, recorded clock
  and a declared comparison window. It reports elapsed days, mathematical window
  comparisons, invalid/future dates and source fields. Date mentions stay labeled
  unverified; no entitlement or tool authorization is inferred.
- Verification: tasks opt in with --calendar-window-days. The verifier recomputes
  the exact permitted system block independently, checks originals in BOTH traffic
  and goldens, and rejects modified numbers, missing/duplicate/misplaced blocks or
  undeclared additions. The helper/verifier are outside the candidate's allowed
  source scope; no broad content exception or golden assertion was introduced.
- Validation: all 147 Python tests pass, including leap-day/boundary/future/invalid
  dates, explicit-clock validation, content rejection and golden-only enrichment
  cases. Ruff and CLI option/help checks pass. The public-snapshot checks still
  validate earlier artifacts. No inference or new Devin session in this commit.
- Next: prepare a fresh baseline with the declared window, wire the exact helper
  output into the prompt tail, then collect real quality first. Actual later
  outcomes belong to the saved run; no application fix is approved here.

## 2026-10-25T00:11:26+05:30 — Validate real current snapshots instead of demanding historical fixtures

- Fixed: the public-demo test asserted verification_current must always be false.
  A real current task export correctly set it true, causing one failure with 132
  other tests passing. Replace that historical-only expectation with typed task
  and candidate identity checks plus exact report/verification byte hashes.
  Ignored local task bundles are not required for a public checkout's test.
- Scope: no runtime content, quality, source-scope or approval gate changed.
  Production still rejects stale/tampered evidence. The original failing date
  outputs remain preserved; the timestamp-last layout remains unapproved.
- Operations: stopped the second warming allocation before it generated any
  golden request. Start a fresh baseline after this framework-only source change
  and reuse the documented model/inputs/settings. Actual later quality outcomes
  belong to the saved run, not a claimed pass in this entry.
- Validation: the focused public-snapshot test and all 133 Python tests pass;
  Ruff check and format pass. The saved current candidate exercises the positive
  snapshot path. No actual behavioral pass is claimed.

## 2026-10-25T00:07:19+05:30 — Preserve the failed date case and move existing time context last

- Observed: the first actual fixed suite passes four AFTER cases but fails the
  date/return-window schema: BEFORE and AFTER both answer true for a delivery
  34 days earlier against a 30-day rule. The initial candidate remains unapproved.
  All original output/measurement bytes are preserved under
  eval_results/attempts/pr2-v1/ and the original quality_guard run.
- Changed: move the existing Current time line to the end of system context,
  after examples/retrieval, to make the actual date salient beside the question.
  No rule, value, golden assertion, expected answer, seed or output budget changes.
- Validation: final current structural/test/quality outcomes are recorded in the
  source-bound verification artifacts. Collect the complete fixed suite first;
  a failed assertion cannot be waived by human review. A later performance run
  is collected only if all AFTER behavioral assertions and completion checks pass.
- Limitations: this is a bounded prompt-layout attempt, not a general fix for
  model arithmetic. If it fails, stop and discuss a broader application change.

## 2026-10-25T00:04:44+05:30 — Save paired live replay and collect the fixed behavioral suite

- Changed: recorded the real AFTER replay on the reviewed PR #2 builder, using
  the same original synthetic inputs, planned schedule, generation settings,
  pinned L4 profile and price as BEFORE. Three repetitions completed; immutable
  raw measurements, deployment profile and post-collection provenance are saved.
  The generated benchmark summary supplies all comparisons, including metrics
  that did not improve. This is sequential replay, not an open-loop load test.
- Evidence: eval_results/after_replay.json, after_replay.run.json and
  benchmark_summary.md. The actual application diff keeps the static handbook
  first, sorts tools and restores recorded history without changing goldens.
- Validation: combined candidate passes 133 tests and Ruff; current local content,
  scope, signature and prefix checks pass. Measured AFTER cache reuse median is
  80.622%. The saved run contains each repetition's prediction error.
- Quality: collect the unchanged five public synthetic BEFORE/AFTER cases on this
  same allocation at temperature zero. Actual outputs and independently evaluated
  outcomes are recorded only in eval_results/quality_guard/ and
  eval_results/current_fix_summary.md; this note does not claim a pass or review.
  Human output review and exact-diff approval remain separate gates.
- Provenance: these record-only CHANGELOG/AI_USAGE edits follow the completed
  benchmark and precede golden inference. The benchmark binds its earlier source;
  the quality artifact and final verification bind the later complete source.
  The prompt builder is identical. No second Devin session was started.

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
## 2026-10-24T23:29:40+05:30 — Restore history and integrate framework repairs in PR #2

- Changed: retain all recorded conversation messages in the prompt builder;
  keep static handbook first, deterministic tools and the original roles/content.
  Integrated current main's independent BEFORE fixtures and tokenizer dependency.
- Why: the original fixed window drops the early fact required by the fixed
  continuity golden. The verifier supports restoring original recorded history;
  the change still needs actual behavioral review.
- Validation: the combined candidate passes 131 Python tests plus Ruff check
  and format. Original failed preflight remains historical evidence; no actual
  golden or current authoritative verification pass is claimed.
- Limitations: actual golden evidence and human approval remain required. The
  configured context budget is enforced by analysis/collection; no history is
  silently truncated to make a request fit.


## 2026-10-24T23:17:02+05:30 — Reorder the helpdesk prompt builder for prefix reuse (unapproved)

- Changed: `demo_app/helpdesk/prompt.py` now puts the company support handbook first
  in the single system message, followed by the unchanged per-request block (current
  time, customer identity, locale, the three seeded sampled examples, retrieved
  context) in its original order; tools are sorted by name. Public signature,
  history window, roles, tool definitions and generation settings are unchanged.
  `before.py` stays frozen.
- Why: fix task 391115f6d51ca8741ea5fea8 (timestamp, user_identity,
  rag_before_static, few_shot_sampling high; tool_order low).
- Validation (local, recorded 27-request synthetic inputs, sha256 bc20d296...):
  `cachekit verify` SIMULATED vLLM hit rate 0.00304 -> 0.80851 (target 0.73165);
  no high-severity findings remain (four at medium, history_truncation low);
  content, scope, signature and prefix checks passed; Ruff passed.
- Not passing: `python3 -m pytest -q` reports 7 failed and 13 errors, 109 passed. The
  engine fix-workflow fixture (`engine/tests/fix_helpers.py`) copies the real
  `prompt.py` and requires it to reproduce BEFORE requests; it is outside this
  task's allowed files. Golden BEFORE/AFTER inference was not run, so quality
  evidence is missing and the fix is incomplete and unapproved.
- Limitations: simulation only; no measured latency or cost claim. Moving context
  into another message/role was not done; it would raise simulated reuse further
  but needs quality review.


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
