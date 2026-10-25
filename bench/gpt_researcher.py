"""Explicit pinned upstream prompt-order experiment; never imported by the engine."""

import ast
import asyncio
import difflib
import hashlib
import json
import re
import warnings
from collections import Counter
from datetime import UTC, date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Annotated

import httpx
import typer
from cachekit.fix.models import DeploymentIdentity, Generation
from cachekit.fix.task import digest
from cachekit.ingest.config import load_config
from cachekit.ingest.fix import file_sha, read_model, snapshot
from cachekit.ingest.jsonl import read_requests, write_requests
from cachekit.ingest.tokenizer import load_tokenizer
from cachekit.ingest.workspace import Workspace
from cachekit.models import BoundaryModel, Message, RequestRecord
from cachekit.render.tokenize import tokenize
from pydantic import Field

from bench.quality import CompletionResponse, validate_endpoint
from bench.replay import inspect_deployment, save_new

app = typer.Typer(no_args_is_help=True)
REVISION = "5cdad9cb434754188b78bd998df18dd8d502cf7e"
UPSTREAM = {
    "gpt_researcher/prompts.py": "d01f15d07ee9c4caf85db3c0c009fcc8ac1c8f9d6d7fd10e67cf5cc2714cd786",
    "gpt_researcher/utils/enum.py": (
        "8f41cdeb433a02177e7217fbe21274fb37aebd516d8f0711221742a3c7414075"
    ),
    "gpt_researcher/actions/report_generation.py": (
        "2a29229e213bb9dd5a04dc3e614474f4bba4ab8ce3e6c2e1c9a5f64fe17e4442"
    ),
    "LICENSE": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
}
DYNAMIC = (
    'Information: "{context}"\n---\n'
    "Using the above information, answer the following query or task: "
    '"{question}" in a detailed report --\n'
)
END = "Assume that the current date is {date.today()}.\n"


class ResearchInput(BoundaryModel):
    id: str
    question: str
    context: str
    language: str = "english"
    total_words: int = Field(default=1000, gt=0)
    required: list[str] = Field(default_factory=list)
    forbidden: list[str] = Field(default_factory=list)
    markdown_table: bool = False
    insufficient_data: bool = False


class ResearchSuite(BoundaryModel):
    version: str
    date: date
    role: str
    replay: list[ResearchInput]
    cases: list[ResearchInput]


def reorder_source(source: str) -> str:
    """Move exactly one existing context/task block; add no instructions or values."""
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PromptFamily")
    method = next(n for n in cls.body if getattr(n, "name", "") == "generate_report_prompt")
    lines = source.splitlines(keepends=True)
    original = "".join(lines[method.lineno - 1 : method.end_lineno])
    if original.count(DYNAMIC) != 1 or original.count(END) != 1:
        raise ValueError("Pinned prompt layout differs from the declared reorder")
    changed = original.replace(DYNAMIC, "", 1).replace(END, END + DYNAMIC, 1)
    if Counter(original.splitlines()) != Counter(changed.splitlines()):
        raise ValueError("The reorder changed original content")
    lines[method.lineno - 1 : method.end_lineno] = [changed]
    result = "".join(lines)
    ast.parse(result)
    return result


def load_nodes(source, select, namespace, filename):
    nodes = [node for node in ast.parse(source).body if select(node)]
    if not nodes:
        raise ValueError("Required pinned upstream definitions are absent")
    module = ast.Module(
        body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)]
        + nodes,
        type_ignores=[],
    )
    exec(compile(ast.fix_missing_locations(module), filename, "exec"), namespace)


