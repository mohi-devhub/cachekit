"""Explicit E2/E3 streaming replay. No deterministic engine command imports this runner."""

import asyncio
import math
import statistics
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal

import httpx
import typer
import yaml
from cachekit import __version__
from cachekit.fix.models import DeploymentIdentity
from cachekit.fix.task import digest
from cachekit.ingest.config import load_config
from cachekit.ingest.fix import file_sha, read_model, snapshot
from cachekit.ingest.jsonl import read_requests
from cachekit.ingest.tokenizer import load_tokenizer
from cachekit.render.tokenize import tokenize
from cachekit.serialization import canonical_json

from bench.metrics import CacheSnapshot, counter_delta, parse_metrics
from bench.models import BenchmarkRun, ReplayMeasurement, ReplaySettings
from bench.quality import ModelsResponse, VersionResponse, validate_endpoint
from bench.stream import completion

app = typer.Typer(no_args_is_help=True)


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    left, right = math.floor(position), math.ceil(position)
    return ordered[left] + (ordered[right] - ordered[left]) * (position - left)


async def scrape(client: httpx.AsyncClient, endpoint: str, model: str) -> CacheSnapshot:
    response = await client.get(endpoint + "/metrics")
    response.raise_for_status()
    return parse_metrics(response.text, model)


async def wait_ready(client, endpoint: str, timeout: float = 900):
    endpoint = validate_endpoint(endpoint)
    deadline = time.perf_counter() + timeout
    while True:
        try:
            response = await client.get(endpoint + "/health")
            if response.status_code == 200:
                return
            if response.status_code != 503:
                response.raise_for_status()
        except httpx.TransportError:
            pass
        if time.perf_counter() >= deadline:
            raise ValueError("Server startup exceeded the readiness timeout")
        await asyncio.sleep(2)


async def inspect_deployment(client, endpoint: str, deployment_id: str) -> DeploymentIdentity:
    endpoint = validate_endpoint(endpoint)
    profile = load_config().vllm
    version_response = await client.get(endpoint + "/version")
    model_response = await client.get(endpoint + "/v1/models")
    version_response.raise_for_status()
    model_response.raise_for_status()
    version = VersionResponse.model_validate(version_response.json())
    models = ModelsResponse.model_validate(model_response.json())
    model = next((m for m in models.data if m.id == profile.model), None)
    if (
        version.version != profile.version
        or model is None
        or model.max_model_len != profile.max_model_len
    ):
        raise ValueError("Live version/model/context differs from the pinned profile")
    cache = await scrape(client, endpoint, profile.model)
    if cache.running or cache.waiting:
        raise ValueError("Benchmark server is busy")
    return DeploymentIdentity(
        model=profile.model,
        revision=profile.revision,
        tokenizer_revision=profile.revision,
        vllm_version=version.version,
        gpu="L4",
        max_model_len=model.max_model_len,
        block_size=cache.block_size,
        capacity_blocks=cache.capacity_blocks,
        deployment_id=deployment_id,
    )


async def settle(client, endpoint, model, before, expected: int, timeout: float):
    deadline = time.perf_counter() + timeout
    while True:
        after = await scrape(client, endpoint, model)
        queries, _ = counter_delta(before, after)
        if queries > expected:
            raise ValueError("Unexpected inference traffic contaminated the measurement")
        if queries == expected and after.running == after.waiting == 0:
            return after
        if time.perf_counter() >= deadline:
            raise ValueError("Cache counters did not settle to the exact prompt-token count")
        await asyncio.sleep(0.25)


def payload(tokens, model, settings):
    return dict(
        model=model,
        prompt=tokens,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        seed=settings.seed,
        stream=True,
        stream_options={"include_usage": True},
        skip_special_tokens=False,
    )


