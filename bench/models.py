"""Saved measurement contracts. Tokens, timings and hashes only; never raw prompts."""

from typing import Literal

from cachekit.fix.models import DeploymentIdentity
from cachekit.models import SHA256, BoundaryModel, JsonObject, Rate
from pydantic import Field

from bench.metrics import CacheSnapshot


class ReplaySettings(BoundaryModel):
    repetitions: int = Field(default=3, ge=1, le=3)
    arrival_scale: float = Field(default=1, gt=0)
    max_tokens: int = Field(default=64, gt=0)
    temperature: Literal[0] = 0
    seed: int = 42
    concurrency: Literal[1] = 1
    warmup_requests: Literal[5] = 5
    metrics_timeout: float = Field(default=15, gt=0)


class RequestMeasurement(BoundaryModel):
    request_sha256: SHA256
    scheduled_s: float = Field(ge=0)
    sent_s: float = Field(ge=0)
    first_token_s: float = Field(ge=0)
    ended_s: float = Field(ge=0)
    ttft_s: float = Field(ge=0)
    latency_s: float = Field(ge=0)
    scheduling_delay_s: float = Field(ge=0)
    prompt_tokens: int = Field(gt=0)
    completion_tokens: int = Field(gt=0)
    cached_tokens: int | None = Field(default=None, ge=0)
    finish_reason: Literal["stop", "length"]
    output_sha256: SHA256


class ReplayMeasurement(BoundaryModel):
    repetition: int = Field(ge=1)
    requests: list[RequestMeasurement]
    duration_s: float = Field(gt=0)
    ttft_p50_s: float = Field(ge=0)
    ttft_p95_s: float = Field(ge=0)
    latency_p50_s: float = Field(ge=0)
    latency_p95_s: float = Field(ge=0)
    throughput_requests_s: float = Field(gt=0)
    queried_tokens: int = Field(gt=0)
    cached_tokens: int = Field(ge=0)
    measured_hit_rate: Rate
    simulated_hit_rate: Rate
    absolute_hit_rate_error: Rate
    allocated_gpu_seconds_per_1000: float = Field(gt=0)
    gpu_window_usd_per_1000: float | None = None
    metrics_before: CacheSnapshot
    metrics_after: CacheSnapshot


class BenchmarkRun(BoundaryModel):
    experiment: Literal["E2-E3-replay"] = "E2-E3-replay"
    measurement: Literal["MEASURED"] = "MEASURED"
    status: Literal["completed"] = "completed"
    variant: Literal["before", "after"]
    timestamp: str
    git_sha: str | None
    source_sha256: SHA256
    git_dirty: bool | None
    input_sha256: SHA256
    recorded_inputs_sha256: SHA256 | None
    schedule_sha256: SHA256
    config_sha256: SHA256
    tokenizer: JsonObject
    deployment: DeploymentIdentity
    settings: ReplaySettings
    cachekit_version: str
    n_requests: int = Field(gt=0)
    price: JsonObject | None
    runs: list[ReplayMeasurement]
    summary: dict[str, dict[str, float]]
    note: str