async def render_inputs(sources, suite, cases, *, max_tokens):
    """Execute the pinned application's prompt and request functions at the LLM boundary."""
    from enum import Enum

    captured = []

    async def capture(**kwargs):
        captured.append(kwargs)
        return ""  # Capture-only sentinel, never saved or evaluated as a model output.

    class RecordedDate(date):
        @classmethod
        def today(cls):
            return suite.date

    namespace = dict(
        Enum=Enum,
        date=RecordedDate,
        datetime=datetime,
        timezone=timezone,
        warnings=warnings,
        create_chat_completion=capture,
    )
    load_nodes(
        sources["gpt_researcher/utils/enum.py"],
        lambda n: isinstance(n, ast.ClassDef),
        namespace,
        "upstream-enums.py",
    )
    load_nodes(
        sources["gpt_researcher/prompts.py"],
        lambda n: (
            isinstance(n, ast.ClassDef)
            and n.name == "PromptFamily"
            or isinstance(n, ast.FunctionDef)
            and n.name == "get_prompt_by_report_type"
            or isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "report_type_mapping" for t in n.targets)
        ),
        namespace,
        "upstream-prompts.py",
    )
    load_nodes(
        sources["gpt_researcher/actions/report_generation.py"],
        lambda n: isinstance(n, ast.AsyncFunctionDef) and n.name == "generate_report",
        namespace,
        "upstream-report-generation.py",
    )
    config = load_config()
    output = []
    for index, case in enumerate(cases):
        cfg = SimpleNamespace(
            smart_llm_model=config.vllm.model,
            smart_llm_provider="openai",
            smart_token_limit=max_tokens,
            llm_kwargs={},
            report_format="apa",
            total_words=case.total_words,
            language=case.language,
        )
        count = len(captured)
        await namespace["generate_report"](
            query=case.question,
            context=case.context,
            agent_role_prompt=suite.role,
            report_type="research_report",
            tone=namespace["Tone"].Objective,
            report_source="local",
            websocket=None,
            cfg=cfg,
            prompt_family=namespace["PromptFamily"],
        )
        if len(captured) != count + 1:
            raise ValueError("Expected exactly one original application request per case")
        request = captured[-1]
        output.append(
            RequestRecord(
                id=case.id,
                ts=float(index),
                session_id=case.id,
                route="gpt-researcher.generate_report",
                model=request["model"],
                messages=[Message.model_validate(m) for m in request["messages"]],
                # Explicit experimental controls, identical BEFORE/AFTER. Upstream uses 0.35.
                params={"temperature": 0, "max_tokens": max_tokens, "seed": 42},
                meta={
                    "source": "assafelovic/gpt-researcher",
                    "source_revision": REVISION,
                    "controlled_inputs": True,
                    "synthetic_arrivals": True,
                    "recorded_date": suite.date.isoformat(),
                    "upstream_temperature": 0.35,
                },
            )
        )
    return output


def content_preserved(before, after):
    if len(before) != len(after):
        return False
    for old, new in zip(before, after, strict=True):
        if old.model_dump(exclude={"messages"}) != new.model_dump(exclude={"messages"}):
            return False
        if [m.role for m in old.messages] != [m.role for m in new.messages]:
            return False
        if len(old.messages) != 2 or old.messages[0] != new.messages[0]:
            return False
        if Counter(old.messages[1].content.splitlines()) != Counter(
            new.messages[1].content.splitlines()
        ):
            return False
    return True


def check_behavior(case: ResearchInput, generation: Generation) -> dict[str, bool]:
    text = generation.text
    checks = {
        "complete": generation.finish_reason == "stop",
        "no_tool_calls": not generation.tool_calls,
    }
    for value in case.required:
        checks[f"contains:{value}"] = bool(
            re.search(r"(?<!\w)" + re.escape(value) + r"(?!\w)", text, re.I)
        )
    for value in case.forbidden:
        checks[f"excludes:{value}"] = value.casefold() not in text.casefold()
    if case.language == "french":
        checks["french_markers"] = (
            len(set(re.findall(r"\b(?:le|la|les|des|une|est|et|du|de)\b", text, re.I))) >= 3
        )
    if case.markdown_table:
        checks["markdown_table"] = bool(re.search(r"(?m)^\s*\|?\s*:?-{3,}:?\s*\|", text))
    if case.insufficient_data:
        checks["states_missing_data"] = bool(
            re.search(
                r"not (?:provided|available|specified|documented)|unknown|insufficient"
                r"|cannot.{0,30}determine",
                text,
                re.I,
            )
        )
        checks["no_invented_percentage"] = not bool(
            re.search(r"\d+(?:\.\d+)?\s*(?:%|percent)", text, re.I)
        )
    return checks


