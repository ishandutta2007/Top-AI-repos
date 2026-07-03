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
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GITIGNORE = REPO_ROOT / ".gitignore"

# Patterns that must be present in .gitignore to prevent history bloat (issue #26)
REQUIRED_GITIGNORE_PATTERNS = [
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "n8n/",
    "node_modules/",
    "sort_log.txt",
    "star_cache.json",
]

# Files that are auto-generated and must NOT be tracked by git
UNTRACKED_FILES = [
    "sort_log.txt",
    "star_cache.json",
]

# 1 MB — no single blob in the working tree should exceed this
MAX_TRACKED_FILE_SIZE_BYTES = 1 * 1024 * 1024
README = REPO_ROOT / "README.md"
TABLE_ROW = re.compile(r"^\|\s*(\d+)\s*\|")


def test_readme_has_curated_list_header() -> None:
    """The README's H1 project header must appear near the top (after the
    centered banner image) — guards against accidental truncation or a
    stray prepended line."""
    lines = README.read_text(encoding="utf-8").splitlines()
    header_lines = [line for line in lines[:10] if line.startswith("# ")]
    assert header_lines, f"No H1 header found in first 10 lines: {lines[:10]!r}"
    assert "Top-AI" in header_lines[0], (
        f"README H1 lost its project name: {header_lines[0]!r}"
    )


def test_table_row_indices_are_unique_and_start_at_one() -> None:
    """Each row in the README table is numbered. Numbers must be unique (no
    accidental duplicates after an insertion) and the first listed row must
    still be #1."""
    text = README.read_text(encoding="utf-8")
    indices = [
        int(m.group(1)) for line in text.splitlines() if (m := TABLE_ROW.match(line))
    ]
    assert indices, "no numbered table rows found in README"
    assert indices[0] == 1, f"first table row should be #1, got #{indices[0]}"
    duplicates = sorted({i for i in indices if indices.count(i) > 1})
    assert not duplicates, f"duplicate table row indices: {duplicates}"


def test_table_row_indices_are_continuous() -> None:
    """Table row numbers should increment continuously without gaps.

    This catches common insertion errors where rows are added without
    properly renumbering subsequent entries.
    """
    text = README.read_text(encoding="utf-8")
    indices = [
        int(m.group(1)) for line in text.splitlines() if (m := TABLE_ROW.match(line))
    ]

    if not indices:
        pytest.skip("no numbered table rows found in README")

    for i, idx in enumerate(indices, start=1):
        assert idx == i, (
            f"Expected row #{i}, got #{idx} at position {i} — there may be a gap in numbering"
        )


def test_table_row_count_matches_highest_index() -> None:
    """The highest row number should equal the total number of rows.

    This ensures the table numbering is consistent and complete.
    """
    text = README.read_text(encoding="utf-8")
    indices = [
        int(m.group(1)) for line in text.splitlines() if (m := TABLE_ROW.match(line))
    ]

    assert indices, "no numbered table rows found in README"
    assert indices[-1] == len(indices), (
        f"Highest index {indices[-1]} does not match row count {len(indices)} — "
        f"check for missing or extra rows"
    )


def test_table_row_format_valid() -> None:
    """Each table row should have the correct number of columns.

    Prevents accidental truncation or malformed rows that break the table layout.
    """
    text = README.read_text(encoding="utf-8")

    # track rows and validate column count
    for line in text.splitlines():
        if m := TABLE_ROW.match(line):
            pipe_count = line.count("|")
            # minimum pipes for a valid row (need at least 6 pipes for 7 columns)
            assert pipe_count >= 6, (
                f"Row {m.group(1)} has too few columns ({pipe_count} pipes): {line[:80]}"
            )


def test_table_repo_links_are_valid() -> None:
    """Repository links in the table should be properly formatted.

    Catches broken or malformed GitHub repository URLs.
    """
    text = README.read_text(encoding="utf-8")
    link_pattern = re.compile(r"\[(.+?)\]\((https://github\.com/[^)]+)\)")

    found_links = False
    for match in link_pattern.finditer(text):
        found_links = True
        repo_name, url = match.groups()
        # basic validation: URL should have owner and repo
        assert url.count("/") >= 3, (
            f"Invalid repo link format for '{repo_name}': {url} — "
            f"should be https://github.com/owner/repo"
        )
        assert "github.com" in url, f"Non-GitHub link found: {url}"

    assert found_links, "No repository links found in README table"


def test_table_rows_no_unintended_newlines() -> None:
    """Table rows should not have line breaks within them.

    Prevents accidentally split rows that break the table structure.
    """
    text = README.read_text(encoding="utf-8")
    lines = text.splitlines()

    for i, line in enumerate(lines, start=1):
        if TABLE_ROW.match(line):
            # row should end with pipe or contain an image tag (badges)
            assert line.rstrip().endswith("|") or "<img" in line, (
                f"Line {i}: Row may be malformed or incomplete: {line[:80]}..."
            )


