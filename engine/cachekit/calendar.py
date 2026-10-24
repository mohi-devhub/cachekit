"""Deterministic arithmetic on ISO calendar dates mentioned in supplied text."""

import re
from datetime import date, datetime

from cachekit.serialization import canonical_json

HEADER = (
    "Computed calendar timing from unverified date mentions. Use within_window for calendar "
    "timing only; original product eligibility and action-authorization checks remain in force."
)
DATE = re.compile(r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)")


def calendar_facts(
    *, message: str, history: list[str], documents: list[str], now: datetime, window_days: int
) -> dict | None:
    """Compare mentioned dates with the explicit clock/window; grant no eligibility."""
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Calendar arithmetic requires a timezone-aware recorded clock")
    if type(window_days) is not int or window_days <= 0:
        raise ValueError("Calendar window must be a positive integer")
    sources = [("message", message)]
    sources += [(f"history[{i}]", text) for i, text in enumerate(history)]
    sources += [(f"retrieved_docs[{i}]", text) for i, text in enumerate(documents)]
    mentions: dict[str, set[str]] = {}
    for label, text in sources:
        for value in DATE.findall(text):
            mentions.setdefault(value, set()).add(label)
    if not mentions:
        return None
    calculations, invalid = [], []
    for value, labels in sorted(mentions.items()):
        try:
            mentioned = date.fromisoformat(value)
        except ValueError:
            invalid.append({"date": value, "source_fields": sorted(labels)})
            continue
        elapsed = (now.date() - mentioned).days
        calculations.append(
            {
                "date": value,
                "elapsed_calendar_days": elapsed,
                "exceeds_calendar_window": elapsed > window_days,
                "within_calendar_window": 0 <= elapsed <= window_days,
                "date_in_future": elapsed < 0,
                "source_fields": sorted(labels),
            }
        )
    return {
        "as_of_date": now.date().isoformat(),
        "calendar_window_days": window_days,
        "date_calculations": calculations,
        "invalid_date_mentions": invalid,
    }


def calendar_context(
    *, message: str, history: list[str], documents: list[str], now: datetime, window_days: int
) -> str:
    """Present each calculated date as one flat record with its original source labels."""
    facts = calendar_facts(
        message=message, history=history, documents=documents, now=now, window_days=window_days
    )
    if facts is None:
        return ""
    rows = []
    for item in facts["date_calculations"]:
        row = {
            "as_of_date": facts["as_of_date"],
            "mentioned_date": item["date"],
            "elapsed_calendar_days": item["elapsed_calendar_days"],
            "calendar_window_days": facts["calendar_window_days"],
            "within_window": item["within_calendar_window"],
            "source_fields": item["source_fields"],
        }
        if item["date_in_future"]:
            row["date_in_future"] = True
        rows.append(canonical_json(row))
    for item in facts["invalid_date_mentions"]:
        rows.append(
            canonical_json({"invalid_date": item["date"], "source_fields": item["source_fields"]})
        )
    return HEADER + "\n" + "\n".join(rows)