async def measure(
    client, endpoint, encoded, records, deployment, settings, tokenizer, repetition, gpu_hourly_usd
):
    from cachekit.simulate.vllm import simulate

    profile = load_config().vllm.model_copy(
        update={
            "block_size": deployment.block_size,
            "capacity_blocks": deployment.capacity_blocks,
        }
    )
    simulation = simulate(encoded, profile)
    before_warm = await scrape(client, endpoint, deployment.model)
    if before_warm.running or before_warm.waiting:
        raise ValueError("Benchmark server must be exclusive and idle")
    warm_tokens = 0
    for i in range(settings.warmup_requests):
        tokens = tokenizer.encode_offsets(f"Warmup unrelated to helpdesk policy: {i}. Reply OK.")[0]
        warm_tokens += len(tokens)
        await completion(
            client,
            endpoint,
            payload(tokens, deployment.model, settings),
            request_id=f"warmup-{i}",
            origin=time.perf_counter(),
            scheduled=0,
        )
    await settle(
        client, endpoint, deployment.model, before_warm, warm_tokens, settings.metrics_timeout
    )
    response = await client.post(endpoint + "/reset_prefix_cache")
    response.raise_for_status()
    if response.json() != {"success": True}:
        raise ValueError("Server declined the prefix-cache reset")
    before = await scrape(client, endpoint, deployment.model)
    if counter_delta(before_warm, before)[0] != warm_tokens:
        raise ValueError("Unexpected traffic between warmup and reset")
    if before.running or before.waiting:
        raise ValueError("Server is busy after reset")
    origin = time.perf_counter()
    rows = []
    for record, request in zip(records, encoded, strict=True):
        scheduled = (request.ts - encoded[0].ts) / settings.arrival_scale
        await asyncio.sleep(max(0, origin + scheduled - time.perf_counter()))
        body = payload(request.token_ids, deployment.model, settings)
        if "cache_salt" in record.params:
            body["cache_salt"] = record.params["cache_salt"]
        rows.append(
            await completion(
                client, endpoint, body, request_id=request.id, origin=origin, scheduled=scheduled
            )
        )
    duration = rows[-1].ended_s
    expected = sum(r.prompt_tokens for r in rows)
    after = await settle(
        client, endpoint, deployment.model, before, expected, settings.metrics_timeout
    )
    queries, hits = counter_delta(before, after)
    if all(row.cached_tokens is not None for row in rows):
        if sum(row.cached_tokens for row in rows) != hits:
            raise ValueError("Stream cached-token usage disagrees with server counters")
    measured = hits / queries
    gpu_seconds = duration * 1000 / len(rows)
    return ReplayMeasurement(
        repetition=repetition,
        requests=rows,
        duration_s=duration,
        ttft_p50_s=percentile([r.ttft_s for r in rows], 0.5),
        ttft_p95_s=percentile([r.ttft_s for r in rows], 0.95),
        latency_p50_s=percentile([r.latency_s for r in rows], 0.5),
        latency_p95_s=percentile([r.latency_s for r in rows], 0.95),
        throughput_requests_s=len(rows) / duration,
        queried_tokens=queries,
        cached_tokens=hits,
        measured_hit_rate=measured,
        simulated_hit_rate=simulation.hit_rate,
        absolute_hit_rate_error=abs(measured - simulation.hit_rate),
        allocated_gpu_seconds_per_1000=gpu_seconds,
        gpu_window_usd_per_1000=gpu_seconds * gpu_hourly_usd / 3600
        if gpu_hourly_usd is not None
        else None,
        metrics_before=before,
        metrics_after=after,
    )


def load_price(path: Path) -> dict | None:
    entry = yaml.safe_load(path.read_text())["vllm"]["gpu_hourly_usd"]
    if entry["value"] is None:
        return None
    value = entry["value"]
    if (
        type(value) not in {int, float}
        or not math.isfinite(value)
        or value <= 0
        or entry.get("source") != "https://modal.com/pricing"
        or not entry.get("verified_on")
    ):
        raise ValueError("GPU price requires a positive verified Modal rate")
    return entry


async def collect(
    *,
    repo: Path,
    input_path: Path,
    recorded_inputs: Path | None,
    variant: str,
    endpoint: str,
    deployment: DeploymentIdentity,
    tokenizer,
    settings: ReplaySettings,
    client: httpx.AsyncClient,
    price: dict | None,
    exclusive_server: bool,
) -> BenchmarkRun:
    endpoint = validate_endpoint(endpoint)
    if not exclusive_server:
        raise ValueError("A dedicated single-container benchmark server must be confirmed")
    config = load_config()
    if (
        tokenizer.identity.get("model") != config.vllm.model
        or tokenizer.identity.get("revision") != config.vllm.revision
    ):
        raise ValueError("Tokenizer does not match the selected model revision")
    live = await inspect_deployment(client, endpoint, deployment.deployment_id)
    if live != deployment:
        raise ValueError("Deployment manifest differs from live cache/version/model profile")
    records, input_hash = read_requests(input_path)
    if not records:
        raise ValueError("No requests to replay")
    records = sorted(records, key=lambda r: (r.ts, r.id))
    for record in records:
        if set(record.params) - {"temperature", "max_tokens", "seed", "cache_salt"}:
            raise ValueError("Unsupported generation params; never silently discard settings")
        for key in ("temperature", "max_tokens", "seed"):
            if key in record.params and record.params[key] != getattr(settings, key):
                raise ValueError("Recorded generation settings differ from replay settings")
    encoded = [tokenize(r, tokenizer) for r in records]
    if any(
        not r.token_ids or len(r.token_ids) + settings.max_tokens > deployment.max_model_len
        for r in encoded
    ):
        raise ValueError("A prompt plus output budget exceeds context; truncation is forbidden")
    recorded_hash = file_sha(recorded_inputs) if recorded_inputs else None
    source = snapshot(repo)
    runs = []
    for repetition in range(1, settings.repetitions + 1):
        runs.append(
            await measure(
                client,
                endpoint,
                encoded,
                records,
                deployment,
                settings,
                tokenizer,
                repetition,
                price["value"] if price else None,
            )
        )
    if snapshot(repo).sha256 != source.sha256 or file_sha(input_path) != input_hash:
        raise ValueError("Source or replay inputs changed during collection")
    if recorded_inputs and file_sha(recorded_inputs) != recorded_hash:
        raise ValueError("Recorded application inputs changed during collection")
    metrics = (
        "measured_hit_rate",
        "simulated_hit_rate",
        "absolute_hit_rate_error",
        "ttft_p50_s",
        "ttft_p95_s",
        "latency_p50_s",
        "latency_p95_s",
        "throughput_requests_s",
        "allocated_gpu_seconds_per_1000",
        "gpu_window_usd_per_1000",
    )
    summary = {}
    for key in metrics:
        values = [getattr(run, key) for run in runs]
        if all(v is not None for v in values):
            summary[key] = {
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
            }
    git = subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True)
    return BenchmarkRun(
        variant=variant,
        timestamp=datetime.now(UTC).isoformat(),
        git_sha=source.git_sha,
        source_sha256=source.sha256,
        git_dirty=bool(git.stdout.strip()) if source.git_sha else None,
        input_sha256=input_hash,
        recorded_inputs_sha256=recorded_hash,
        schedule_sha256=digest([(r.id, r.ts) for r in records]),
        config_sha256=digest(
            {
                "analysis": config.model_dump(mode="json"),
                "deployment": deployment.model_dump(mode="json"),
                "settings": settings.model_dump(mode="json"),
                "price": price,
            }
        ),
        tokenizer=tokenizer.identity,
        deployment=deployment,
        settings=settings,
        cachekit_version=__version__,
        n_requests=len(records),
        price=price,
        runs=runs,
        summary=summary,
        note="Sequential scheduled streaming replay on one exclusive L4. TTFT is client-side first "
        "nonempty output event; scheduling delay is separate. GPU seconds are allocated benchmark "
        "window wall time, not hardware utilization. GPU-only USD excludes startup, warmup, reset, "
        "idle, CPU, memory and storage; it is not the complete Modal invoice. "
        "Simulator is prompt-only "
        "and excludes generated-token pressure. Revision/GPU identity is operator-provided; live "
        "version, model, context and cache configuration are checked. "
        "No raw prompts/outputs saved.",
    )


