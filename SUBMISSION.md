# Project submission

Prepared for Devin Hacks Kochi. Submission deadline: **07:00 IST on Oct 25, 2026**; feature freeze: **05:30 IST**. Mohith will record the backup video and submit through the organizers’ announced method.

## Project

- **Project name:** cachekit
- **Short description:** A deterministic prompt-cache analyzer that diagnoses lost reuse, generates redacted source-refactoring tasks, and verifies candidate fixes with content checks and a required behavioral guard. Intended for developers running LLM applications.
- **Code repository URL:** https://github.com/mohi-devhub/cachekit
- **Final submitted implementation commit SHA:** Pending final implementation and publication. The final frozen implementation SHA will be recorded before submission.
- **Working demo URL or local demo steps:** Local CLI: after setup, `bash scripts/demo.sh`. API/UI: `bash scripts/run-api.sh` and `bash scripts/run-web.sh` in separate terminals. No hosted demo is claimed.
- **Demo access requirements:** Python, uv, Node.js and the pinned public tokenizer. Installation uses network access; ordinary synthetic analysis needs no credentials, GPU or external LLM.

## Participants

List participants according to the organizers' current participation format. Remove unused rows.

| Participant name | GitHub handle | Contribution |
| --- | --- | --- |
| Mohith | [mohi-devhub](https://github.com/mohi-devhub) | Solo builder; project direction and review. Implementation assistance documented in AI_USAGE.md. |

## Run and demonstrate

- **Prerequisites and versions:** Python requirement in `pyproject.toml` and `.python-version`; Node requirement in `web/package.json`; uv and npm.
- **Install command:** `bash scripts/setup.sh`.
- **Required environment variable names:** None for synthetic offline analysis. Optional fixer/deployment variables are listed as names only in `.env.example`; keep real values local.
- **Start command:** `bash scripts/demo.sh` for the implemented CLI workflow; API and web start scripts above open the analysis/report workspace.
- **Demo walkthrough:** Generate fictional BEFORE traffic, render with the pinned local Qwen tokenizer, open the saved SIMULATED report and route heatmap in the UI, prepare a redacted fix task through the local API, and run verification. Compare the saved BEFORE/AFTER heatmap and five actual golden outputs, inspect the measured replay with repetition ranges, and review source-bound verification. Missing/stale quality evidence leaves a candidate unapproved.
- **Checks performed and results:** Full local Python suite, Ruff, real-tokenizer offline/reproducibility tests and CLI wheel build passed during implementation. Run scripts have been syntax checked; API HTTP contract tests and the web production build passed; local API/UI launching, Analyze behavior and desktop/mobile browser views have been checked. Re-run `bash scripts/check.sh` in the configured participant environment.
- **Screenshots:** [Actual desktop/mobile UI captures](screenshots/README.md). No mock screenshot is presented as an implemented interface.
- **Known limitations or incomplete features:** Current source/approval status is in [the verification record](eval_results/current_fix_summary.md). The five-case guard is bounded evidence, not universal equivalence. The explicit confirmation restoration is an authorized semantic change. Measured BEFORE/AFTER replay applies to its recorded sources; the saved confirmation-repair run includes that instruction; the UI shows measurements only for matching rendered request bytes. Analysis cache rates are SIMULATED. Replay is sequential; GPU-window cost is narrower than the full bill. Final freeze, video and submission remain pending.
- **Libraries and APIs:** Python/uv, Pydantic, Typer, FastAPI, pytest/Ruff, Transformers/tokenizers, httpx/jsonschema, Next.js/React/Tailwind, pinned GSAP/Lenis and self-hosted Fontsource fonts; one React Bits fade adaptation ([sources/licenses](web/THIRD_PARTY_NOTICES.md)); [vLLM](https://github.com/vllm-project/vllm) and [Modal](https://modal.com/) for the selected serving profile; [Devin API](https://docs.devin.ai/api-reference/overview) one real capped session opened PR #2; the local API never starts a session.
- **Public datasets:** [SWE-agent trajectories](https://huggingface.co/datasets/nebius/SWE-agent-trajectories) (CC BY 4.0; respect upstream/model terms), [Glaive function calling](https://huggingface.co/datasets/glaiveai/glaive-function-calling-v2) (Apache-2.0), and [WildChat](https://huggingface.co/datasets/allenai/WildChat-1M) (ODC-BY). Only SWE-agent/Glaive conversion is implemented so far; downloads/raw data and dataset-derived previews remain local. Public demo evidence uses fictional synthetic inputs.
- **AI usage record:** [AI_USAGE.md](AI_USAGE.md)
- **Development change log:** [CHANGELOG.md](CHANGELOG.md)

## Submission checklist

- [ ] The project follows the organizers' current project-start and eligibility instructions.
- [ ] The participation format follows the organizers' current instructions.
- [x] Actual AI assistance is documented; no particular tool or provider is required.
- [x] The code repository URL, short description, and local demo steps are provided.
- [ ] README setup and demo instructions match the submitted code.
- [x] Actual checks and known limitations are documented.
- [ ] Meaningful changes are documented and committed throughout development.
- [ ] The final implementation is committed and pushed, and its SHA is recorded above.
- [ ] No credentials or private data are included in the repository or demo instructions.
- [ ] The organizers' announced submission method and timing have been followed.

Event: **Devin Hacks Kochi**. Submission is due by 07:00 IST; follow the organizers' announced submission method. No particular template or AI provider is required. Pending checklist items are not asserted as complete.
