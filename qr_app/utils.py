from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TIMESTAMP_FORMATS = (
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",
)


def parse_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    text = str(value).strip()
    if not text:
        return None

    # SQLite CURRENT_TIMESTAMP values are stored in UTC.
    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        pass

    for timestamp_format in TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(text, timestamp_format).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def time_ago(value: Any) -> str:
    moment = parse_timestamp(value)
    if moment is None:
        return ""
    diff = datetime.now(timezone.utc) - moment
    seconds = diff.total_seconds()
    if seconds < 0:
        if abs(seconds) < 60:
            return "just now"
        return "in the future"
    if seconds < 60:
        return "just now"
    minutes = seconds / 60
    if minutes < 60:
        minute_count = int(minutes)
        suffix = "min" if minute_count == 1 else "mins"
        return f"{minute_count} {suffix} ago"
    hours = minutes / 60
    if hours < 24:
        hour_count = int(hours)
        suffix = "hr" if hour_count == 1 else "hrs"
        return f"{hour_count} {suffix} ago"
    days = hours / 24
    if days < 30:
        day_count = int(days)
        suffix = "day" if day_count == 1 else "days"
        return f"{day_count} {suffix} ago"
    return moment.strftime("%b %d, %Y")


def get_initials(name: str) -> str:
    parts = [part[0].upper() for part in (name or "").split() if part]
    return "".join(parts[:2]) or "QR"


def read_binary_file(path: Path) -> bytes:
    return path.read_bytes()
