# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
#   "icalendar",
#   "recurring-ical-events",
#   "tzdata",
# ]
# ///
"""Fetch private iCal feeds and print today's and tomorrow's events."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import recurring_ical_events
import requests
from icalendar import Calendar


DEFAULT_CONFIG = Path(__file__).with_name("calendars.local.json")
SECRET_RE = re.compile(r"private-[0-9a-f]+", re.IGNORECASE)


Event = dict[str, Any]


def mask_secret(value: object) -> str:
    """Mask private Google Calendar URL tokens in emitted text."""
    return SECRET_RE.sub("private-***", str(value))


def parse_anchor_date(value: str) -> date:
    """Parse an ISO date for argparse."""
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected YYYY-MM-DD") from exc


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--date", type=parse_anchor_date, default=None)
    parser.add_argument("--format", choices=("json", "md"), default="json")
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    """Read the JSON calendar config."""
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Config root must be a JSON object.")
    return data


def as_list(value: object) -> list[Any]:
    """Return a possibly scalar iCalendar value as a list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def clean_attendee(value: Any) -> str:
    """Extract a display name or email address from an attendee field."""
    params = getattr(value, "params", {})
    common_name = params.get("CN") if params else None
    if common_name:
        return str(common_name)

    address = str(value)
    if address.lower().startswith("mailto:"):
        return address[7:]
    return address


def event_text(component: Any, name: str, default: str = "") -> str:
    """Return an iCalendar component property as text."""
    value = component.get(name)
    if value is None:
        return default
    return str(value)


def event_optional_text(component: Any, name: str) -> str | None:
    """Return an optional iCalendar component property as text."""
    value = component.get(name)
    if value is None:
        return None
    text = str(value)
    return text if text else None


def normalize_datetime(value: datetime, tz: ZoneInfo) -> datetime:
    """Convert a datetime to the configured timezone."""
    if value.tzinfo is None:
        return value.replace(tzinfo=tz)
    return value.astimezone(tz)


def normalize_event(component: Any, label: str, tz: ZoneInfo) -> Event:
    """Convert an expanded VEVENT into the output schema."""
    start_raw = component.decoded("dtstart")
    end_prop = component.get("dtend")
    end_raw = component.decoded("dtend") if end_prop is not None else start_raw
    all_day = isinstance(start_raw, date) and not isinstance(start_raw, datetime)

    if all_day:
        start = start_raw.isoformat()
        end = end_raw.isoformat() if isinstance(end_raw, date) else str(end_raw)
        start_hm = None
        end_hm = None
    else:
        start_dt = normalize_datetime(start_raw, tz)
        end_dt = normalize_datetime(end_raw, tz)
        start = start_dt.isoformat()
        end = end_dt.isoformat()
        start_hm = start_dt.strftime("%H:%M")
        end_hm = end_dt.strftime("%H:%M")

    attendees = [clean_attendee(item) for item in as_list(component.get("attendee"))]
    return {
        "summary": event_text(component, "summary"),
        "all_day": all_day,
        "start": start,
        "end": end,
        "start_hm": start_hm,
        "end_hm": end_hm,
        "attendees": attendees,
        "attendees_count": len(attendees),
        "location": event_optional_text(component, "location"),
        "calendar": label,
        "uid": event_text(component, "uid"),
    }


def event_start_date(event: Event) -> date:
    """Return the JST start date used for day assignment."""
    start = str(event["start"])
    if event["all_day"]:
        return date.fromisoformat(start)
    return datetime.fromisoformat(start).date()


def sort_events(events: list[Event]) -> list[Event]:
    """Sort all-day events first, then timed events by start time."""
    return sorted(
        events,
        key=lambda item: (
            0 if item["all_day"] else 1,
            item["start_hm"] or "00:00",
            str(item["summary"]),
        ),
    )


