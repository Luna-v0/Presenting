"""SHOTS.md — what the human has to go and find.

Keyed by beat `id`, never by position, so reordering the deck never invalidates
an ask or an asset path.

The shot list is a **function of the target**. A `constructible` visual needs
nothing from the human on manim — the library draws it — but the same visual on
Slides needs a rendered still. Expect a short list for a manim deck and a much
longer one for a Slides deck, from the identical screenplay.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .screenplay import Beat, Deck


@dataclass
class Shot:
    beat_id: str
    kind: str
    sub: str
    needs: str
    why: str
    search: str = ""
    wrong_if: str = ""
    save_to: str = ""
    attribution: str = ""
    built_by_us: bool = False        # we can produce it; no ask for the human

    def render(self) -> str:
        lines = [f"### {self.beat_id} — {self.kind} / {self.sub or 'figure'}", ""]
        lines.append(f"**Needs:** {self.needs}")
        lines.append(f"**Why:** {self.why}")
        if self.search:
            lines.append(f"**Search:** {self.search}")
        if self.wrong_if:
            lines.append(f"**Wrong if:** {self.wrong_if}")
        lines.append(f"**Save to:** {self.save_to}")
        if self.attribution:
            lines.append(f"**Attribution:** {self.attribution}")
        lines.append("")
        return "\n".join(lines)


def asset_path(beat: Beat, *, built: bool = False) -> str:
    folder = "assets/built" if built else "assets/raw"
    return f"{folder}/{beat.id}.png"


def shots_for(deck: Deck) -> list[Shot]:
    """Every visual the deck cannot produce for itself, for this target."""
    target = deck.target
    out: list[Shot] = []

    for beat in deck.beats():
        spec = beat.visual or {}
        kind = spec.get("kind", "none")
        if kind in ("none", ""):
            continue
        intent = spec.get("intent", "")
        sub = spec.get("sub", "")

        if kind == "constructible":
            if target == "manim":
                continue                      # the library draws it; nothing to ask
            out.append(Shot(
                beat.id, kind, sub or "diagram",
                needs="a manim still of this diagram",
                why=("Slides cannot construct it, and a clip-art substitute is what "
                     "makes a deck stop looking like the rest of them"),
                save_to=asset_path(beat, built=True),
                built_by_us=True,
            ))
            continue

        if kind == "chart":
            if spec.get("data"):
                continue                      # we have the numbers; we can plot it
            out.append(Shot(
                beat.id, kind, sub or "chart",
                needs=f"the numbers behind: {intent}",
                why="a chart earns its place only if the beat walks through it",
                search=spec.get("source", ""),
                save_to=asset_path(beat),
            ))
            continue

        # referential: a real thing that has to be found or photographed
        if spec.get("asset"):
            continue
        out.append(Shot(
            beat.id, kind, sub or "photo",
            needs=intent or "an image for this beat",
            why=spec.get("why", "") or "the claim rests on a real thing being shown",
            search=spec.get("search", ""),
            wrong_if=spec.get("wrong_if", ""),
            save_to=asset_path(beat),
            attribution=spec.get("attribution", ""),
        ))
    return out


def render(deck: Deck, shots: list[Shot]) -> str:
    asks = [s for s in shots if not s.built_by_us]
    ours = [s for s in shots if s.built_by_us]

    lines = [f"# Shots — {deck.meta.get('title', deck.slug)}", ""]
    lines.append(f"Target: **{deck.target}**. {len(asks)} to find, {len(ours)} for us "
                 "to build.")
    lines.append("")
    lines.append("Keyed by beat id, never by position: moving a beat changes nothing "
                 "here and breaks no path.")
    lines.append("")
    if asks:
        lines.append("## To find")
        lines.append("")
        lines += [s.render() for s in asks]
    if ours:
        lines.append("## For us to build")
        lines.append("")
        lines += [s.render() for s in ours]
    if not shots:
        lines.append("Nothing to source. Every visual in this deck is constructible "
                     "on this target.")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def write(deck: Deck, path: Path | str | None = None) -> Path:
    path = Path(path or (deck.path.parent / "SHOTS.md"))
    path.write_text(render(deck, shots_for(deck)))
    return path
