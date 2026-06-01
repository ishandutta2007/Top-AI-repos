"""Smoke test so pytest collects at least one item in CI.

This repo is a curated list of AI projects, not a Python package — it has no
runtime tests today. Without this file pytest exits with code 5 ("no tests
collected"), which the `Python package` workflow treats as a build failure
on every push to main and every PR.

Replace with real tests if/when the helper scripts grow real surface area.
"""


def test_smoke() -> None:
    assert True
