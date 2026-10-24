"""Offline comparison of two saved replay artifacts. No inference or network calls."""

import hashlib
from collections.abc import Callable
from pathlib import Path
from statistics import median
from typing import Annotated

import typer
from pydantic import ValidationError

from cachekit.benchmark_models import BenchmarkRun, ReplayMeasurement, matched_replays

METRICS: list[tuple[str, str, Callable[[float], str]]] = [
    ("Measured cache-hit rate", "measured_hit_rate", lambda v: f"{v * 100:.3f}%"),
    ("Client TTFT p50", "ttft_p50_s", lambda v: f"{v:.3f} s"),
    ("Client TTFT p95", "ttft_p95_s", lambda v: f"{v:.3f} s"),
    ("Request latency p50", "latency_p50_s", lambda v: f"{v:.3f} s"),
    ("Request latency p95", "latency_p95_s", lambda v: f"{v:.3f} s"),
    ("GPU-window USD / 1k requests", "gpu_window_usd_per_1000", lambda v: f"${v:.4f}"),
]

LIMITATIONS = [
    "Formatted from saved artifacts only; no new measurement or model output was collected.",
    "Sequential replay with one request in flight; no concurrency or production-load claim.",
    "TTFT/latency start at client send time and exclude the client scheduling queue.",
    "GPU-window USD is the base-rate GPU component of the replay window only; it excludes "
    "startup, warmup, idle, CPU, memory and storage. It is not an invoice.",
    "Model quality and behavioral acceptance are recorded separately and are not "
    "established by this comparison.",
]


def mismatches(before: BenchmarkRun, after: BenchmarkRun) -> list[str]:
    """Human-readable reasons a pair fails matched_replays."""
    reasons = []
    if before.variant != "before" or after.variant != "after":
        reasons.append(f"variants are {before.variant!r}/{after.variant!r}, need before/after")
    if before.recorded_inputs_sha256 is None or (
        before.recorded_inputs_sha256 != after.recorded_inputs_sha256
    ):
        reasons.append("recorded inputs differ or are missing")
    if before.schedule_sha256 != after.schedule_sha256:
        reasons.append("schedule differs")
    if before.n_requests != after.n_requests:
        reasons.append("request count differs")
    if before.settings != after.settings:
        reasons.append("replay settings differ")
    if before.tokenizer != after.tokenizer:
        reasons.append("tokenizer differs")
    if before.price != after.price:
        reasons.append("price differs")
    if not len(before.runs) == len(after.runs) == 3:
        reasons.append("each artifact needs exactly 3 repetitions")
    if before.deployment.model_dump(exclude={"deployment_id"}) != after.deployment.model_dump(
        exclude={"deployment_id"}
    ):
        reasons.append("deployment profile differs")
    if not reasons and not matched_replays(before, after):
        reasons.append("pair is not matched")
    return reasons


def metric_cell(runs: list[ReplayMeasurement], key: str, fmt: Callable[[float], str]) -> str:
    values = [getattr(run, key) for run in runs]
    missing = sum(value is None for value in values)
    if missing:
        return f"missing in {missing}/{len(values)} repetitions"
    return f"{fmt(median(values))} ({fmt(min(values))}–{fmt(max(values))})"


def comparison_markdown(
    before: BenchmarkRun, after: BenchmarkRun, before_path: Path, after_path: Path
) -> str:
    deployment = before.deployment
    lines = [
        "# Saved replay comparison",
        "",
        f"Model `{deployment.model}` on {deployment.gpu}, vLLM {deployment.vllm_version}; "
        f"{before.n_requests} requests per repetition, {len(before.runs)} sequential "
        "repetitions per variant. Median (min–max) across repetitions.",
        "",
        "| Metric | BEFORE | AFTER |",
        "| --- | ---: | ---: |",
    ]
    lines += [
        f"| {label} | {metric_cell(before.runs, key, fmt)} | {metric_cell(after.runs, key, fmt)} |"
        for label, key, fmt in METRICS
    ]
    lines += ["", "## Artifacts", ""]
    for path, run in ((before_path, before), (after_path, after)):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"- {run.variant.upper()} `{path.name}`: SHA-256 `{digest}`")
    lines += ["", "## Limitations", ""] + [f"- {item}" for item in LIMITATIONS]
    return "\n".join(lines) + "\n"


def load_run(path: Path) -> BenchmarkRun:
    try:
        return BenchmarkRun.model_validate_json(path.read_bytes())
    except ValidationError as error:
        typer.echo(f"{path} is not a valid BenchmarkRun ({error.error_count()} errors)", err=True)
        raise typer.Exit(1) from None


def register(app: typer.Typer) -> None:
    @app.command("compare")
    def compare_command(
        before_json: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
        after_json: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
        out: Annotated[Path, typer.Option()] = Path("comparison.md"),
    ) -> None:
        """Compare two matched saved replay artifacts offline."""
        before, after = load_run(before_json), load_run(after_json)
        reasons = mismatches(before, after)
        if reasons:
            typer.echo("Refusing comparison: " + "; ".join(reasons), err=True)
            raise typer.Exit(1)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(comparison_markdown(before, after, before_json, after_json))
        typer.echo(f"Wrote saved-artifact comparison to {out}; no new measurement performed.")
