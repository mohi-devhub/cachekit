"""Protocol and accounting fixtures only. No fake measurements leave pytest's temp dirs."""

import asyncio
import hashlib
import json
import time
from pathlib import Path

import httpx
import pytest
from cachekit.ingest.config import load_config
from cachekit.ingest.jsonl import write_requests
from cachekit.models import RequestRecord
from fastapi import FastAPI
from fastapi.testclient import TestClient

from bench.metrics import counter_delta, parse_metrics
from bench.middleware import BenchmarkRoutes
from bench.models import ReplaySettings
from bench.quality import validate_endpoint
from bench.replay import collect, inspect_deployment, percentile, save_new
from bench.stream import completion

MODEL = "Qwen/Qwen3-4B-Instruct-2507"


def metrics(queries=0, hits=0, created=1):
    label = f'engine="0",model_name="{MODEL}"'
    return (
        "\n".join(
            [
                f"vllm:prefix_cache_queries_total{{{label}}} {queries}",
                f"vllm:prefix_cache_hits_total{{{label}}} {hits}",
                f"vllm:prefix_cache_queries_created{{{label}}} {created}",
                f"vllm:prefix_cache_hits_created{{{label}}} {created}",
                f"vllm:num_requests_running{{{label}}} 0",
                f"vllm:num_requests_waiting{{{label}}} 0",
                'vllm:cache_config_info{engine="0",block_size="16",num_gpu_blocks="5180",'
                'kv_cache_size_tokens="82880",enable_prefix_caching="True",sliding_window="None",'
                'is_attention_free="False"} 1',
            ]
        )
        + "\n"
    )


def stream(prompt=4, tokens=1, text="PRIVATE_OUTPUT", done=True, usage=True):
    events = [
        dict(model=MODEL, choices=[dict(index=0, text="", finish_reason=None)]),
        dict(model=MODEL, choices=[dict(index=0, text=text, finish_reason=None)]),
        dict(model=MODEL, choices=[dict(index=0, text="", finish_reason="stop")]),
    ]
    if usage:
        events.append(
            dict(
                model=MODEL, choices=[], usage=dict(prompt_tokens=prompt, completion_tokens=tokens)
            )
        )
    result = "".join("data: " + json.dumps(event) + "\n\n" for event in events)
    return result + ("data: [DONE]\n\n" if done else "")


def test_metrics_token_units_config_and_delta():
    before = parse_metrics(metrics(), MODEL)
    after = parse_metrics(metrics(32, 16), MODEL)
    assert counter_delta(before, after) == (32, 16)
    assert after.capacity_tokens == after.block_size * after.capacity_blocks
    with pytest.raises(ValueError, match="restarted"):
        counter_delta(before, parse_metrics(metrics(32, 16, created=2), MODEL))
    with pytest.raises(ValueError, match="reset"):
        counter_delta(after, before)


@pytest.mark.parametrize(
    "change",
    [
        lambda s: s.replace('engine="0"', 'engine="1"'),
        lambda s: s.replace('enable_prefix_caching="True"', 'enable_prefix_caching="False"'),
        lambda s: s.replace("82880", "82881"),
        lambda s: s + s,
        lambda s: s.replace("queries_total", "other_queries"),
        lambda s: s.replace('sliding_window="None"', 'sliding_window="128"'),
    ],
)
def test_metrics_rejects_ambiguous_missing_disabled_or_hybrid_profile(change):
    with pytest.raises(ValueError):
        parse_metrics(change(metrics()), MODEL)


@pytest.mark.parametrize(
    "options", [{"done": False}, {"usage": False}, {"prompt": 5}, {"tokens": 0}]
)
def test_stream_rejects_incomplete_or_inconsistent_usage(options):
    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda r: httpx.Response(
                    200, text=stream(**options), headers={"content-type": "text/event-stream"}
                )
            )
        ) as client:
            await completion(
                client,
                "http://localhost",
                dict(model=MODEL, prompt=[1] * 4, max_tokens=8),
                request_id="private-id",
                origin=time.perf_counter(),
                scheduled=0,
            )

    with pytest.raises(ValueError):
        asyncio.run(run())


def test_stream_first_nonempty_token_timing_and_output_privacy(monkeypatch):
    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda r: httpx.Response(
                    200, text=stream(), headers={"content-type": "text/event-stream"}
                )
            )
        ) as client:
            clock = iter([10, 11, 12])
            monkeypatch.setattr("bench.stream.perf_counter", lambda: next(clock))
            return await completion(
                client,
                "http://localhost",
                dict(model=MODEL, prompt=[1] * 4, max_tokens=8),
                request_id="PRIVATE_ID",
                origin=9,
                scheduled=0,
            )

    row = asyncio.run(run())
    assert row.sent_s == 1 and row.first_token_s == 2 and row.ended_s == 3
    assert row.ttft_s == 1 and row.latency_s == 2 and row.scheduling_delay_s == 1
    assert row.output_sha256 == hashlib.sha256(b"PRIVATE_OUTPUT").hexdigest()
    assert "PRIVATE_" not in row.model_dump_json()


