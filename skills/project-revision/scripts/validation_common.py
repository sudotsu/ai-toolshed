#!/usr/bin/env python3
"""Shared, dependency-free validation helpers for project-revision artifacts."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

class _HardenedList(list):
    """List subclass used to recursively normalize untrusted JSON.

    It intentionally retains normal list equality and remains unhashable.
    """

    __slots__ = ()


class _HardenedDict(dict):
    """Dict subclass that retains normal value equality and remains unhashable."""

    __slots__ = ()


def harden_json(value):
    """Recursively normalize JSON containers while preserving value equality."""
    if isinstance(value, dict):
        return _HardenedDict((key, harden_json(item)) for key, item in value.items())
    if isinstance(value, list):
        return _HardenedList(harden_json(item) for item in value)
    return value

ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*-\d{3}$")
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


def canonical_digest(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def read_text(path: Path, label: str, errors: list[str], *, require_heading: bool = True) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read {label}: {exc}")
        return ""
    if not text.strip():
        errors.append(f"{label} is empty")
    elif require_heading and not re.search(r"^#\s+\S", text, re.MULTILINE):
        errors.append(f"{label} is missing a top-level Markdown heading")
    return text


def load_object(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        errors.append(f"cannot read {label}: {exc}")
        return None
    if not isinstance(raw, dict):
        errors.append(f"{label} must contain an object")
        return None
    try:
        return harden_json(raw)
    except RecursionError as exc:
        errors.append(f"cannot read {label}: {exc}")
        return None


def exact_keys(value: Any, expected: set[str], label: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return False
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        errors.append(f"{label} missing keys: {', '.join(missing)}")
    if extra:
        errors.append(f"{label} has unexpected keys: {', '.join(extra)}")
    return not missing and not extra


def require_nonempty_string(value: Any, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")
        return False
    return True


def validate_timestamp(value: Any, label: str, errors: list[str]) -> None:
    if not require_nonempty_string(value, label, errors):
        return
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be an ISO-8601 timestamp")
        return
    if parsed.tzinfo is None:
        errors.append(f"{label} must include a timezone")


def require_string_list(
    value: Any,
    label: str,
    errors: list[str],
    *,
    allow_empty: bool = True,
    safe_paths: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label} must be an array")
        return []
    cleaned: list[str] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{label} item {index} must be a non-empty string")
            continue
        item = item.strip()
        cleaned.append(item)
        if safe_paths and not is_safe_relative_path(item):
            errors.append(f"{label} item {index} is not a safe relative project path: {item!r}")
    duplicates = sorted(item for item, count in Counter(cleaned).items() if count > 1)
    if duplicates:
        errors.append(f"{label} contains duplicates: {', '.join(duplicates)}")
    if not allow_empty and not cleaned:
        errors.append(f"{label} must contain at least one item")
    for index, item in enumerate(cleaned, start=1):
        reject_round_trip_delimiters(item, f"{label} item {index}", errors)
    return cleaned


# Markdown views join list values with " | " and acceptance results with " => ".
# The validator parses those views back and compares them to the JSON, so a value
# containing either delimiter cannot survive the round trip. Reject it explicitly
# rather than letting it surface as a confusing structural parse error.
ROUND_TRIP_DELIMITERS = (" | ", " => ")


def reject_round_trip_delimiters(value: str, label: str, errors: list[str]) -> None:
    for delimiter in ROUND_TRIP_DELIMITERS:
        if delimiter in value:
            errors.append(
                f"{label} must not contain {delimiter!r}; it is a Markdown round-trip "
                f"delimiter and would corrupt the generated view"
            )
    if value.strip() == "None":
        errors.append(
            f"{label} must not be the literal 'None'; that value marks an empty list "
            f"in the Markdown view and cannot be distinguished from one"
        )


def is_safe_relative_path(value: str) -> bool:
    if not value or "\\" in value or "\x00" in value:
        return False
    if re.match(r"^[A-Za-z]:", value):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)


def split_pipe(value: str) -> list[str]:
    stripped = value.strip()
    if stripped == "None":
        return []
    return [item.strip() for item in stripped.split(" | ") if item.strip()]


def marker(text: str, label: str, errors: list[str]) -> str | None:
    match = re.search(rf"^\*\*{re.escape(label)}:\*\*\s*(\S(?:.*\S)?)\s*$", text, re.MULTILINE)
    if not match:
        errors.append(f"missing exact marker: **{label}:**")
        return None
    return match.group(1)


def markdown_section(text: str, heading: str, level: int = 2) -> str | None:
    prefix = "#" * level
    # Terminate at the next heading of this level *or higher* (fewer #). Stopping
    # only at the same level lets a level-2 section absorb a following level-1
    # heading and all of its content.
    pattern = rf"^{re.escape(prefix)} {re.escape(heading)}\s*$([\s\S]*?)(?=^#{{1,{level}}} |\Z)"
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else None


def parse_labeled_fields(section: str) -> dict[str, str]:
    return {
        match.group(1).strip(): match.group(2).strip()
        for match in re.finditer(r"^- \*\*(.+?):\*\*\s*(.*)$", section, re.MULTILINE)
    }
