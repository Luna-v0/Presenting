"""Shared fixtures. Building a beat renders real manim text, so the heavier
fixtures are session-scoped."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

FT_V2 = REPO / "decks" / "ft-v2"


@pytest.fixture(scope="session")
def repo() -> Path:
    return REPO


@pytest.fixture(scope="session")
def ft_v2_deck():
    from presenting_lib.screenplay import load

    return load(FT_V2 / "screenplay.md")


@pytest.fixture(scope="session")
def ft_v2_brief():
    from presenting_lib.brief import load

    return load(FT_V2 / "brief.md")


@pytest.fixture
def tmp_deck(tmp_path):
    """A deck directory with a screenplay written from `text`."""

    def make(text: str, *, brief: str | None = None):
        from presenting_lib.screenplay import load

        (tmp_path / "assets" / "raw").mkdir(parents=True, exist_ok=True)
        path = tmp_path / "screenplay.md"
        path.write_text(text)
        if brief is not None:
            (tmp_path / "brief.md").write_text(brief)
        return load(path)

    return make