class MockServer:
    def __init__(self, *, reset=True, contaminated=False):
        self.queries = 0
        self.reset = reset
        self.contaminated = contaminated
        self.reset_calls = 0
        self.requests = []

    def __call__(self, request):
        path = request.url.path
        if path == "/version":
            return httpx.Response(200, json={"version": load_config().vllm.version})
        if path == "/v1/models":
            return httpx.Response(200, json={"data": [{"id": MODEL, "max_model_len": 16384}]})
        if path == "/metrics":
            return httpx.Response(200, text=metrics(self.queries))
        if path == "/reset_prefix_cache":
            self.reset_calls += 1
            return httpx.Response(200, json={"success": self.reset})
        assert path == "/v1/completions"
        payload = json.loads(request.content)
        assert isinstance(payload["prompt"], list) and payload["stream_options"]["include_usage"]
        self.requests.append(payload)
        self.queries += len(payload["prompt"]) + int(self.contaminated)
        return httpx.Response(
            200,
            text=stream(prompt=len(payload["prompt"])),
            headers={"content-type": "text/event-stream"},
        )


def run_fixture(tmp_path, tokenizer, *, reset=True, contaminated=False, exclusive=True):
    tmp_path.mkdir(exist_ok=True)
    path = tmp_path / "data/input.jsonl"
    write_requests(
        [
            RequestRecord(
                id="PRIVATE_REQUEST",
                ts=0,
                messages=[{"role": "user", "content": "PRIVATE_PROMPT"}],
                params={"temperature": 0, "max_tokens": 64},
            )
        ],
        path,
    )
    server = MockServer(reset=reset, contaminated=contaminated)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(server)) as client:
            manifest = await inspect_deployment(
                client, "http://localhost", "fixture-not-a-deployment"
            )
            return await collect(
                repo=tmp_path,
                input_path=path,
                recorded_inputs=None,
                variant="before",
                endpoint="http://localhost",
                deployment=manifest,
                tokenizer=tokenizer,
                settings=ReplaySettings(repetitions=3),
                client=client,
                price={"value": 1, "source": "fixture", "verified_on": "fixture"},
                exclusive_server=exclusive,
            )

    return asyncio.run(run()), server


def test_replay_repetitions_warmups_resets_metadata_and_no_raw_artifact(tmp_path, qwen_tokenizer):
    result, server = run_fixture(tmp_path, qwen_tokenizer)
    assert len(result.runs) == 3 and server.reset_calls == 3
    assert len(server.requests) == 3 * (5 + result.n_requests)
    assert result.summary["measured_hit_rate"] == {"median": 0, "min": 0, "max": 0}
    for run in result.runs:
        assert run.queried_tokens == sum(r.prompt_tokens for r in run.requests)
        assert run.absolute_hit_rate_error == abs(run.measured_hit_rate - run.simulated_hit_rate)
        assert run.gpu_window_usd_per_1000 == pytest.approx(
            run.allocated_gpu_seconds_per_1000 / 3600
        )
    output = tmp_path / "eval_results/test-only.json"
    save_new(output, result)
    assert "PRIVATE_" not in output.read_text()
    assert "recorded_inputs_sha256" in output.read_text()
    with pytest.raises(FileExistsError):
        save_new(output, result)


@pytest.mark.parametrize(
    "options", [{"reset": False}, {"contaminated": True}, {"exclusive": False}]
)
def test_replay_rejects_bad_reset_other_traffic_and_unconfirmed_server(
    tmp_path, qwen_tokenizer, options
):
    with pytest.raises(ValueError):
        run_fixture(tmp_path, qwen_tokenizer, **options)


def test_route_allowlist_blocks_dev_rpc_and_other_paths():
    app = FastAPI()
    app.add_middleware(BenchmarkRoutes)

    @app.post("/collective_rpc")
    def dangerous():
        raise AssertionError("Development RPC must never be reached")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    client = TestClient(app)
    assert client.post("/collective_rpc").status_code == 404
    assert client.get("/openapi.json").status_code == 404
    assert client.get("/health").status_code == 200


def test_modal_hosts_percentiles_and_serving_pin():
    assert validate_endpoint("https://workspace--server.us-east.modal.direct")
    assert percentile([1], 0.95) == 1
    assert percentile([0, 10], 0.95) == 9.5
    import ast

    source = Path(__file__).resolve().parents[2] / "bench/modal_vllm.py"
    assignments = {
        n.targets[0].id: ast.literal_eval(n.value)
        for n in ast.parse(source.read_text()).body
        if isinstance(n, ast.Assign)
        and isinstance(n.targets[0], ast.Name)
        and n.targets[0].id in {"MODEL", "REVISION", "VLLM_VERSION"}
    }
    config = load_config().vllm
    assert (assignments["MODEL"], assignments["REVISION"], assignments["VLLM_VERSION"]) == (
        config.model,
        config.revision,
        config.version,
    )


@pytest.mark.parametrize("status", [200, 401, 503])
def test_startup_readiness_is_bounded_and_does_not_retry_auth_failures(status):
    from bench.replay import wait_ready

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda r: httpx.Response(status))
        ) as client:
            await wait_ready(client, "http://localhost", timeout=0)

    if status == 200:
        asyncio.run(run())
    else:
        with pytest.raises(httpx.HTTPStatusError if status == 401 else ValueError):
            asyncio.run(run())
