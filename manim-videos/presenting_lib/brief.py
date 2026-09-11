"""`brief.md` — the deck's intent, and the gates that follow from it.

The primary field is `Narrative`. It is the reason the brief exists: setup,
turn, landing, in broad steps. A narrative is checkable against beats in a way
that "a talk about NLHF" is not, and it is what makes an interview worth
running even when the human already has a draft — with a whiteboard photo in
hand the useful question stops being "what is on the board" and becomes "what
story do these six boxes tell, and where does it break?"

Sections fall out of the narrative rather than being negotiated separately.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .errors import PresentingError

GENRES = ("research-talk", "showcase", "tutorial", "defense", "lecture")
INTERACTIONS = ("none", "organic", "structured")
TARGETS = ("manim", "slides")


class BriefError(PresentingError):
    """The brief is missing something the rest of the pipeline depends on."""


@dataclass(frozen=True)
class GenreRules:
    """What a genre allows. The human already thinks this way — the backup slide
    of their May 2026 deck lists lab meeting, 1:1, defense and external talk
    with different emphases."""

    discussion: bool
    activities: bool
    emphasis: str


RULES = {
    "research-talk": GenreRules(True, False, "open questions, doubts"),
    "showcase": GenreRules(False, False, "intuitive ideas, the pitch"),
    "tutorial": GenreRules(False, True, "sequence, mechanics, demos"),
    "defense": GenreRules(False, False, "method and results"),
    "lecture": GenreRules(True, True, "conceptual depth"),
}


@dataclass
class Brief:
    meta: dict = field(default_factory=dict)
    narrative: str = ""
    why: str = ""
    audience_should: str = ""
    series: str = ""
    out_of_scope: str = ""
    path: Path | None = None

    @property
    def slug(self) -> str:
        return self.meta.get("slug", "deck")

    @property
    def genre(self) -> str:
        return self.meta.get("genre", "research-talk")

    @property
    def target(self) -> str:
        return self.meta.get("target", "manim")

    @property
    def interaction(self) -> str:
        return self.meta.get("interaction", "none")

    @property
    def technicality(self) -> int:
        return int(self.meta.get("technicality", 3))

    @property
    def duration_min(self) -> int:
        return int(self.meta.get("duration_min", 30))

    @property
    def narrative_frozen(self) -> bool:
        return bool(self.meta.get("narrative_frozen", False))

    @property
    def rules(self) -> GenreRules:
        return RULES[self.genre]

    def allows_discussion(self) -> bool:
        """Discussion beats are gated by genre *and* by interaction.

        Never in a showcase: a showcase with a discussion prompt is a failed
        showcase. And never when the human said the talk has no interaction.
        """
        return self.rules.discussion and self.interaction != "none"

    def allows_activities(self) -> bool:
        return self.rules.activities

    def validate(self) -> list[str]:
        problems = []
        if not self.narrative.strip():
            problems.append(
                "no Narrative. It is the primary field — setup, turn, landing. "
                "Without it there is nothing to check the beats against.")
        if self.genre not in GENRES:
            problems.append(f"genre={self.genre!r} is not one of {GENRES}")
        if self.interaction not in INTERACTIONS:
            problems.append(f"interaction={self.interaction!r} is not one of {INTERACTIONS}")
        if self.target not in TARGETS:
            problems.append(f"target={self.target!r} is not one of {TARGETS}")
        if not 1 <= self.technicality <= 5:
            problems.append(f"technicality={self.technicality} is outside 1..5")
        return problems


_FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_HEADINGS = {
    "narrative": "narrative",
    "why i'm presenting": "why",
    "why im presenting": "why",
    "what the audience should do": "audience_should",
    "series": "series",
    "out of scope": "out_of_scope",
}


def parse(text: str, *, path: Path | None = None) -> Brief:
    brief = Brief(path=path)
    match = _FRONT.match(text)
    body = text
    if match:
        brief.meta = yaml.safe_load(match.group(1)) or {}
        body = text[match.end():]

    current: str | None = None
    collected: dict[str, list[str]] = {}
    for line in body.split("\n"):
        if line.startswith("## "):
            key = _HEADINGS.get(line[3:].strip().lower())
            current = key
            if key:
                collected.setdefault(key, [])
            continue
        if current:
            collected[current].append(line)

    for key, lines in collected.items():
        setattr(brief, key, "\n".join(lines).strip())
    return brief


def load(path: Path | str) -> Brief:
    path = Path(path)
    return parse(path.read_text(), path=path)


def require(path: Path | str) -> Brief:
    brief = load(path)
    problems = brief.validate()
    if problems:
        raise BriefError(f"{path}:\n  " + "\n  ".join(problems))
    return brief
