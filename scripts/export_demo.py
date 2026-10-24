"""Export reviewed synthetic views, never arbitrary API uploads or raw inputs."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "engine"), str(ROOT)]

from cachekit.api_models import BenchView  # noqa: E402
from cachekit.ingest.config import load_config  # noqa: E402
from cachekit.ingest.fix_workflow import load_bundle  # noqa: E402
from cachekit.ingest.workspace import Workspace  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id")
    options = parser.parse_args()
    workspace = Workspace(ROOT, ROOT / "data/tokenizer", load_config())
    report = workspace.bundle("demo-before")
    if report.metadata.dataset != ["synthetic-helpdesk"] or report.report.routes != [
        "helpdesk.answer"
    ]:
        raise ValueError("Only the reviewed public synthetic helpdesk report can be exported")
    task = None
    path = ROOT / "data/fixes/demo/fix_task.json"
    if options.task_id:
        path = workspace.task_path(options.task_id)
    if path.is_file():
        baseline, _ = load_bundle(path)
        if baseline.before_requests_sha256 != report.report.input_sha256:
            raise ValueError("Only the matching synthetic helpdesk task can be exported")
        task = workspace.task_view(baseline.task.id)
    try:
        current_candidate = workspace.candidate_view("demo-before")
        after = current_candidate.model_dump(mode="json") if current_candidate else None
    except FileNotFoundError:
        after = None
    bench = BenchView.model_validate(workspace.bench())
    before_run = next((b.run for b in bench.benchmarks if b.run.variant == "before"), None)
    for artifact in bench.benchmarks:
        if artifact.run.variant == "before":
            if artifact.run.input_sha256 != report.report.input_sha256:
                raise ValueError("Only the reviewed synthetic benchmark may be exported")
        elif (
            before_run is None
            or before_run.recorded_inputs_sha256 is None
            or artifact.run.recorded_inputs_sha256 != before_run.recorded_inputs_sha256
        ):
            raise ValueError("AFTER must use the same original synthetic inputs")
    output = {
        "report": report.model_dump(mode="json"),
        "after": after,
        "fix": task.model_dump(mode="json") if task else None,
        "bench": bench.model_dump(mode="json"),
    }
    # Raw baselines, dataset reports and GPU log tails are deliberately omitted.
    path = ROOT / "web/public/demo/workspace.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    )
    print("Exported reviewed synthetic report, redacted task status and measured smoke counters.")


if __name__ == "__main__":
    main()