def fetch_calendar_events(
    calendar_config: dict[str, Any],
    window_start: datetime,
    window_end: datetime,
    tz: ZoneInfo,
) -> list[Event]:
    """Fetch, parse, and expand one calendar feed."""
    label = str(calendar_config.get("label", ""))
    url = str(calendar_config.get("url", ""))
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    calendar = Calendar.from_ical(response.content)
    expanded = recurring_ical_events.of(calendar).between(window_start, window_end)
    return [normalize_event(component, label, tz) for component in expanded]


def build_result(config: dict[str, Any], anchor: date) -> tuple[dict[str, Any], int]:
    """Fetch configured calendars and build the JSON output object."""
    timezone = str(config.get("timezone", "Asia/Tokyo"))
    tz = ZoneInfo(timezone)
    calendars = config.get("calendars", [])
    if not isinstance(calendars, list):
        calendars = []

    tomorrow = anchor + timedelta(days=1)
    window_start = datetime.combine(anchor, time(0, 0, 0), tzinfo=tz)
    window_end = datetime.combine(tomorrow, time(23, 59, 59), tzinfo=tz)

    today_events: list[Event] = []
    tomorrow_events: list[Event] = []
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()
    success_count = 0

    for item in calendars:
        if not isinstance(item, dict):
            errors.append("Skipped invalid calendar entry.")
            continue
        label = str(item.get("label", ""))
        try:
            events = fetch_calendar_events(item, window_start, window_end, tz)
            success_count += 1
        except Exception as exc:  # noqa: BLE001 - calendar failures must not abort.
            url = item.get("url", "")
            errors.append(mask_secret(f"Calendar '{label}' failed ({url}): {exc}"))
            continue

        for event in events:
            key = (str(event["uid"]), str(event["start"]))
            if key in seen:
                continue
            seen.add(key)

            start_day = event_start_date(event)
            if start_day == anchor:
                today_events.append(event)
            elif start_day == tomorrow:
                tomorrow_events.append(event)

    result = {
        "generated_for": anchor.isoformat(),
        "timezone": timezone,
        "today": sort_events(today_events),
        "tomorrow": sort_events(tomorrow_events),
        "errors": errors,
    }
    return result, success_count


def attendee_suffix(event: Event) -> str:
    """Return the attendee-count suffix for Markdown output."""
    count = int(event["attendees_count"])
    return f" ({count}名)" if count else ""


def render_md_event(event: Event) -> list[str]:
    """Render one event as Markdown lines."""
    summary = str(event["summary"])
    if event["all_day"]:
        line = f"- 終日 **{summary}**{attendee_suffix(event)}"
    else:
        line = (
            f"- {event['start_hm']}-{event['end_hm']} "
            f"**{summary}**{attendee_suffix(event)}"
        )

    lines = [line]
    attendees = event["attendees"]
    if attendees:
        lines.append(f"  - 参加者: {', '.join(str(item) for item in attendees)}")
    return lines


def render_md_day(title: str, events: list[Event]) -> list[str]:
    """Render one day section as Markdown."""
    lines = [title]
    if not events:
        lines.append("- 予定なし")
        return lines

    for event in events:
        lines.extend(render_md_event(event))
    return lines


def render_md(result: dict[str, Any]) -> str:
    """Render the output object as Markdown."""
    lines = render_md_day("### 📅 今日の予定", result["today"])
    lines.append("")
    lines.extend(render_md_day("### 📅 明日の予定", result["tomorrow"]))
    return "\n".join(lines)


def _force_utf8_stdio() -> None:
    """Force UTF-8 on stdio so Windows cp932 consoles can print emoji/JP text."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def main() -> int:
    """CLI entry point."""
    _force_utf8_stdio()
    args = parse_args()

    try:
        config = load_config(args.config)
    except FileNotFoundError as exc:
        print(mask_secret(exc), file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - config errors must be clear.
        print(mask_secret(f"Failed to read config {args.config}: {exc}"), file=sys.stderr)
        return 1

    timezone = str(config.get("timezone", "Asia/Tokyo"))
    tz = ZoneInfo(timezone)
    anchor = args.date or datetime.now(tz).date()
    result, success_count = build_result(config, anchor)

    if args.format == "json" or success_count == 0:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_md(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
