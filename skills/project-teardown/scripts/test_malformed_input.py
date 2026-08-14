#!/usr/bin/env python3
"""Table-driven wrong-type regression tests for project-teardown.

Canonical JSON is untrusted input. Every field is mutated to each wrong type and
the validator must return a bounded error list rather than raise. This is a
generic property test: it encodes no project-specific expected findings, only
the contract that malformed input is reported, never crashed on.

KNOWN_UNGUARDED records call sites that still raise. It is an upper bound that
must only ever shrink; a new crash site fails the suite.
"""

from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import traceback
import unittest
from pathlib import Path

from validate_teardown import validate

WRONG_TYPES = (
    ("null", None),
    ("empty array", []),
    ("empty object", {}),
    ("string", "unexpected"),
    ("integer", 0),
    ("boolean", True),
    ("array of objects", [{"a": 1}]),
    ("object of arrays", {"k": ["v"]}),
)

# Call sites known to still raise on malformed input, as "file.py:line".
# Shrink this list; never grow it.
KNOWN_UNGUARDED: frozenset[str] = frozenset([
    "validate_teardown.py:351",
    "validate_teardown.py:354",
    "validate_teardown.py:355",
    "validate_teardown.py:357"
])


def json_paths(value, prefix=()):
    yield prefix
    if isinstance(value, dict):
        for key, item in value.items():
            yield from json_paths(item, prefix + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value[:2]):
            yield from json_paths(item, prefix + (index,))


def set_at(payload, path, replacement):
    if not path:
        return replacement
    payload = copy.deepcopy(payload)
    cursor = payload
    for step in path[:-1]:
        try:
            cursor = cursor[step]
        except Exception:
            return None
    try:
        cursor[path[-1]] = replacement
    except Exception:
        return None
    return payload


class MalformedInputTests(unittest.TestCase):
    """Every wrong type in every field must be reported, not raised."""

    CANONICAL = ('findings.json',)

    def _fixture(self) -> Path:
        from test_validate_teardown import TeardownValidatorTests as _T
        case = _T(methodName=next(m for m in dir(_T) if m.startswith("test_")))
        case.setUp(); self.addCleanup(case.tearDown)
        return Path(case.root)

    def _sweep(self) -> dict[str, tuple[str, str]]:
        """Mutate every field to every wrong type; return site -> first trigger."""
        source = self._fixture()
        raised: dict[str, tuple[str, str]] = {}
        checked = 0
        for canonical_name in self.CANONICAL:
            base = json.loads((source / canonical_name).read_text(encoding="utf-8"))
            for path in json_paths(base):
                for type_label, replacement in WRONG_TYPES:
                    mutated = set_at(base, path, replacement)
                    if mutated is None:
                        continue
                    checked += 1
                    workdir = Path(tempfile.mkdtemp())
                    target = workdir / source.name
                    shutil.copytree(source, target)
                    (target / canonical_name).write_text(
                        json.dumps(mutated, indent=2), encoding="utf-8"
                    )
                    try:
                        errors = validate(target)
                        if not isinstance(errors, list):
                            raise AssertionError(f"validate returned {type(errors).__name__}")
                    except Exception:
                        frame = traceback.extract_tb(sys.exc_info()[2])[-1]
                        site = f"{Path(frame.filename).name}:{frame.lineno}"
                        field = ".".join(str(part) for part in path) or "<root>"
                        raised.setdefault(site, (field, type_label))
                    finally:
                        shutil.rmtree(workdir, ignore_errors=True)
        self.assertGreater(checked, 0, "fixture produced no mutations")
        self._checked = checked
        return raised

    def setUp(self) -> None:
        if not hasattr(type(self), "_cached_sweep"):
            type(self)._cached_sweep = self._sweep()
        self.raised = type(self)._cached_sweep

    def test_no_new_unguarded_crash_sites(self) -> None:
        unexpected = {k: v for k, v in self.raised.items() if k not in KNOWN_UNGUARDED}
        self.assertEqual(
            unexpected,
            {},
            "new unguarded crash sites (site -> first field/type that reached it): "
            + json.dumps({k: list(v) for k, v in sorted(unexpected.items())}, indent=2),
        )

    def test_known_unguarded_list_is_not_stale(self) -> None:
        stale = sorted(KNOWN_UNGUARDED - set(self.raised))
        self.assertEqual(
            stale, [], f"KNOWN_UNGUARDED is stale; these no longer raise and must be removed: {stale}"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