def save_new(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as file:
        file.write(canonical_json(value) + "\n")


@app.command("inspect")
def inspect_command(
    endpoint: Annotated[str, typer.Option()],
    deployment_id: Annotated[str, typer.Option()],
    out: Annotated[Path, typer.Option()],
):
    """Save a live cache profile. Model revision/L4 identity comes from the pinned deployment."""

    async def inspect():
        async with httpx.AsyncClient(timeout=30, trust_env=False) as client:
            await wait_ready(client, endpoint)
            return await inspect_deployment(client, endpoint, deployment_id)

    try:
        if out.exists():
            raise ValueError("Manifest already exists; use a new path")
        save_new(out, asyncio.run(inspect()))
        typer.echo("Saved live deployment manifest: " + str(out))
    except Exception as error:
        typer.echo(
            f"Deployment inspection failed ({type(error).__name__}); details withheld", err=True
        )
        raise typer.Exit(1) from None


@app.command("run")
def run_command(
    input_path: Annotated[Path, typer.Option("--input", exists=True, dir_okay=False)],
    variant: Annotated[Literal["before", "after"], typer.Option()],
    endpoint: Annotated[str, typer.Option()],
    deployment_manifest: Annotated[Path, typer.Option(exists=True, dir_okay=False)],
    out: Annotated[Path, typer.Option()],
    exclusive_server: Annotated[bool, typer.Option()] = False,
    recorded_inputs: Annotated[Path | None, typer.Option(exists=True, dir_okay=False)] = None,
    repo: Annotated[Path, typer.Option(exists=True, file_okay=False)] = Path("."),
    tokenizer: Annotated[Path, typer.Option()] = Path("data/tokenizer"),
    repetitions: Annotated[int, typer.Option(min=1, max=3)] = 3,
    arrival_scale: Annotated[float, typer.Option(min=0.000001)] = 1,
):
    """Run actual inference explicitly; failures produce no completed benchmark artifact."""

    async def run(deployment, loaded, settings, price):
        async with httpx.AsyncClient(timeout=300, trust_env=False) as client:
            return await collect(
                repo=repo,
                input_path=input_path,
                recorded_inputs=recorded_inputs,
                variant=variant,
                endpoint=endpoint,
                deployment=deployment,
                tokenizer=loaded,
                settings=settings,
                client=client,
                price=price,
                exclusive_server=exclusive_server,
            )

    try:
        if out.exists():
            raise ValueError("Result already exists; select a new immutable run path")
        config = load_config()
        loaded = load_tokenizer(tokenizer, model=config.vllm.model, revision=config.vllm.revision)
        deployment = read_model(deployment_manifest, DeploymentIdentity)
        price = load_price(
            Path(__file__).resolve().parents[1] / "engine/cachekit/config/pricing.yaml"
        )
        result = asyncio.run(
            run(
                deployment,
                loaded,
                ReplaySettings(repetitions=repetitions, arrival_scale=arrival_scale),
                price,
            )
        )
        save_new(out, result)
        typer.echo("Saved actual replay measurements: " + str(out))
    except Exception as error:
        typer.echo(
            f"Benchmark failed ({type(error).__name__}); prompts/responses withheld. "
            "No completed result saved.",
            err=True,
        )
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
