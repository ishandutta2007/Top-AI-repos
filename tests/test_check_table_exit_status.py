"""CLI exit-code regression checks for detected README badge mismatches."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALID_REPO_STARS = '<a href="https://github.com/acme/demo"></a>'
MISMATCHED_REPO_LINK = '<a href="https://github.com/acme/other"></a>'
MISMATCHED_BADGE_URL = (
    '<a href="https://github.com/acme/demo">'
    '<img src="https://example.org/stars?url=https://api.github.com/repos/acme/other"/>'
    "</a>"
)


def run_checker(tmp_path: Path, entrypoint: str, repo_stars: str):
    readme = tmp_path / "README.md"
    readme.write_text(
        "|1| [demo](https://github.com/acme/demo) | "
        f"{repo_stars} | "
        '<a href="https://github.com/acme">'
        '<img src="https://example.org/stars?url='
        'https://api.github-star-counter.workers.dev/user/acme"/>'
        "</a> | Python |\n",
        encoding="utf-8",
    )

    if entrypoint == "direct":
        command = [sys.executable, str(REPO_ROOT / "check_table.py")]
    else:
        command = [
            sys.executable,
            str(REPO_ROOT / "main.py"),
            "--file",
            str(readme),
            "check",
        ]
    return subprocess.run(command, cwd=tmp_path, text=True, capture_output=True)


@pytest.mark.parametrize("entrypoint", ["direct", "main"])
def test_valid_table_exits_successfully(tmp_path: Path, entrypoint: str) -> None:
    result = run_checker(tmp_path, entrypoint, VALID_REPO_STARS)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Success: No inconsistencies found!" in result.stdout


@pytest.mark.parametrize("entrypoint", ["direct", "main"])
@pytest.mark.parametrize(
    "repo_stars",
    [MISMATCHED_REPO_LINK, MISMATCHED_BADGE_URL],
    ids=["repository-href", "badge-api-url"],
)
def test_detected_mismatch_exits_nonzero(
    tmp_path: Path, entrypoint: str, repo_stars: str
) -> None:
    result = run_checker(tmp_path, entrypoint, repo_stars)

    assert "Found 1 inconsistencies." in result.stdout
    assert result.returncode == 1, result.stdout + result.stderr
