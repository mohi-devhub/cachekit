"""Deterministically format saved benchmark artifacts. No inference or network calls."""

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "engine"), str(ROOT)]

from cachekit.benchmark_models import BenchmarkRun, matched_replays  # noqa: E402


def main():
    directory = ROOT / "eval_results"
    old_path = directory / "before_replay.json"
    new_path = directory / "after_confirmation_replay.json"
    if not new_path.is_file():
        new_path = directory / "after_replay.json"
    before = BenchmarkRun.model_validate_json(old_path.read_bytes())
    after = BenchmarkRun.model_validate_json(new_path.read_bytes()) if new_path.is_file() else None
    matched = after is not None and matched_replays(before, after)
    rows = [
        ("Measured cache-hit rate", "measured_hit_rate", lambda v: f"{v * 100:.3f}%"),
        ("Simulated cache-hit rate", "simulated_hit_rate", lambda v: f"{v * 100:.3f}%"),
        ("Absolute prediction error", "absolute_hit_rate_error", lambda v: f"{v * 100:.3f} pp"),
        ("Client TTFT p50", "ttft_p50_s", lambda v: f"{v:.3f} s"),
        ("Client TTFT p95", "ttft_p95_s", lambda v: f"{v:.3f} s"),
        ("Request latency p50", "latency_p50_s", lambda v: f"{v:.3f} s"),
        ("Request latency p95", "latency_p95_s", lambda v: f"{v:.3f} s"),
        ("Completed requests / second", "throughput_requests_s", lambda v: f"{v:.3f}"),
        ("Allocated GPU-seconds / 1k", "allocated_gpu_seconds_per_1000", lambda v: f"{v:.2f}"),
        ("GPU-window USD / 1k", "gpu_window_usd_per_1000", lambda v: f"${v:.4f}"),
    ]

    def cell(run, key, format):
        value = run.summary.get(key) if run else None
        return (
            f"{format(value['median'])} ({format(value['min'])}–{format(value['max'])})"
            if value is not None
            else "<pending>"
        )

    text = [
        "# Saved measured replay results",
        "",
        "Generated only from the linked saved artifacts; "
        "median (min–max) across each run's repetitions.",
        "",
        "| Metric | BEFORE | AFTER |",
        "| --- | ---: | ---: |",
        f"| Requests per repetition | {before.n_requests} | "
        f"{after.n_requests if after else '<pending>'} |",
        f"| Repetitions | {len(before.runs)} | {len(after.runs) if after else '<pending>'} |",
    ]
    text += [
        f"| {label} | {cell(before, key, fmt)} | {cell(after, key, fmt)} |"
        for label, key, fmt in rows
    ]
    text += [
        "",
        "Matched inputs, planned schedule, settings, price and profile: "
        + ("yes." if matched else "not established; no paired speedup claim."),
        "",
    ]
    if matched:
        b = before.summary["ttft_p50_s"]["median"]
        a = after.summary["ttft_p50_s"]["median"]
        if b > 0:
            text.append(f"TTFT p50 change: {(a / b - 1) * 100:+.2f}% (negative means lower).")
        difference = (
            after.summary["measured_hit_rate"]["median"]
            - before.summary["measured_hit_rate"]["median"]
        )
        text.append(f"Measured cache reuse change: {difference * 100:+.3f} percentage points.")
    text += [
        "",
        "One request is in flight. Planned arrivals can wait at the client; TTFT/latency",
        "start at send time and exclude that queue delay. This is not an open-loop load test.",
        "GPU seconds are allocated replay-window wall time, not GPU utilization. GPU-only",
        "USD excludes startup, warmup/reset/idle, CPU, memory, storage and price modifiers.",
        "It is not a full invoice. Model quality and human exact-diff approval are separate.",
        "",
        "## Artifact identities",
        "",
    ]
    for path, run in [(old_path, before), (new_path, after)]:
        if run is None:
            continue
        lag = max(r.scheduling_delay_s for repeat in run.runs for r in repeat.requests)
        text += [
            f"- [{run.variant.upper()}]({path.name}): "
            f"SHA-256 `{hashlib.sha256(path.read_bytes()).hexdigest()}`.",
            f"  Source `{run.source_sha256}`; maximum client scheduling lag {lag:.3f} s.",
        ]
    (directory / "benchmark_summary.md").write_text("\n".join(text) + "\n")
    print("Formatted saved benchmark evidence; no new measurement was performed.")


if __name__ == "__main__":
    main()
