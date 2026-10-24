"""Exercise real HTTP contracts, private storage, provenance and fail-closed gates."""

import hashlib
import json
import socket

import pytest
from cachekit.api import create_app
from cachekit.ingest.fix import file_sha
from fastapi.testclient import TestClient
from fix_helpers import temporary_bundle


def client_for(repo, tokenizer, config, **options):
    app = create_app(repo=repo, tokenizer=repo / "unused-tokenizer", config=config, **options)
    app.state.workspace._tokenizer = tokenizer
    return TestClient(app), app.state.workspace


def test_upload_saves_exact_input_and_repeatable_report_without_network(
    tmp_path, qwen_tokenizer, config, monkeypatch
):
    client, workspace = client_for(tmp_path, qwen_tokenizer, config)
    raw = b'{"id":"a","ts":0,"messages":[{"role":"user","content":"hello"}]}\n'

    def forbidden(*args, **kwargs):
        raise AssertionError("Analysis attempted a network connection")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    response = client.post("/analyze/upload", content=raw)
    assert response.status_code == 200, response.text
    key = response.json()["report_id"]
    assert client.post("/analyze/upload", content=raw).json()["report_id"] == key
    saved = client.get(f"/reports/{key}/bundle").json()
    assert saved["metadata"]["report_sha256"] == key
    assert saved["metadata"]["input_sha256"] == hashlib.sha256(raw).hexdigest()
    assert saved["metadata"]["n_requests"] == saved["report"]["n_requests"] == 1
    assert saved["metadata"]["gpu"] is None
    assert saved["report"]["backends"][0]["cost_actual"] is None
    assert client.get("/reports").json()[0]["id"] == key
    assert (
        workspace.private / "inputs" / f"{hashlib.sha256(raw).hexdigest()}.jsonl"
    ).read_bytes() == raw
    assert not (tmp_path / "web/public").exists()
    path = workspace.report_path(key)
    path.write_text(path.read_text() + " ")
    assert client.get(f"/reports/{key}/bundle").status_code == 400


@pytest.mark.parametrize(
    "payload", [b"PRIVATE_INVALID_JSON", b'{"messages":"PRIVATE_SENTINEL"}', b"", b"\xff"]
)
def test_rejects_invalid_upload_without_echoing_input(tmp_path, qwen_tokenizer, config, payload):
    client, workspace = client_for(tmp_path, qwen_tokenizer, config)
    response = client.post("/analyze/upload", content=payload)
    assert response.status_code == 400
    assert "PRIVATE" not in response.text
    assert not workspace.private.exists()


def test_size_limit_and_identifier_only_paths(tmp_path, qwen_tokenizer, config):
    client, _ = client_for(tmp_path, qwen_tokenizer, config, max_upload_bytes=8)
    assert client.post("/analyze/upload", content=b"x" * 9).status_code == 413
    assert client.get("/reports/not-a-report").status_code == 404
    assert client.get("/fix/not-a-task").status_code == 404
    response = client.post("/analyze", json={"dataset_id": "../.env", "key": "PRIVATE_KEY"})
    assert response.status_code == 422 and "PRIVATE_KEY" not in response.text
    response = client.post("/verify", json={"task_id": "a" * 24, "quality_run_id": "../.env"})
    assert response.status_code == 422
    assert client.post("/fix", json={"api_key": "PRIVATE_KEY"}).status_code == 404


def test_saved_dataset_selection_and_untrusted_browser_origin(tmp_path, qwen_tokenizer, config):
    client, _ = client_for(tmp_path, qwen_tokenizer, config)
    assert all(not d["available"] for d in client.get("/datasets").json())
    assert client.post("/analyze", json={"dataset_id": "demo-before"}).status_code == 404
    response = client.options(
        "/analyze",
        headers={"Origin": "https://unrelated.example", "Access-Control-Request-Method": "POST"},
    )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
    assert client.get("/bench").json()["smoke"] is None


