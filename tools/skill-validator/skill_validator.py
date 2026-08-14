#!/usr/bin/env python3
"""Reusable package validator for AI Toolshed skills.

A single, generic replacement for the per-skill ``validate_skill.py`` scripts.
Each skill declares its package contract in a ``skill-manifest.json`` file; this
tool reads that manifest and runs the same integrity checks against every skill:

1. The manifest is well-formed.
2. Every ``required_files`` entry exists (and no ``forbidden_files`` do).
3. ``SKILL.md`` frontmatter satisfies the Claude Code spec and the manifest's
   own rules (name matches, kebab-case, length bounds, no angle brackets, key
   policy).
4. Every relative Markdown link resolves to a file inside the skill.
5. Every ``scripts/*.py`` file byte-compiles.
6. Each declared regression-test command runs green.

The validator has no third-party dependencies (standard library only).

Usage::

    python3 skill_validator.py                      # validate every bundled skill
    python3 skill_validator.py <skill-dir> [...]    # validate specific skills
    python3 skill_validator.py <skills-root>        # validate each skill under a root
    python3 skill_validator.py --no-tests <skill>   # skip the regression-test step

Exit status is 0 when every validated skill passes and 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

MANIFEST_NAME = "skill-manifest.json"

# The full set of frontmatter keys the Claude Code skill spec permits.
CLAUDE_ALLOWED_KEYS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}
# Named frontmatter key policies a manifest may select.
FRONTMATTER_POLICIES = {"name-description-only", "claude-standard"}

DEFAULT_DESCRIPTION_MIN_LENGTH = 40
DESCRIPTION_MAX_LENGTH = 1024
NAME_MAX_LENGTH = 64
DEFAULT_TEST_TIMEOUT_SECONDS = 180

MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_BLOCK = re.compile(r"^---\n([\s\S]*?)\n---\n")
TOP_LEVEL_KEY = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_-]*):")


class ManifestError(Exception):
    """Raised when a manifest cannot be loaded or is structurally invalid."""


def _within_skill(root: Path, rel: str) -> bool:
    """True if ``rel`` is a relative path that stays inside ``root``.

    Rejects absolute paths and any ``..`` traversal or symlink target that
    resolves outside the skill directory.
    """
    candidate = Path(rel)
    if candidate.is_absolute():
        return False
    try:
        (root / candidate).resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def load_manifest(root: Path) -> dict[str, Any]:
    """Load and structurally validate ``skill-manifest.json`` under ``root``."""
    path = root / MANIFEST_NAME
    if not path.is_file():
        raise ManifestError(f"missing {MANIFEST_NAME}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestError(f"{MANIFEST_NAME} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ManifestError(f"{MANIFEST_NAME} must be a JSON object")

    if data.get("schema_version") != 1:
        raise ManifestError("manifest schema_version must be 1")

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ManifestError("manifest name must be a non-empty string")

    required = data.get("required_files")
    if not isinstance(required, list) or not required or not all(
        isinstance(item, str) and item for item in required
    ):
        raise ManifestError("manifest required_files must be a non-empty list of strings")

    forbidden = data.get("forbidden_files", [])
    if not isinstance(forbidden, list) or not all(
        isinstance(item, str) and item for item in forbidden
    ):
        raise ManifestError("manifest forbidden_files must be a list of strings")

    frontmatter = data.get("frontmatter", {})
    if not isinstance(frontmatter, dict):
        raise ManifestError("manifest frontmatter must be an object")
    policy = frontmatter.get("keys", "claude-standard")
    if policy not in FRONTMATTER_POLICIES:
        raise ManifestError(
            f"manifest frontmatter.keys must be one of {sorted(FRONTMATTER_POLICIES)}"
        )
    min_length = frontmatter.get("description_min_length", DEFAULT_DESCRIPTION_MIN_LENGTH)
    if not isinstance(min_length, int) or isinstance(min_length, bool) or min_length < 0:
        raise ManifestError("manifest frontmatter.description_min_length must be a non-negative integer")

    tests = data.get("tests", [])
    if not isinstance(tests, list):
        raise ManifestError("manifest tests must be a list")
    for index, entry in enumerate(tests):
        if not isinstance(entry, dict):
            raise ManifestError(f"manifest tests[{index}] must be an object")
        command = entry.get("command")
        if not isinstance(command, list) or not command or not all(
            isinstance(part, str) for part in command
        ):
            raise ManifestError(f"manifest tests[{index}].command must be a non-empty list of strings")
        cwd = entry.get("cwd", ".")
        if not isinstance(cwd, str):
            raise ManifestError(f"manifest tests[{index}].cwd must be a string")
        timeout = entry.get("timeout_seconds", DEFAULT_TEST_TIMEOUT_SECONDS)
        if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
            raise ManifestError(f"manifest tests[{index}].timeout_seconds must be a positive integer")

    # Every manifest-declared path must stay inside the skill directory. This
    # blocks a manifest from satisfying a required file with, say, ../README.md
    # or running a declared test from outside the skill.
    for rel in required:
        if not _within_skill(root, rel):
            raise ManifestError(f"required_files entry escapes the skill directory: {rel}")
    for rel in forbidden:
        if not _within_skill(root, rel):
            raise ManifestError(f"forbidden_files entry escapes the skill directory: {rel}")
    for index, entry in enumerate(tests):
        cwd = entry.get("cwd", ".")
        if not _within_skill(root, cwd):
            raise ManifestError(f"tests[{index}].cwd escapes the skill directory: {cwd}")

    return data


def check_required_files(root: Path, manifest: dict[str, Any], errors: list[str]) -> None:
    for rel in manifest["required_files"]:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    for rel in manifest.get("forbidden_files", []):
        if (root / rel).exists():
            errors.append(f"forbidden file present: {rel}")


def check_directory_name(root: Path, manifest: dict[str, Any], errors: list[str]) -> None:
    if root.name != manifest["name"]:
        errors.append(
            f"skill directory name {root.name!r} does not match manifest name {manifest['name']!r}"
        )


def check_frontmatter(root: Path, manifest: dict[str, Any], errors: list[str]) -> None:
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        errors.append("missing SKILL.md")
        return
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("SKILL.md must start with YAML frontmatter")
        return
    block_match = FRONTMATTER_BLOCK.match(text)
    if not block_match:
        errors.append("SKILL.md frontmatter is malformed (missing closing --- fence)")
        return
    block = block_match.group(1)

    top_level_keys: list[str] = []
    for line in block.splitlines():
        if not line or line[0] in " \t#":
            continue
        key_match = TOP_LEVEL_KEY.match(line)
        if key_match:
            top_level_keys.append(key_match.group(1))

    policy = manifest.get("frontmatter", {}).get("keys", "claude-standard")
    key_set = set(top_level_keys)
    if len(top_level_keys) != len(key_set):
        errors.append("SKILL.md frontmatter contains duplicate top-level keys")
    if policy == "name-description-only":
        if key_set != {"name", "description"}:
            errors.append("SKILL.md frontmatter may contain only name and description")
    else:  # claude-standard
        unexpected = sorted(key_set - CLAUDE_ALLOWED_KEYS)
        if unexpected:
            errors.append(
                "SKILL.md frontmatter has unexpected key(s): "
                + ", ".join(unexpected)
                + f" (allowed: {', '.join(sorted(CLAUDE_ALLOWED_KEYS))})"
            )
    for required_key in ("name", "description"):
        if required_key not in key_set:
            errors.append(f"SKILL.md frontmatter is missing {required_key}")

    name_match = re.search(r"^name:\s*(.+?)\s*$", block, re.MULTILINE)
    name = name_match.group(1) if name_match else ""
    if not name:
        errors.append("SKILL.md name is empty")
    else:
        if name != manifest["name"]:
            errors.append(
                f"SKILL.md name {name!r} does not match manifest name {manifest['name']!r}"
            )
        if not KEBAB_CASE.match(name):
            errors.append(f"SKILL.md name {name!r} must be kebab-case (lowercase letters, digits, hyphens)")
        if len(name) > NAME_MAX_LENGTH:
            errors.append(f"SKILL.md name is too long ({len(name)} > {NAME_MAX_LENGTH})")

    description_match = re.search(r"^description:\s*(.+?)\s*$", block, re.MULTILINE)
    description = description_match.group(1) if description_match else ""
    if not description:
        errors.append("SKILL.md description is empty")
    else:
        min_length = manifest.get("frontmatter", {}).get(
            "description_min_length", DEFAULT_DESCRIPTION_MIN_LENGTH
        )
        if len(description) < min_length:
            errors.append(
                f"SKILL.md description is too short ({len(description)} < {min_length}); "
                "make it specific and useful"
            )
        if len(description) > DESCRIPTION_MAX_LENGTH:
            errors.append(
                f"SKILL.md description is too long ({len(description)} > {DESCRIPTION_MAX_LENGTH})"
            )
        if "<" in description or ">" in description:
            errors.append("SKILL.md description cannot contain angle brackets (< or >)")


def check_local_links(root: Path, errors: list[str]) -> None:
    root_resolved = root.resolve()
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for target in MARKDOWN_LINK.findall(text):
            clean = target.split("#", 1)[0]
            if not clean or "://" in clean or clean.startswith("mailto:"):
                continue
            resolved = (path.parent / clean).resolve()
            try:
                resolved.relative_to(root_resolved)
            except ValueError:
                errors.append(f"{path.relative_to(root)} links outside the skill: {target}")
                continue
            if not resolved.exists():
                errors.append(f"broken local link in {path.relative_to(root)}: {target}")


def compile_scripts(root: Path, errors: list[str], compile_root: Path) -> None:
    scripts_dir = root / "scripts"
    if not scripts_dir.is_dir():
        return
    for path in sorted(scripts_dir.glob("*.py")):
        try:
            py_compile.compile(
                str(path),
                cfile=str(compile_root / f"{path.stem}.pyc"),
                doraise=True,
            )
        except py_compile.PyCompileError as exc:
            errors.append(f"Python compile failed for scripts/{path.name}: {exc.msg}")


def run_declared_tests(
    root: Path, manifest: dict[str, Any], errors: list[str], pycache_dir: Path
) -> None:
    import os

    for index, entry in enumerate(manifest.get("tests", [])):
        command = list(entry["command"])
        if command[0] in ("python", "python3"):
            command[0] = sys.executable
        cwd = (root / entry.get("cwd", ".")).resolve()
        if not cwd.is_dir():
            errors.append(f"tests[{index}] cwd does not exist: {entry.get('cwd', '.')}")
            continue
        env = os.environ.copy()
        env["PYTHONPYCACHEPREFIX"] = str(pycache_dir / f"tests-{index}")
        timeout = entry.get("timeout_seconds", DEFAULT_TEST_TIMEOUT_SECONDS)
        try:
            proc = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
            )
        except FileNotFoundError:
            errors.append(f"tests[{index}] command not found: {command[0]}")
            continue
        except subprocess.TimeoutExpired:
            errors.append(f"tests[{index}] timed out after {timeout}s")
            continue
        if proc.returncode != 0:
            errors.append(
                f"tests[{index}] failed ({' '.join(entry['command'])}):\n"
                + proc.stdout
                + proc.stderr
            )


def validate(root: Path, run_tests: bool = True) -> list[str]:
    """Return a list of validation errors for the skill at ``root`` (empty = valid)."""
    root = root.resolve()
    errors: list[str] = []
    try:
        manifest = load_manifest(root)
    except ManifestError as exc:
        return [str(exc)]

    check_directory_name(root, manifest, errors)
    check_required_files(root, manifest, errors)
    check_frontmatter(root, manifest, errors)
    check_local_links(root, errors)

    with tempfile.TemporaryDirectory() as temp:
        compile_root = Path(temp)
        compile_scripts(root, errors, compile_root)
        # Only run the (slower, subprocess-spawning) declared tests once the
        # package is otherwise structurally sound, matching the prior behavior.
        if run_tests and not errors:
            run_declared_tests(root, manifest, errors, compile_root)
    return errors


def _looks_like_skill(path: Path) -> bool:
    # A directory with either file is a skill candidate. Treating a SKILL.md
    # without a manifest as a candidate lets validate() report the missing
    # manifest instead of silently passing a skill that has no package contract.
    return (path / MANIFEST_NAME).is_file() or (path / "SKILL.md").is_file()


def discover_skills(path: Path) -> list[Path]:
    """Expand ``path`` into skill directories (those with a manifest or SKILL.md)."""
    if _looks_like_skill(path):
        return [path]
    if not path.is_dir():
        return []
    return sorted(child for child in path.iterdir() if child.is_dir() and _looks_like_skill(child))


def default_skills_root() -> Path:
    # tools/skill-validator/skill_validator.py -> repo root is two levels up.
    return Path(__file__).resolve().parents[2] / ".claude" / "skills"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="skill directories, or roots containing skills (default: bundled .claude/skills)",
    )
    parser.add_argument("--no-tests", action="store_true", help="skip declared regression tests")
    args = parser.parse_args()

    search_paths = args.paths or [default_skills_root()]
    skills: list[Path] = []
    for path in search_paths:
        resolved = path.resolve()
        if not resolved.exists():
            print(f"path does not exist: {path}", file=sys.stderr)
            return 2
        found = discover_skills(resolved)
        if not found:
            print(f"no skill-manifest.json found at or under: {path}", file=sys.stderr)
            return 2
        skills.extend(found)

    # De-duplicate while preserving order.
    seen: set[Path] = set()
    unique_skills = [s for s in skills if not (s in seen or seen.add(s))]

    failed = 0
    for skill in unique_skills:
        errors = validate(skill, run_tests=not args.no_tests)
        label = skill.name
        if errors:
            failed += 1
            print(f"FAIL {label} ({len(errors)} error(s)):")
            for error in errors:
                lines = error.splitlines() or [""]
                print(f"  - {lines[0]}")
                for line in lines[1:]:
                    print(f"    {line}")
            print()
        else:
            print(f"PASS {label}")

    total = len(unique_skills)
    print(f"\n{total - failed}/{total} skill(s) passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
