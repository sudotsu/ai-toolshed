#!/usr/bin/env python3
"""Shared constants and safe helpers for brand-revision scripts."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUTHORITY_IDS = (
    "AUTH-REPOSITORY-EDIT",
    "AUTH-CONTENT-EDIT",
    "AUTH-ASSET-EDIT",
    "AUTH-CONFIGURATION-EDIT",
    "AUTH-CMS-MUTATION",
    "AUTH-COMMIT",
    "AUTH-PUSH",
    "AUTH-PULL-REQUEST",
    "AUTH-MERGE",
    "AUTH-DEPLOY",
    "AUTH-PUBLISH",
    "AUTH-SOCIAL-PROFILE",
    "AUTH-BUSINESS-LISTING",
    "AUTH-OUTREACH",
    "AUTH-PURCHASE",
)

DELIVERY_KEYS = (
    "committed",
    "pushed",
    "pull_request",
    "merged",
    "deployed",
    "published",
    "social_profile_changes",
    "business_listing_changes",
    "outreach",
)

EVIDENCE_LEVELS = (
    "source-inspection",
    "rendered-experience",
    "published-channel",
    "audience-observation",
    "first-party-measurement",
    "business-outcome",
)

EVIDENCE_METHODS = (
    "source-inspection",
    "build-unit",
    "rendered-browser",
    "visual-inspection",
    "claim-verification",
    "published-fetch",
    "profile-observation",
    "collateral-observation",
    "audience-test",
    "customer-research",
    "first-party-analysis",
    "business-record-analysis",
    "owner-authorization",
    "external-research",
)

PLACEHOLDER_TOKENS = (
    "TODO",
    "TBD",
    "placeholder",
    "lorem ipsum",
    "<fill",
    "coming soon",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"missing required file: {path.name}"]
    except json.JSONDecodeError as exc:
        return None, [f"invalid JSON in {path.name}: {exc}"]
    except OSError as exc:
        return None, [f"could not read {path.name}: {exc}"]


def parse_frontmatter_name(text: str) -> str | None:
    """Return the single YAML-frontmatter name scalar, without matching body prose."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None

    values: list[str] = []
    for raw in lines[1:end]:
        match = re.match(r"^\s*name\s*:\s*(.*?)\s*$", raw)
        if not match:
            continue
        value = match.group(1).strip()
        if " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values.append(value)
    return values[0] if len(values) == 1 and values[0] else None


def locate_brand_teardown_validator() -> Path | None:
    env = os.environ.get("BRAND_TEARDOWN_SKILL")
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env))
    here = Path(__file__).resolve()
    try:
        candidates.append(here.parents[2] / "brand-teardown")
    except IndexError:
        pass
    candidates.extend(
        [
            Path.home() / ".agents" / "skills" / "brand-teardown",
            Path.home() / ".claude" / "skills" / "brand-teardown",
        ]
    )
    seen: set[Path] = set()
    for root in candidates:
        try:
            root = root.expanduser().resolve()
        except OSError:
            continue
        if root in seen:
            continue
        seen.add(root)
        skill = root / "SKILL.md"
        validator = root / "scripts" / "validate_brand_teardown.py"
        if not skill.is_file() or not validator.is_file():
            continue
        try:
            text = skill.read_text(encoding="utf-8")
        except OSError:
            continue
        if parse_frontmatter_name(text) == "brand-teardown":
            return validator
    return None


def run_upstream_validator(teardown_dir: Path) -> tuple[bool, str]:
    validator = locate_brand_teardown_validator()
    if validator is None:
        return False, "could not locate installed brand-teardown validator"
    try:
        proc = subprocess.run(
            [sys.executable, str(validator), str(teardown_dir.resolve())],
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"brand-teardown validator could not run: {exc}"
    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        return False, output or f"brand-teardown validator exited {proc.returncode}"
    return True, output or "passed"


def as_dict(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def as_list(value: Any) -> list[Any] | None:
    return value if isinstance(value, list) else None


def unique_strings(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(x, str) and x for x in value) and len(value) == len(set(value))