def test_task_redaction_scope_and_missing_quality_block_approval(tmp_path, qwen_tokenizer, config):
    repo, _, _, _ = temporary_bundle(tmp_path, qwen_tokenizer, config)
    for name in ("CHANGELOG.md", "AI_USAGE.md"):
        (repo / name).write_text("Fixture document\n")
    client, workspace = client_for(repo, qwen_tokenizer, config)
    raw = (repo / "data/demo/requests_before.jsonl").read_bytes()
    report_id = client.post("/analyze/upload", content=raw).json()["report_id"]
    response = client.post(f"/reports/{report_id}/task", json={})
    assert response.status_code == 200, response.text
    view = response.json()
    assert view["state"] == "prepared" and view["verification"] is None
    task_id = view["task"]["id"]
    assert len(view["golden_cases"]) == 5
    assert "recorded_inputs" not in view["task"]
    # A source change outside the declared scope invalidates the baseline.
    (repo / "fixture_tests.py").write_text("def test_changed(): pass\n")
    assert client.get(f"/fix/{task_id}").json()["state"] == "stale"
    response = client.post("/verify", json={"task_id": task_id})
    assert response.status_code == 200, response.text
    result = response.json()
    assert not result["result"]["passed"]
    assert not result["result"]["scope_check"]["passed"]
    assert result["result"]["quality_guard"]["status"] == "not_run"
    provenance = workspace.results / "verifications" / f"{result['id']}.run.json"
    assert json.loads(provenance.read_text())["verify_sha256"] == result["id"]
    response = client.post(
        "/approve",
        json={
            "task_id": task_id,
            "verification_id": result["id"],
            "diff_sha256": result["result"]["diff_sha256"],
            "reviewer": "Fixture reviewer",
        },
    )
    assert response.status_code == 400
    assert not (workspace.results / "approvals").exists()
    missing = client.post("/verify", json={"task_id": task_id, "quality_run_id": "a" * 64})
    assert missing.status_code == 404


def test_bench_view_exposes_measured_counters_without_logs(tmp_path, qwen_tokenizer, config):
    client, _ = client_for(tmp_path, qwen_tokenizer, config)
    # An isolated HTTP contract fixture, never published as evaluation evidence.
    smoke = {
        "status": "passed",
        "model": "fixture",
        "model_revision": "fixture",
        "gpu_type_requested": "fixture",
        "vllm_version": "fixture",
        "finished_at": "fixture",
        "summary": {
            "block_size": 16,
            "kv_cache_size_tokens": 64,
            "hits_delta_per_request": [16],
            "queries_delta_per_request": [32],
        },
        "requests": [{"request": 1, "prompt_tokens": 32}],
        "logs": "PRIVATE_LOG_TAIL",
    }
    path = tmp_path / "eval_results/modal_smoke.json"
    path.parent.mkdir()
    path.write_text(json.dumps(smoke))
    response = client.get("/bench")
    assert response.status_code == 200
    assert "PRIVATE_LOG_TAIL" not in response.text
    assert response.json()["smoke"]["sha256"] == file_sha(path)
    assert response.json()["smoke"]["requests"][0]["cached_tokens"] == 16
    assert response.json()["benchmarks"] == []


def test_public_demo_snapshot_matches_saved_evidence():
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    exported = json.loads((root / "web/public/demo/workspace.json").read_text())
    report_path = root / "eval_results/demo_before_report.json"
    assert exported["report"]["report"] == json.loads(report_path.read_text())
    assert exported["report"]["metadata"]["report_sha256"] == file_sha(report_path)
    assert exported["report"]["metadata"]["dataset"] == ["synthetic-helpdesk"]
    assert exported["bench"]["smoke"]["sha256"] == file_sha(root / "eval_results/modal_smoke.json")
    for artifact in exported["bench"]["benchmarks"]:
        path = root / artifact["source"]
        assert artifact["sha256"] == file_sha(path)
        assert artifact["run"] == json.loads(path.read_text())
    assert any(a["run"]["variant"] == "before" for a in exported["bench"]["benchmarks"])
    from cachekit.api_models import CandidateView, TaskView

    task = TaskView.model_validate(exported["fix"])
    if task.verification_current:
        assert task.verification is not None
        assert task.verification.task_id == task.task.id
    if exported.get("after") is not None:
        candidate = CandidateView.model_validate(exported["after"])
        assert candidate.metadata.source_sha256 == candidate.verification.after_source_sha256
        assert candidate.metadata.task_sha256 == candidate.verification.task_sha256
        import hashlib

        from cachekit.serialization import canonical_json

        assert (
            candidate.metadata.verify_sha256
            == hashlib.sha256((canonical_json(candidate.verification) + "\n").encode()).hexdigest()
        )
        assert (
            candidate.metadata.candidate_report_sha256
            == hashlib.sha256((canonical_json(candidate.report) + "\n").encode()).hexdigest()
        )


