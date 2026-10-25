"""Removing template documents must not break a fresh source-fix baseline."""

from cachekit.ingest.fix_workflow import default_allowed_files


def test_default_scope_does_not_require_template_records(tmp_path):
    assert default_allowed_files(tmp_path) == ["demo_app/helpdesk/prompt.py"]


def test_existing_local_records_can_still_be_declared(tmp_path):
    (tmp_path / "DECISIONS.md").write_text("Local decisions\n")
    assert default_allowed_files(tmp_path) == ["demo_app/helpdesk/prompt.py", "DECISIONS.md"]