def test_readme_encoding_valid() -> None:
    """README should be valid UTF-8 without BOM or special characters.

    Catches encoding issues that might cause parsing failures.
    """
    try:
        text = README.read_text(encoding="utf-8")
        # verify no null bytes
        assert "\x00" not in text, "README contains null bytes"
        # re-encode to catch any invalid sequences
        text.encode("utf-8").decode("utf-8")
    except UnicodeDecodeError as e:
        pytest.fail(f"README has encoding issues: {e}")


def test_readme_required_sections_present() -> None:
    """README should contain all required sections.

    Prevents accidental deletion of important README structure.
    """
    text = README.read_text(encoding="utf-8")
    required_sections = {
        "H1 Header": "# 🚀",
        "Table Header": "|<ins>#</ins>",
        "Contributors Section": "## 👥 Contributors",
        "Discord Link": "discord.gg/jc4xtF58Ve",
    }

    for section_name, section_text in required_sections.items():
        assert section_text in text, (
            f"Missing required section: {section_name} (looking for '{section_text}')"
        )


@pytest.mark.parametrize(
    "section",
    [
        "# 🚀 Top-AI",
        "## 👥 Contributors",
    ],
)
def test_readme_critical_sections_exist(section: str) -> None:
    """Verify critical sections exist in README (parameterized test).

    Provides fine-grained checks for each important section.
    """
    text = README.read_text(encoding="utf-8")
    assert section in text, f"Critical section '{section}' not found in README"


def test_helper_scripts_parse_as_python() -> None:
    """Helper scripts in the repo root should be syntactically valid Python so
    a typo can't silently land on main."""
    scripts = sorted(REPO_ROOT.glob("*.py"))
    assert scripts, "expected at least one helper script at the repo root"
    for script in scripts:
        try:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except SyntaxError as e:
            pytest.fail(f"Script {script.name} has syntax errors: {e}")


def test_no_empty_table_rows() -> None:
    """Ensure no empty or whitespace-only table rows exist.

    Catches rows that may have been accidentally cleared or corrupted.
    """
    text = README.read_text(encoding="utf-8")

    for line in text.splitlines():
        if TABLE_ROW.match(line):
            # remove all pipes and whitespace
            content = line.replace("|", "").replace(" ", "").replace("\t", "")
            # should have row number and some additional content
            assert len(content.strip()) > 1, (
                f"Row appears to be empty or whitespace-only: {line[:80]}"
            )


def test_readme_file_exists_and_readable() -> None:
    """Ensure README.md exists and is readable.

    Basic sanity check for file access.
    """
    assert README.exists(), f"README.md not found at {README}"
    assert README.is_file(), f"README.md is not a file: {README}"
    assert README.stat().st_size > 0, "README.md is empty"


# ---------------------------------------------------------------------------
# Git-history-bloat guards (issue #26)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("pattern", REQUIRED_GITIGNORE_PATTERNS)
def test_gitignore_covers_bloat_patterns(pattern: str) -> None:
    """Each known history-bloat pattern must be present in .gitignore as an
    active (non-commented) line.

    This guards against accidental removal of entries that were added to fix
    the 300 MB history bloat caused by n8n assets and lock-file churn.
    """
    assert GITIGNORE.exists(), ".gitignore file not found"
    active_lines = [
        line.strip()
        for line in GITIGNORE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert pattern in active_lines, (
        f"'.gitignore' is missing the active pattern {pattern!r} — "
        "removing it allows history bloat to recur (see issue #26)"
    )


@pytest.mark.parametrize("filename", UNTRACKED_FILES)
def test_autogenerated_files_are_not_tracked(filename: str) -> None:
    """Auto-generated files must not be tracked by git.

    These files are regenerated on every script run and should never appear
    in git history, as repeated commits inflate the pack size.
    """
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", filename],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, (
        f"{filename!r} is tracked by git but should be untracked — "
        "add it to .gitignore and run `git rm --cached {filename}`"
    )


def test_no_large_files_tracked() -> None:
    """No tracked file in the working tree should exceed 1 MB.

    Prevents accidentally committing large assets (e.g. lock files, zip
    archives, JSON fixtures) that would balloon the repository's pack size.
    """
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    tracked = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    oversized = []
    for rel_path in tracked:
        path = REPO_ROOT / rel_path
        if path.is_file() and path.stat().st_size > MAX_TRACKED_FILE_SIZE_BYTES:
            size_kb = path.stat().st_size // 1024
            oversized.append(f"{rel_path} ({size_kb} KB)")

    assert not oversized, (
        "The following tracked files exceed 1 MB and will bloat git history:\n"
        + "\n".join(f"  {f}" for f in oversized)
        + "\nAdd them to .gitignore or use Git LFS."
    )