def test_current_candidate_is_hash_bound_and_stale_source_is_not_served(
    tmp_path, qwen_tokenizer, config
):
    from fix_helpers import CANDIDATE

    repo, _, _, _ = temporary_bundle(tmp_path, qwen_tokenizer, config)
    for name in ("CHANGELOG.md", "AI_USAGE.md"):
        (repo / name).write_text("Fixture record\n")
    client, workspace = client_for(repo, qwen_tokenizer, config)
    raw = (repo / "data/demo/requests_before.jsonl").read_bytes()
    report_id = client.post("/analyze/upload", content=raw).json()["report_id"]
    assert client.get(f"/reports/{report_id}/after").json() is None
    task_id = client.post(f"/reports/{report_id}/task", json={}).json()["task"]["id"]
    (repo / "demo_app/helpdesk/prompt.py").write_text(CANDIDATE)
    response = client.post("/verify", json={"task_id": task_id})
    assert response.status_code == 200, response.text
    assert response.json()["result"]["quality_guard"]["status"] == "not_run"
    candidate = client.get(f"/reports/{report_id}/after")
    assert candidate.status_code == 200, candidate.text
    assert candidate.json()["approval"] is None
    assert not candidate.json()["verification"]["passed"]
    path = workspace.results / "candidates" / f"{task_id}.json"
    original = path.read_bytes()
    assert candidate.json()["metadata"]["candidate_report_sha256"] == file_sha(path)
    from cachekit.fix.models import FixResult
    from cachekit.ingest.fix import write_model
    from cachekit.ingest.fix_workflow import load_bundle
    from fix_helpers import fake_quality

    baseline, _ = load_bundle(workspace.task_path(task_id))
    quality = fake_quality(repo, workspace.task_path(task_id).parent, baseline, qwen_tokenizer)
    quality_path = repo / "eval_results/quality_guard/unit-fixture.json"
    write_model(quality_path, quality)
    verified = client.post(
        "/verify", json={"task_id": task_id, "quality_run_id": file_sha(quality_path)}
    )
    assert verified.status_code == 200, verified.text
    view = client.get(f"/fix/{task_id}").json()
    assert len(view["quality_outputs"]) == 5
    assert {o["id"] for o in view["quality_outputs"]} == {o.id for o in quality.outputs}
    assert view["approval"] is None
    verified_id = verified.json()["id"]
    approved = client.post(
        "/approve",
        json={
            "task_id": task_id,
            "verification_id": verified_id,
            "diff_sha256": verified.json()["result"]["diff_sha256"],
            "reviewer": "Unit fixture reviewer",
            "review_ids": [],
        },
    )
    assert approved.status_code == 200, approved.text
    assert client.get(f"/fix/{task_id}").json()["approval"] == approved.json()
    assert client.get(f"/reports/{report_id}/after").json()["approval"] == approved.json()
    approval_path = workspace.results / "approvals" / f"{verified_id}.json"
    approval_bytes = approval_path.read_bytes()
    altered = approved.json() | {"quality_result_sha256": "0" * 64}
    approval_path.write_text(json.dumps(altered))
    assert client.get(f"/fix/{task_id}").json()["approval"] is None
    assert client.get(f"/reports/{report_id}/after").json()["approval"] is None
    approval_path.write_bytes(approval_bytes)
    reference = FixResult(
        task_id="f" * 24, status="finished", pr_url="https://github.com/mohi-devhub/cachekit/pull/2"
    )
    write_model(workspace.task_path(task_id).parent / "handoff_reference.json", reference)
    view = client.get(f"/fix/{task_id}").json()
    assert view["handoff"]["reference_only"]
    assert view["handoff"]["task_id"] == reference.task_id != task_id
    path.write_bytes(original + b" ")
    assert client.get(f"/reports/{report_id}/after").status_code == 400
    path.write_bytes(original)
    (repo / "unrelated.py").write_text("changed source\n")
    assert client.get(f"/reports/{report_id}/after").json() is None
    assert client.get(f"/fix/{task_id}").json()["approval"] is None


def test_real_before_benchmark_is_available_without_smoke_file(tmp_path, qwen_tokenizer, config):
    import shutil
    from pathlib import Path

    client, _ = client_for(tmp_path, qwen_tokenizer, config)
    root = Path(__file__).resolve().parents[2]
    out = tmp_path / "eval_results/before_replay.json"
    out.parent.mkdir()
    shutil.copyfile(root / "eval_results/before_replay.json", out)
    response = client.get("/bench")
    assert response.status_code == 200, response.text
    assert response.json()["smoke"] is None
    assert not response.json()["comparison_ready"]
    assert response.json()["benchmarks"][0]["sha256"] == file_sha(out)
    before = json.loads(out.read_text())
    assert response.json()["benchmarks"][0]["run"]["summary"] == before["summary"]
    # Isolated metadata-compatibility fixture; this copy is never published as a measurement.
    before["variant"] = "after"
    (out.parent / "after_replay.json").write_text(json.dumps(before))
    assert client.get("/bench").json()["comparison_ready"]
    before["schedule_sha256"] = "0" * 64
    (out.parent / "after_replay.json").write_text(json.dumps(before))
    assert not client.get("/bench").json()["comparison_ready"]
