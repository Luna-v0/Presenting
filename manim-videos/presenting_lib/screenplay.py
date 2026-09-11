"""The screenplay format: parse, hold, write back.

`screenplay.md` is the artifact the human keeps. It has to read as a document
in six months *and* parse into something the compiler can render, so it is
markdown with a small amount of structure rather than a data file with prose
smuggled into it.

Two rules this module enforces mechanically:

* **`Note` and `Cue` are copied byte for byte.** They are the human's own
  words. Nothing here tidies, merges, re-wraps or translates them — a round
  trip through parse/dump leaves them identical, and there is a test for it.
* **Beats are identified by slug, not position.** `2.1` is display, derived
  from position at render time. `preference-cycle` is identity. Without that,
  inserting a beat renumbers everything after it, every asset path drifts, and
  every verdict from the last review points at the wrong beat.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .errors import PresentingError

PROSE_FIELDS = ("Note", "Claim", "On slide", "Cue", "Skip")

#: Fields that make up a beat's content for the purpose of "has a human touched
#: this?". Position, verdicts and demotion notes are excluded — moving a beat or
#: reviewing it is not editing it.
FINGERPRINTED = ("layout", "claim", "on_slide", "note", "cue", "skip",
                 "visual", "content", "raw", "time_s", "transition")
VERDICTS = ("keep", "demote", "narrative-wrong")
ORIGINS = ("generated", "human")
TRANSITIONS = ("cut", "build")
SCENE_TYPES = ("2d", "3d")


class ScreenplayError(PresentingError):
    """The screenplay could not be parsed, or breaks a rule the format guarantees."""


@dataclass
class Beat:
    id: str
    layout: str = "claim-above-figure"
    heading: str = ""
    origin: str = "generated"
    time_s: int = 60
    transition: str = "cut"
    scene_type: str = "2d"
    backup: bool = False
    demoted_because: str = ""
    verdict: str = ""
    visual: dict = field(default_factory=dict)
    content: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)      # layout: raw -> {code | scene}

    # Prose. `note` and `cue` are verbatim, always.
    note: str = ""
    claim: str = ""
    on_slide: list[str] = field(default_factory=list)
    cue: str = ""
    skip: str = ""

    generated_hash: str = ""  # fingerprint of the content as generated

    section: str = ""        # filled in by the parser
    number: int = 0          # display position, derived at render time

    def fingerprint(self) -> str:
        """A hash of the beat's content, used to notice hand edits.

        `origin: human` is what stops a revision pass overwriting the user's
        own work, and asking them to set it by hand is asking them to remember
        something at exactly the moment they are thinking about the talk. So
        the skill stamps this when it generates a beat, and anything that no
        longer matches its stamp was edited by a person — no flag to remember,
        and no way to forget it.
        """
        import hashlib
        import json

        payload = json.dumps(
            {name: getattr(self, name) for name in FINGERPRINTED},
            sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def stamp(self) -> "Beat":
        """Record the current content as generated. Called after generating."""
        self.origin = "generated"
        self.generated_hash = self.fingerprint()
        return self

    def edited_by_hand(self) -> bool:
        """True when the content has drifted from what was generated."""
        if self.origin == "human":
            return True
        if not self.generated_hash:
            return False          # never stamped: nothing to compare against
        return self.fingerprint() != self.generated_hash

    def is_raw(self) -> bool:
        return self.layout == "raw"

    def spec_fields(self) -> dict:
        out = {
            "id": self.id,
            "origin": self.origin,
            "layout": self.layout,
            "time_s": self.time_s,
            "transition": self.transition,
        }
        if self.scene_type != "2d":
            out["scene_type"] = self.scene_type
        if self.visual:
            out["visual"] = self.visual
        if self.content:
            out["content"] = self.content
        if self.raw:
            out["raw"] = self.raw
        if self.backup:
            out["backup"] = True
        if self.demoted_because:
            out["demoted_because"] = self.demoted_because
        if self.verdict:
            out["verdict"] = self.verdict
        if self.generated_hash:
            out["generated_hash"] = self.generated_hash
        return out


@dataclass
class Section:
    name: str
    bridge: str = ""
    beats: list[Beat] = field(default_factory=list)


@dataclass
class Deck:
    meta: dict = field(default_factory=dict)
    sections: list[Section] = field(default_factory=list)
    path: Path | None = None

    @property
    def slug(self) -> str:
        return self.meta.get("slug", "deck")

    @property
    def target(self) -> str:
        return self.meta.get("target", "manim")

    def beats(self) -> list[Beat]:
        return [b for s in self.sections for b in s.beats]

    def main_beats(self) -> list[Beat]:
        return [b for b in self.beats() if not b.backup]

    def backup_beats(self) -> list[Beat]:
        return [b for b in self.beats() if b.backup]

    def beat(self, beat_id: str) -> Beat:
        for b in self.beats():
            if b.id == beat_id:
                return b
        raise ScreenplayError(f"no beat with id {beat_id!r} in {self.slug}")

    def section_names(self) -> list[str]:
        return [s.name for s in self.sections]

    def total_time_s(self) -> int:
        return sum(b.time_s for b in self.main_beats())


# ── parsing ──────────────────────────────────────────────────────────────────

_FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_SECTION_PREFIX = re.compile(r"^Section\s+\d+\s*[—–-]\s*", re.IGNORECASE)
_BEAT_PREFIX = re.compile(r"^[\d.]+\s*[—–-]\s*")
_PROSE = re.compile(r"^\*\*(" + "|".join(PROSE_FIELDS) + r")\.?\*\*\s*", re.IGNORECASE)
_BRIDGE = re.compile(r"^>\s*\*\*Bridge\.?\*\*\s*", re.IGNORECASE)
_BRIDGE_LABEL = re.compile(r"^\*\*Bridge\.?\*\*\s*", re.IGNORECASE)


def parse(text: str, *, path: Path | None = None) -> Deck:
    deck = Deck(path=path)

    match = _FRONT.match(text)
    if match:
        deck.meta = yaml.safe_load(match.group(1)) or {}
        body = text[match.end():]
    else:
        body = text

    section: Section | None = None
    beat: Beat | None = None
    lines = body.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith("# "):
            section = Section(name=_SECTION_PREFIX.sub("", line[2:].strip()))
            deck.sections.append(section)
            beat = None
            i += 1
            continue

        if line.startswith("## "):
            if section is None:
                raise ScreenplayError(
                    f"beat {line[3:].strip()!r} appears before any section. "
                    "Every beat belongs to a section — sections are the narrative's joints."
                )
            heading = line[3:].strip()
            block, i = _read_fenced_yaml(lines, i + 1)
            beat = _beat_from(block, heading=heading, section=section.name)
            section.beats.append(beat)
            continue

        if _BRIDGE.match(line):
            if section is None:
                raise ScreenplayError("a Bridge appears before any section heading")
            chunk, i = _read_quote(lines, i)
            section.bridge = _BRIDGE_LABEL.sub("", chunk).strip()
            continue

        prose = _PROSE.match(line)
        if prose and beat is not None:
            name = prose.group(1).lower()
            value, i = _read_prose(lines, i, prose.end())
            _assign_prose(beat, name, value)
            continue

        i += 1

    _check_unique_ids(deck)
    return deck


def _read_fenced_yaml(lines: list[str], i: int) -> tuple[dict, int]:
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or not lines[i].startswith("```"):
        return {}, i
    fence = lines[i].strip()
    lang = fence.strip("`").strip()
    i += 1
    body: list[str] = []
    while i < len(lines) and not lines[i].startswith("```"):
        body.append(lines[i])
        i += 1
    i += 1  # closing fence
    if lang not in ("yaml", "yml", ""):
        return {}, i
    return yaml.safe_load("\n".join(body)) or {}, i


def _read_quote(lines: list[str], i: int) -> tuple[str, int]:
    chunk = []
    while i < len(lines) and lines[i].startswith(">"):
        chunk.append(lines[i].lstrip(">").strip())
        i += 1
    return " ".join(chunk).strip(), i


def _read_prose(lines: list[str], i: int, offset: int) -> tuple[str, int]:
    """Everything from the label to the next blank line followed by a new block.

    Captured exactly as written: no re-wrapping, no whitespace normalisation
    beyond stripping the trailing newline.
    """
    collected = [lines[i][offset:]]
    i += 1
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if (not nxt.strip() or nxt.startswith("#") or nxt.startswith("```")
                    or _PROSE.match(nxt) or _BRIDGE.match(nxt)):
                break
            collected.append(line)
            i += 1
            continue
        if line.startswith("#") or line.startswith("```") or _PROSE.match(line) \
                or _BRIDGE.match(line):
            break
        collected.append(line)
        i += 1
    return "\n".join(collected).strip("\n"), i


def _assign_prose(beat: Beat, name: str, value: str) -> None:
    if name == "note":
        beat.note = value          # verbatim
    elif name == "cue":
        beat.cue = value           # verbatim, any language
    elif name == "claim":
        beat.claim = value.strip()
    elif name == "skip":
        beat.skip = value.strip()
    elif name == "on slide":
        beat.on_slide = [
            re.sub(r"^[-*]\s+", "", ln).strip()
            for ln in value.split("\n")
            if ln.strip()
        ]


def _beat_from(spec: dict, *, heading: str, section: str) -> Beat:
    if "id" not in spec:
        raise ScreenplayError(
            f"beat {heading!r} has no id. Beats are identified by a slug that "
            "survives reordering — without one, moving a beat breaks every asset "
            "path and every review verdict pointing at it."
        )
    beat = Beat(
        id=str(spec["id"]),
        layout=str(spec.get("layout", "claim-above-figure")),
        heading=_BEAT_PREFIX.sub("", heading),
        origin=str(spec.get("origin", "generated")),
        time_s=int(spec.get("time_s", 60)),
        transition=str(spec.get("transition", "cut")),
        scene_type=str(spec.get("scene_type", "2d")),
        backup=bool(spec.get("backup", False)),
        demoted_because=str(spec.get("demoted_because", "")),
        verdict=str(spec.get("verdict", "")),
        generated_hash=str(spec.get("generated_hash", "")),
        visual=dict(spec.get("visual") or {}),
        content=dict(spec.get("content") or {}),
        raw=dict(spec.get("raw") or {}),
        section=section,
    )
    for field_name, allowed in (("origin", ORIGINS), ("transition", TRANSITIONS),
                                ("scene_type", SCENE_TYPES)):
        value = getattr(beat, field_name)
        if value not in allowed:
            raise ScreenplayError(
                f"beat {beat.id!r}: {field_name}={value!r} is not one of {allowed}")
    if beat.verdict and beat.verdict not in VERDICTS:
        raise ScreenplayError(
            f"beat {beat.id!r}: verdict={beat.verdict!r} is not one of {VERDICTS}")
    return beat


def _check_unique_ids(deck: Deck) -> None:
    seen: dict[str, str] = {}
    for section in deck.sections:
        for beat in section.beats:
            if beat.id in seen:
                raise ScreenplayError(
                    f"duplicate beat id {beat.id!r} (in {seen[beat.id]!r} and "
                    f"{section.name!r}). Ids are identity: assets and review "
                    "verdicts key off them, so two beats cannot share one."
                )
            seen[beat.id] = section.name


def load(path: Path | str) -> Deck:
    path = Path(path)
    return parse(path.read_text(), path=path)


# ── writing ──────────────────────────────────────────────────────────────────

def dump(deck: Deck) -> str:
    out: list[str] = []
    if deck.meta:
        out.append("---")
        out.append(yaml.safe_dump(deck.meta, sort_keys=False,
                                  allow_unicode=True).rstrip("\n"))
        out.append("---")
        out.append("")

    for s_index, section in enumerate(deck.sections, start=1):
        out.append(f"# Section {s_index} — {section.name}")
        out.append("")
        if section.bridge:
            out.append(f"> **Bridge.** {section.bridge}")
            out.append("")
        for b_index, beat in enumerate(section.beats, start=1):
            out.append(f"## {s_index}.{b_index} — {beat.heading or beat.id}")
            out.append("")
            out.append("```yaml")
            out.append(yaml.safe_dump(beat.spec_fields(), sort_keys=False,
                                      allow_unicode=True).rstrip("\n"))
            out.append("```")
            out.append("")
            for label, value in (("Note", beat.note), ("Claim", beat.claim)):
                if value:
                    out.append(f"**{label}.** {value}")
                    out.append("")
            if beat.on_slide:
                out.append("**On slide.**")
                out.extend(f"- {item}" for item in beat.on_slide)
                out.append("")
            for label, value in (("Cue", beat.cue), ("Skip", beat.skip)):
                if value:
                    out.append(f"**{label}.** {value}")
                    out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def save(deck: Deck, path: Path | str | None = None) -> Path:
    path = Path(path or deck.path)
    path.write_text(dump(deck))
    return path