@app.command()
def prepare(
    directory: Annotated[Path, typer.Option()] = Path("data/gpt_researcher"),
    suite_path: Annotated[Path, typer.Option()] = Path("bench/fixtures/gpt_researcher.json"),
    quality_max_tokens: Annotated[int, typer.Option(min=1, max=4096)] = 2048,
):
    """Explicitly fetch checked public source, freeze a tiny reorder and render both variants."""
    if directory.exists():
        raise ValueError("Experiment directory already exists; use a new immutable path")
    suite = read_model(suite_path, ResearchSuite)
    if len({x.id for x in suite.cases + suite.replay}) != len(suite.cases + suite.replay):
        raise ValueError("Experiment input IDs must be unique")
    sources = {}
    with httpx.Client(timeout=30, follow_redirects=False) as client:
        for name, expected in UPSTREAM.items():
            response = client.get(
                f"https://raw.githubusercontent.com/assafelovic/gpt-researcher/{REVISION}/{name}"
            )
            response.raise_for_status()
            if hashlib.sha256(response.content).hexdigest() != expected:
                raise ValueError("Pinned upstream file checksum mismatch")
            sources[name] = response.text
    changed = sources | {
        "gpt_researcher/prompts.py": reorder_source(sources["gpt_researcher/prompts.py"])
    }
    directory.mkdir(parents=True)
    for name, source in sources.items():
        (directory / name.replace("/", "__")).write_text(source)
    (directory / "prompts_after.py").write_text(changed["gpt_researcher/prompts.py"])
    patch = "".join(
        difflib.unified_diff(
            sources["gpt_researcher/prompts.py"].splitlines(keepends=True),
            changed["gpt_researcher/prompts.py"].splitlines(keepends=True),
            fromfile="a/gpt_researcher/prompts.py",
            tofile="b/gpt_researcher/prompts.py",
        )
    )
    (directory / "candidate.patch").write_text(patch)
    workspace = Workspace(Path.cwd(), Path("data/tokenizer"), load_config())
    reports = {}
    for name, cases, budget in [
        ("replay", suite.replay, 64),
        ("quality", suite.cases, quality_max_tokens),
    ]:
        before = asyncio.run(render_inputs(sources, suite, cases, max_tokens=budget))
        after = asyncio.run(render_inputs(changed, suite, cases, max_tokens=budget))
        if not content_preserved(before, after):
            raise ValueError("Candidate changed original content, roles or settings")
        for variant, records in [("before", before), ("after", after)]:
            path = directory / f"{name}_{variant}.jsonl"
            write_requests(records, path)
            if name == "replay":
                reports[variant] = workspace.analyze_bytes(
                    path.read_bytes(),
                    f"GPT Researcher · {variant.upper()} reorder experiment · controlled inputs",
                )
    save_new(directory / "inputs.json", suite)
    manifest = dict(
        upstream_revision=REVISION,
        original_source_sha256=UPSTREAM,
        candidate_source_sha256=file_sha(directory / "prompts_after.py"),
        patch_sha256=file_sha(directory / "candidate.patch"),
        inputs_sha256=file_sha(directory / "inputs.json"),
        fixture_sha256=file_sha(suite_path),
        quality_max_tokens=quality_max_tokens,
        content_preserved=True,
        reports=reports,
        files={p.name: file_sha(p) for p in directory.iterdir() if p.is_file()},
        note="Original report-generation bodies; context/task block moved only. "
        "Controlled inputs, fixed date. "
        "Both variants use temperature 0/seed 42; replay 64 output tokens, "
        f"quality {quality_max_tokens}. "
        "Upstream temperature 0.35 is explicitly overridden for this experiment.",
    )
    save_new(directory / "manifest.json", manifest)
    typer.echo(json.dumps(manifest, indent=2))


def validate_prepared(directory):
    manifest = json.loads((directory / "manifest.json").read_text())
    if any(file_sha(directory / name) != value for name, value in manifest["files"].items()):
        raise ValueError("Frozen experiment source/input bytes changed")
    if file_sha(Path("bench/fixtures/gpt_researcher.json")) != manifest["fixture_sha256"]:
        raise ValueError("Declared behavioral fixture changed after preparation")
    return manifest


