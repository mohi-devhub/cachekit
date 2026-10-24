"""Deterministic arithmetic on ISO calendar dates mentioned in supplied text."""

import re
from datetime import date, datetime

from cachekit.serialization import canonical_json

HEADER = "Computed calendar facts for dates mentioned in the input; date sources are unverified."
DATE = re.compile(r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)")


def calendar_context(
    *, message: str, history: list[str], documents: list[str], now: datetime, window_days: int
) -> str:
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
        return ""
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
                "date_in_future": elapsed < 0,
                "source_fields": sorted(labels),
            }
        )
    return (
        HEADER
        + "\n"
        + canonical_json(
            {
                "as_of_date": now.date().isoformat(),
                "calendar_window_days": window_days,
                "date_calculations": calculations,
                "invalid_date_mentions": invalid,
            }
        )
    )
