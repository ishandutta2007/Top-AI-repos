"""Repo health checks for the curated README table.

This repo is a curated list of AI projects, not a Python package — it has no
runtime tests. These checks verify that the README table stays well-formed
and the helper scripts stay parseable, so contributor PRs that insert or
renumber rows can't silently break the file.

Replaces an earlier `assert True` placeholder that existed only to make
pytest exit 0 instead of 5 ("no tests collected").
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
TABLE_ROW = re.compile(r"^\|\s*(\d+)\s*\|")


def test_readme_has_curated_list_header() -> None:
    """First line of the README must be the project H1 — guards against
    accidental truncation or a stray prepended line."""
    first_line = README.read_text(encoding="utf-8").splitlines()[0]
    assert first_line.startswith("# "), f"README first line is not an H1: {first_line!r}"
    assert "Top-AI" in first_line, f"README H1 lost its project name: {first_line!r}"


def test_table_row_indices_are_unique_and_start_at_one() -> None:
    """Each row in the README table is numbered. Numbers must be unique (no
    accidental duplicates after an insertion) and the first listed row must
    still be #1."""
    text = README.read_text(encoding="utf-8")
    indices = [int(m.group(1)) for line in text.splitlines() if (m := TABLE_ROW.match(line))]
    assert indices, "no numbered table rows found in README"
    assert indices[0] == 1, f"first table row should be #1, got #{indices[0]}"
    duplicates = sorted({i for i in indices if indices.count(i) > 1})
    assert not duplicates, f"duplicate table row indices: {duplicates}"


def test_helper_scripts_parse_as_python() -> None:
    """Helper scripts in the repo root should be syntactically valid Python so
    a typo can't silently land on main."""
    scripts = sorted(REPO_ROOT.glob("*.py"))
    assert scripts, "expected at least one helper script at the repo root"
    for script in scripts:
        ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
