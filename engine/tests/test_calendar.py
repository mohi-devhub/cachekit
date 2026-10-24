import json
from datetime import UTC, datetime

import pytest
from cachekit.calendar import calendar_context
from cachekit.fix.content import check_content
from cachekit.models import Message, RequestRecord

NOW = datetime(2026, 10, 24, 12, tzinfo=UTC)


def context(message, **kwargs):
    return calendar_context(
        message=message,
        history=kwargs.get("history", []),
        documents=kwargs.get("documents", []),
        now=kwargs.get("now", NOW),
        window_days=kwargs.get("window_days", 30),
    )


def facts(message, **kwargs):
    return json.loads(context(message, **kwargs).split("\n", 1)[1])


@pytest.mark.parametrize(
    "mentioned,clock,elapsed,exceeds,future",
    [
        ("2026-09-20", NOW, 34, True, False),
        ("2024-02-29", datetime(2024, 3, 30, tzinfo=UTC), 30, False, False),
        ("2024-02-29", datetime(2024, 3, 31, tzinfo=UTC), 31, True, False),
        ("2026-10-24", NOW, 0, False, False),
        ("2026-10-25", NOW, -1, False, True),
    ],
)
def test_calendar_arithmetic(mentioned, clock, elapsed, exceeds, future):
    result = facts("Mentioned date: " + mentioned, now=clock)["date_calculations"][0]
    assert result["elapsed_calendar_days"] == elapsed
    assert result["exceeds_calendar_window"] is exceeds
    assert result["date_in_future"] is future


def test_mentions_are_deduplicated_with_sources_and_invalid_dates_are_explicit():
    result = facts(
        "2026-09-20 and invalid 2026-02-30", history=["2026-09-20"], documents=["2026-09-20"]
    )
    assert len(result["date_calculations"]) == 1
    assert result["date_calculations"][0]["source_fields"] == [
        "history[0]",
        "message",
        "retrieved_docs[0]",
    ]
    assert result["invalid_date_mentions"] == [{"date": "2026-02-30", "source_fields": ["message"]}]
    assert context("No calendar date") == ""
    assert context("01/02/2026") == ""  # Ambiguous numeric dates are not interpreted.
    assert "eligibility" not in result


@pytest.mark.parametrize("window", [0, -1, True, 1.5])
def test_calendar_window_requires_positive_integer(window):
    with pytest.raises(ValueError, match="positive integer"):
        context("2026-09-20", window_days=window)


def test_calendar_requires_recorded_timezone_and_keeps_its_calendar_date():
    with pytest.raises(ValueError, match="timezone-aware"):
        context("2026-09-20", now=datetime(2026, 10, 24))
    clock = datetime.fromisoformat("2026-10-24T00:30:00+05:30")
    result = facts("2026-10-23", now=clock)
    assert result["as_of_date"] == "2026-10-24"
    assert result["date_calculations"][0]["elapsed_calendar_days"] == 1


def test_content_requires_declared_exact_calendar_in_system_and_preserves_originals():
    before = RequestRecord(
        id="a",
        ts=0,
        messages=[
            Message(role="system", content="Original policy"),
            Message(role="user", content="Delivered 2026-09-20"),
        ],
    )
    block = context(before.messages[-1].content)
    after = before.model_copy(deep=True)
    after.messages[0].content += "\n" + block
    expected = {"a": block}
    assert not check_content([before], [after], []).passed
    assert check_content([before], [after], [], allowed_calendar_context=expected).passed
    for changed in [
        after.messages[0].content.replace(
            '"elapsed_calendar_days":34', '"elapsed_calendar_days":4'
        ),
        after.messages[0].content + "\n" + block,
        block,  # The enrichment cannot replace original policy.
        "Original policy",  # A declared required calculation cannot be omitted.
    ]:
        bad = after.model_copy(deep=True)
        bad.messages[0].content = changed
        assert not check_content([before], [bad], [], allowed_calendar_context=expected).passed
    wrong_role = before.model_copy(deep=True)
    wrong_role.messages[-1].content += "\n" + block
    assert not check_content([before], [wrong_role], [], allowed_calendar_context=expected).passed
