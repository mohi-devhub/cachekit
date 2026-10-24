"""Public local-API contracts. Never include raw input files or credentials."""

from typing import Literal

from pydantic import Field

from cachekit.benchmark_models import BenchmarkRun
from cachekit.fix.models import Approval, FixTask, VerificationRun, VerifyResult
from cachekit.models import AnalysisRun, BoundaryModel, JsonObject, Report


class DatasetOption(BoundaryModel):
    id: str
    name: str
    available: bool
    description: str


class AnalyzeRequest(BoundaryModel):
    dataset_id: Literal["demo-before", "glaive-sample", "swe-sample"] = "demo-before"


class AnalyzeResponse(BoundaryModel):
    report_id: str


class SmokeRequest(BoundaryModel):
    request: int
    prompt_tokens: int
    cached_tokens: float
    queried_tokens: float


class SmokeView(BoundaryModel):
    experiment: Literal["serving_smoke"]
    status: str
    model: str
    revision: str
    gpu: str
    vllm_version: str
    timestamp: str
    block_size: int
    capacity_tokens: int
    requests: list[SmokeRequest]
    source: str
    sha256: str


class BenchmarkArtifact(BoundaryModel):
    source: str
    sha256: str
    run: BenchmarkRun


class BenchView(BoundaryModel):
    smoke: SmokeView | None
    benchmarks: list[BenchmarkArtifact]
    comparison_ready: bool = False
    note: str


class ReportSummary(BoundaryModel):
    id: str
    n_requests: int
    n_findings: int
    routes: list[str]
    timestamp: str


class ReportBundle(BoundaryModel):
    id: str
    report: Report
    metadata: AnalysisRun


class CandidateView(BoundaryModel):
    task_id: str
    report: Report
    verification: VerifyResult
    metadata: VerificationRun
    approval: Approval | None = None


class TaskRequest(BoundaryModel):
    finding_ids: list[str] | None = None


class TaskView(BoundaryModel):
    task: FixTask
    markdown: str
    state: Literal["prepared", "candidate", "stale"]
    verification: VerifyResult | None = None
    verification_current: bool = False
    approval: Approval | None = None
    handoff: JsonObject | None = None
    golden_cases: list[JsonObject] = Field(default_factory=list)
    quality_outputs: list[JsonObject] = Field(default_factory=list)
    note: str


class VerifyRequest(BoundaryModel):
    task_id: str = Field(pattern=r"^[a-f0-9]{24}$")
    quality_run_id: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    review_ids: list[str] = Field(default_factory=list)


class VerifyResponse(BoundaryModel):
    id: str
    result: VerifyResult


class ApproveRequest(BoundaryModel):
    task_id: str = Field(pattern=r"^[a-f0-9]{24}$")
    verification_id: str = Field(pattern=r"^[a-f0-9]{64}$")
    diff_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    reviewer: str = Field(min_length=1)
    review_ids: list[str] = Field(default_factory=list)