async def quality_collection(directory, endpoint, deployment, out):
    from cachekit.fix.quality import parse_tool_calls

    manifest = validate_prepared(directory)
    source = snapshot(Path.cwd())
    suite = read_model(directory / "inputs.json", ResearchSuite)
    config = load_config()
    tokenizer = load_tokenizer(
        Path("data/tokenizer"), model=config.vllm.model, revision=config.vllm.revision
    )
    records = {
        v: {r.id: r for r in read_requests(directory / f"quality_{v}.jsonl")[0]}
        for v in ("before", "after")
    }
    generation_settings = next(iter(records["before"].values())).params
    if (
        generation_settings.get("temperature") != 0
        or generation_settings.get("seed") != 42
        or any(
            record.params != generation_settings
            for group in records.values()
            for record in group.values()
        )
    ):
        raise ValueError("Quality generation settings differ across variants or cases")
    results = []
    async with httpx.AsyncClient(timeout=180, trust_env=False) as client:
        if await inspect_deployment(client, endpoint, deployment.deployment_id) != deployment:
            raise ValueError("Live deployment does not match the saved manifest")
        for case in suite.cases:
            result = {"id": case.id}
            for variant in ("before", "after"):
                tokens = tokenize(records[variant][case.id], tokenizer).token_ids
                if len(tokens) + generation_settings["max_tokens"] > deployment.max_model_len:
                    raise ValueError("Quality input exceeds deployment context")
                response = await client.post(
                    endpoint + "/v1/completions",
                    json=dict(
                        model=deployment.model,
                        prompt=tokens,
                        **generation_settings,
                        skip_special_tokens=False,
                    ),
                )
                response.raise_for_status()
                parsed = CompletionResponse.model_validate(response.json())
                if parsed.model != deployment.model or parsed.usage.prompt_tokens != len(tokens):
                    raise ValueError("Actual generation model/token accounting mismatch")
                choice = parsed.choices[0]
                text = choice.text.removesuffix("<|im_end|>").removesuffix("<|endoftext|>")
                generation = Generation(
                    text=text,
                    tool_calls=parse_tool_calls(text),
                    finish_reason=choice.finish_reason,
                    prompt_tokens=parsed.usage.prompt_tokens,
                    completion_tokens=parsed.usage.completion_tokens,
                )
                result[variant] = generation.model_dump(mode="json")
                result[f"{variant}_prompt_sha256"] = digest(tokens)
                result[f"{variant}_assertions"] = check_behavior(case, generation)
                # Preserve each actual answer even if a later collection fails.
                save_new(out / f"{case.id}_{variant}.json", result[variant])
            result["exact_match"] = result["before"]["text"] == result["after"]["text"]
            results.append(result)
    stable = source.sha256 == snapshot(Path.cwd()).sha256
    validate_prepared(directory)
    passed = stable and all(all(case["after_assertions"].values()) for case in results)
    artifact = dict(
        timestamp=datetime.now(UTC).isoformat(),
        source_sha256=source.sha256,
        source_stable=stable,
        prepared_manifest_sha256=file_sha(directory / "manifest.json"),
        fixture_sha256=manifest["fixture_sha256"],
        deployment=deployment.model_dump(mode="json"),
        generation=generation_settings,
        cases=results,
        after_assertions_passed=passed,
        human_review="pending",
        approval=None,
        note="Actual controlled-input outputs from pinned upstream prompt functions. "
        "Bounded assertions, not semantic equivalence; changed answers require human review.",
    )
    save_new(out / "quality.json", artifact)
    typer.echo(
        json.dumps(
            {
                "source_stable": stable,
                "after_assertions_passed": passed,
                "cases": [
                    {
                        "id": c["id"],
                        "before": c["before_assertions"],
                        "after": c["after_assertions"],
                        "exact_match": c["exact_match"],
                    }
                    for c in results
                ],
            },
            indent=2,
        )
    )
    if not passed:
        raise ValueError(
            "Actual AFTER behavior assertions failed; saved outputs require investigation"
        )


@app.command()
def quality(
    endpoint: Annotated[str, typer.Option()],
    deployment_manifest: Annotated[Path, typer.Option()],
    out: Annotated[Path, typer.Option()],
    directory: Annotated[Path, typer.Option()] = Path("data/gpt_researcher"),
):
    """Collect fixed actual BEFORE/AFTER answers once; never retries or grants approval."""
    if out.exists():
        raise ValueError("Quality output directory exists; select a new immutable path")
    out.mkdir(parents=True)
    deployment = read_model(deployment_manifest, DeploymentIdentity)
    asyncio.run(quality_collection(directory, validate_endpoint(endpoint), deployment, out))


if __name__ == "__main__":
    app()
