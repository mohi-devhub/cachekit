import hashlib
import json
from pathlib import Path

import pytest
from cachekit.cli import app
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[2]
BEFORE = ROOT / "eval_results" / "before_replay.json"
AFTER = ROOT / "eval_results" / "after_confirmation_replay.json"


def compare(before: Path, after: Path, out: Path):
    return CliRunner().invoke(app, ["compare", str(before), str(after), "--out", str(out)])


def edited_after(tmp_path: Path, edit) -> Path:
    data = json.loads(AFTER.read_text())
    edit(data)
    path = tmp_path / "after.json"
    path.write_text(json.dumps(data))
    return path


def test_saved_pair_reports_medians_ranges_and_hashes(tmp_path):
    out = tmp_path / "comparison.md"
    result = compare(BEFORE, AFTER, out)
    assert result.exit_code == 0, result.output
    text = out.read_text()
    hit_row = "| Measured cache-hit rate | 0.304% (0.304%–0.304%) | 80.690% (80.690%–80.690%) |"
    assert hit_row in text
    assert "| Client TTFT p50 | 2.014 s (" in text
    assert "| 1.425 s (" in text
    assert "$0.7893 ($0.7745–$0.8328)" in text
    assert "$0.7050 ($0.7038–$0.7075)" in text
    for path in (BEFORE, AFTER):
        assert hashlib.sha256(path.read_bytes()).hexdigest() in text
    assert "## Limitations" in text


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("schedule_sha256", "0" * 64, "schedule differs"),
        ("recorded_inputs_sha256", "1" * 64, "recorded inputs differ"),
        ("n_requests", 26, "request count differs"),
    ],
)
def test_unmatched_pair_is_rejected_without_output(tmp_path, field, value, reason):
    after = edited_after(tmp_path, lambda data: data.update({field: value}))
    out = tmp_path / "comparison.md"
    result = compare(BEFORE, after, out)
    assert result.exit_code == 1
    assert reason in result.output
    assert not out.exists()


def test_unmatched_settings_and_profile_are_rejected(tmp_path):
    def edit(data):
        data["settings"]["max_tokens"] = 128
        data["deployment"]["gpu"] = "A100"

    out = tmp_path / "comparison.md"
    result = compare(BEFORE, edited_after(tmp_path, edit), out)
    assert result.exit_code == 1
    assert "replay settings differ" in result.output
    assert "deployment profile differs" in result.output
    assert not out.exists()


def test_swapped_variants_are_rejected(tmp_path):
    out = tmp_path / "comparison.md"
    result = compare(AFTER, BEFORE, out)
    assert result.exit_code == 1
    assert "need before/after" in result.output


def test_missing_cost_is_explicit_not_zero(tmp_path):
    def edit(data):
        data["runs"][1]["gpu_window_usd_per_1000"] = None

    out = tmp_path / "comparison.md"
    result = compare(BEFORE, edited_after(tmp_path, edit), out)
    assert result.exit_code == 0, result.output
    row = next(line for line in out.read_text().splitlines() if line.startswith("| GPU-window"))
    assert row.endswith("| missing in 1/3 repetitions |")
    assert "$0.0000" not in row


def test_invalid_artifact_is_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{}")
    result = compare(BEFORE, bad, tmp_path / "comparison.md")
    assert result.exit_code == 1
    assert "not a valid BenchmarkRun" in result.output
