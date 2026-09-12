"""Screenplay -> manim-slides scenes.

The compiler decides *how*; the layouts decided *where*. It owns four things
the layouts cannot see:

* **Scene grouping.** One `Slide` per section, split further at raw beats and
  at a `scene_type: 3d` boundary — manim-beamer's `MovingCameraScene` runner
  cannot host a `ThreeDScene`, which `ft_v2` already worked around by hand.
* **Transitions.** `build` keeps the previous beat's mobjects on screen; `cut`
  clears them.
* **Chrome.** Footer persistence and, on a `none`-tier beat, animating the
  chrome out and back.
* **Static beats.** `activity-parking` holds still by construction: it is the
  one slide that has to stay legible for ten minutes rather than animate.

It also refuses to compile a generated deck that encodes anything with an
accent whose meaning has not been decided. See `validate` and plan §11.1.
"""

from __future__ import annotations

import os

import re
from dataclasses import dataclass, field, replace
from pathlib import Path

from . import assets
from .chrome import BARE, Chrome, DeckMeta, FULL, NONE
from .errors import PresentingError
from .layouts import Content, get_layout
from .placeholders import VisualSpec
from .screenplay import Beat, Deck, load
from .slots import budget_for
from .tokens import T

#: Held after each step's animation, before the slide break. Manim renders an
#: animation's frames over [0, run_time), so without this the settled state
#: falls into the *next* slide's video and every slide ends mid-draw — both on
#: screen when presenting and in the frames deck-review looks at. Long enough
#: that a slide visibly lands and holds before the presenter can advance off it.
SETTLE_S = 0.5


# ── beat -> Content ──────────────────────────────────────────────────────────

def visual_for(beat: Beat, *, deck_dir: Path | None = None):
    """Build the beat's visual: a spec, a diagram builder, or a chart."""
    spec = beat.visual or {}
    kind = spec.get("kind", "none")
    if kind == "none" and not spec:
        return None

    if kind == "constructible" and spec.get("graph"):
        from . import diagrams

        graph = spec["graph"]
        parsed = diagrams.DiagramSpec(
            nodes=[diagrams.Node(n["id"], n.get("label", n["id"]), n.get("accent"))
                   for n in graph.get("nodes", [])],
            edges=[diagrams.Edge(e["from"], e["to"], e.get("label", ""),
                                 e.get("accent"), bool(e.get("dashed")),
                                 e.get("tailport", ""), e.get("headport", ""))
                   for e in graph.get("edges", [])],
            rankdir=graph.get("rankdir", "TB"),
        )
        return diagrams.builder(parsed)

    if spec.get("builder"):
        # A figure the catalog cannot draw, built by a named function. The
        # library stays out of it: it imports `module:function`, calls it with
        # `args`, and expects back the `builder(slot)` the layouts already take.
        import importlib

        module_name, _, function_name = spec["builder"].partition(":")
        factory = getattr(importlib.import_module(module_name), function_name)
        return factory(**(spec.get("args") or {}))

    if kind == "chart" and spec.get("data"):
        from . import charts

        data = spec["data"]
        return charts.visual(charts.ChartSpec(
            kind=data.get("kind", "line"),
            x=data.get("x", []),
            series=data.get("series", {}),
            accent=data.get("accent"),
            accent_b=data.get("accent_b"),
            xlabel=data.get("xlabel", ""),
            ylabel=data.get("ylabel", ""),
            source=spec.get("source", ""),
        ))

    built = VisualSpec(
        kind=kind,
        sub=spec.get("sub", ""),
        intent=spec.get("intent", ""),
        asset=spec.get("asset"),
        source=spec.get("source", ""),
    )
    # Resolve the asset here, while the deck directory is still known. The
    # layout resolves it again at draw time but has no `deck_dir` to resolve
    # against, so a deck's own assets/raw was never searched and every
    # referential visual fell through to a placeholder.
    if built.asset and deck_dir is not None:
        found = built.resolved_asset(deck_dir)
        if found is not None:
            built = replace(built, asset=str(found.resolve()))
    return built


def content_for(beat: Beat, deck: Deck, *, number: int,
                deck_dir: Path | None = None) -> Content:
    """Map a beat onto the layout's slots.

    The rule that matters: **what renders is `On slide`**, not `Claim`. `Claim`
    is one sentence stating what the beat asserts and is never spoken or shown
    — it exists so the arc can be checked and so the slide text can be derived
    from it. The two exceptions are `claim-only` and `callout`, which are the
    layouts whose whole job is to hold one sentence.

    Anything under the beat's `content:` key wins over all of this. The mapping
    is a default, not a cage.
    """
    on_slide = "\n".join(beat.on_slide) if beat.on_slide else ""
    visual = visual_for(beat, deck_dir=deck_dir)

    fields: dict = {
        "section": beat.section,
        "number": number,
        "beat_id": beat.id,
        "notes": beat.note,
        "title": beat.heading or None,
    }
    layout_name = beat.content.get("backup_of") or beat.layout
    if beat.backup:
        fields["backup_of"] = beat.content.get("backup_of") or "claim-above-figure"
        layout_name = fields["backup_of"]

    if layout_name == "title-card":
        fields.update(
            title=deck.meta.get("title") or beat.heading,
            subtitle=deck.meta.get("subtitle"),
            author=deck.meta.get("author"),
            affiliation=deck.meta.get("affiliation"),
            date=deck.meta.get("date"),
        )
    elif layout_name == "section-break":
        fields.update(section=beat.section, title=None)
    elif layout_name == "claim-only":
        fields.update(claim=beat.claim or on_slide, title=None)
    elif layout_name == "callout":
        fields.update(statement=beat.claim or on_slide, title=None)
    elif layout_name == "discussion":
        fields.update(prompt=beat.claim or on_slide, title=None)
    elif layout_name == "build-list":
        fields.update(items=beat.on_slide or [beat.claim], claim=None)
    elif layout_name == "full-bleed-figure":
        fields.update(visual=visual, title=None)
    elif layout_name == "term-reveal":
        fields.update(term=beat.on_slide[0] if beat.on_slide else beat.heading,
                      definition=beat.claim, visual=visual)
    elif layout_name == "activity-parking":
        fields.update(instructions=on_slide or beat.claim)
    elif layout_name == "activity-setup":
        fields.update(task=on_slide or beat.claim)
    elif layout_name == "two-up-compare":
        pass                                  # panels and labels come from content:
    elif layout_name == "equation-annotated":
        pass                                  # equation and annotations come from content:
    elif layout_name == "table-accented":
        fields.update(claim=on_slide or beat.claim)
    elif layout_name == "figure-with-callouts":
        fields.update(visual=visual)
    else:                                     # claim-above-figure and friends
        fields.update(claim=on_slide or beat.claim, visual=visual)
        if beat.visual.get("attribution"):
            fields["caption"] = beat.visual["attribution"]

    for key, value in beat.content.items():
        if key == "backup_of":
            continue
        if key == "visual" and value is True:
            fields["visual"] = visual
        elif isinstance(value, dict) and "kind" in value:
            # A panel or a second figure declared inline. Without this it
            # reaches the layout as a plain dict and the placer chokes on it.
            fields[key] = visual_for(Beat(id=beat.id, visual=value),
                                     deck_dir=deck_dir)
        else:
            fields[key] = value

    fields = {k: v for k, v in fields.items() if k in Content.__dataclass_fields__}
    return Content(**fields)


def layout_for(beat: Beat):
    return get_layout("backup" if beat.backup else beat.layout)


# ── validation ───────────────────────────────────────────────────────────────

@dataclass
class Finding:
    level: str          # error | warn | note
    beat_id: str
    message: str

    def __str__(self) -> str:
        where = f" [{self.beat_id}]" if self.beat_id else ""
        return f"{self.level.upper():5}{where} {self.message}"


def accent_uses(beat: Beat) -> list[str]:
    """Every place this beat encodes something with an accent."""
    uses: list[str] = []
    for entry in beat.content.get("annotations", []) or []:
        if isinstance(entry, (list, tuple)) and len(entry) > 1 and entry[1]:
            uses.append(f"annotation {entry[1]}")
    if beat.content.get("accent_rows") or beat.content.get("accent_cols"):
        uses.append("accented table row/column")
    graph = (beat.visual or {}).get("graph") or {}
    for node in graph.get("nodes", []):
        if node.get("accent"):
            uses.append(f"diagram node {node['id']} ({node['accent']})")
    for edge in graph.get("edges", []):
        if edge.get("accent"):
            uses.append(f"diagram edge {edge['from']}->{edge['to']} ({edge['accent']})")
    data = (beat.visual or {}).get("data") or {}
    if data.get("accent") or data.get("accent_b"):
        uses.append("accented chart series")
    return uses


def load_brief(deck: Deck):
    """The deck's brief, if it names one and the file is there."""
    from . import brief as brief_mod

    ref = deck.meta.get("brief")
    if not ref or deck.path is None:
        return None
    path = (deck.path.parent / ref).resolve()
    return brief_mod.load(path) if path.exists() else None


def validate(deck: Deck, brief=None) -> list[Finding]:
    """Everything checkable without rendering a pixel."""
    findings: list[Finding] = []
    target = deck.target
    meanings_set = T.accent_meanings_assigned()
    brief = brief if brief is not None else load_brief(deck)

    if brief is not None:
        for problem in brief.validate():
            findings.append(Finding("error", "", f"brief: {problem}"))
        for beat in deck.beats():
            if beat.layout == "discussion" and not brief.allows_discussion():
                reason = ("a showcase with a discussion prompt is a failed showcase"
                          if brief.genre == "showcase"
                          else f"genre {brief.genre!r} does not run discussions"
                          if not brief.rules.discussion
                          else "the brief says interaction: none")
                findings.append(Finding(
                    "error", beat.id,
                    f"discussion beat in a {brief.genre!r} deck — {reason}."))
            if beat.layout.startswith("activity-") and not brief.allows_activities():
                findings.append(Finding(
                    "error", beat.id,
                    f"activity beat in a {brief.genre!r} deck — activity blocks are "
                    "for tutorials (and sometimes lectures)."))

    for section in deck.sections:
        if not section.bridge:
            findings.append(Finding(
                "warn", "",
                f"section {section.name!r} has no Bridge. If the connection from the "
                "previous section cannot be written in one sentence, the order is "
                "wrong — reorder rather than inventing a connective."))

    for beat in deck.beats():
        uses = accent_uses(beat)
        if uses and not meanings_set:
            level = "error" if beat.origin == "generated" else "warn"
            findings.append(Finding(
                level, beat.id,
                f"uses an accent ({'; '.join(uses)}) while accents.green.meaning and "
                "accents.yellow.meaning are unassigned in identity/tokens.yaml. An "
                "accent that means something different in every deck is worse than "
                "no accent — decide the meanings first (plan §11.1)."))

        if beat.is_raw():
            if not (beat.raw.get("scene") or beat.raw.get("code")):
                findings.append(Finding("error", beat.id,
                                        "layout: raw needs raw.scene or raw.code"))
            continue

        layout = layout_for(beat)
        # Measure what the compiler will actually put in the slot, not a second
        # guess at the mapping — a validator that models the mapping separately
        # drifts from it and starts reporting slots the layout never fills.
        try:
            content = content_for(beat, deck, number=beat.number or 1)
        except Exception as exc:                      # pragma: no cover
            findings.append(Finding("error", beat.id, f"cannot build content: {exc}"))
            continue
        for slot_name in layout.measured_text_slots():
            cap = budget_for(target, layout.name, slot_name)
            value = slot_text(content, slot_name)
            if cap and value and len(value) > cap:
                findings.append(Finding(
                    "error", beat.id,
                    f"{layout.name}.{slot_name} is {len(value)} chars, budget {cap} "
                    f"for target {target}. Cut {len(value) - cap}."))

        has_text = bool(beat.on_slide or beat.claim)
        wants_visual = "visual" in layout.accepts
        if has_text and wants_visual and (beat.visual or {}).get("kind", "none") == "none":
            findings.append(Finding(
                "warn", beat.id,
                "full text slot and an empty visual slot. Figures over text, always."))

        if beat.backup and not beat.demoted_because:
            findings.append(Finding(
                "warn", beat.id,
                "is backup but has no demoted_because. That sentence, in the human's "
                "own framing, is what makes the beat retrievable next talk."))

    duration = deck.meta.get("duration_min")
    if duration:
        budget_s = int(duration) * 60 * 0.85
        total = deck.total_time_s()
        if total > budget_s:
            over = total - budget_s
            candidates = sorted(deck.main_beats(), key=lambda b: -b.time_s)[:3]
            findings.append(Finding(
                "warn", "",
                f"{total // 60} min of beats against a {duration} min slot "
                f"(budget {int(budget_s) // 60} min at 85%). Over by {int(over) // 60} min "
                f"{int(over) % 60} s. Demotion candidates, longest first: "
                + ", ".join(f"{b.id} ({b.time_s}s)" for b in candidates)
                + ". Demote, do not delete."))
    return findings


#: Slots whose name is not the Content field name.
_SLOT_ALIASES = {"definition_half": "definition", "visual_short": "visual"}
_INDEXED = {"annotation": "annotations", "callout": "callouts"}


def slot_text(content: Content, slot_name: str) -> str:
    """The string the compiler will hand to `slot_name`, or "" if none."""
    for prefix, field_name in _INDEXED.items():
        if slot_name.startswith(prefix) and slot_name[len(prefix):].isdigit():
            entries = getattr(content, field_name) or []
            index = int(slot_name[len(prefix):]) - 1
            if index >= len(entries):
                return ""
            entry = entries[index]
            return entry if isinstance(entry, str) else str(entry[0])

    value = getattr(content, _SLOT_ALIASES.get(slot_name, slot_name), None)
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return "\n".join(str(v) for v in value)
    return ""


def raise_on_errors(findings: list[Finding]) -> None:
    errors = [f for f in findings if f.level == "error"]
    if errors:
        raise PresentingError(
            "screenplay will not compile:\n  " + "\n  ".join(str(f) for f in errors))


# ── scene grouping ───────────────────────────────────────────────────────────

@dataclass
class SceneGroup:
    name: str
    kind: str                    # deck | deck3d | raw
    beats: list[Beat] = field(default_factory=list)
    raw_scene: str = ""          # "module:Class" for a raw beat that reuses a scene
    raw_code: str = ""

    def beat_ids(self) -> tuple[str, ...]:
        return tuple(b.id for b in self.beats)


def _camel(text: str) -> str:
    parts = re.split(r"[^0-9a-zA-Z]+", text)
    return "".join(p[:1].upper() + p[1:] for p in parts if p) or "Deck"


def scene_groups(deck: Deck) -> list[SceneGroup]:
    """One scene per section, split at raw beats and 3d boundaries."""
    prefix = _camel(deck.slug)
    groups: list[SceneGroup] = []
    index = 0
    number = 0

    ordered = deck.main_beats() + deck.backup_beats()
    current: SceneGroup | None = None
    current_key: tuple | None = None

    for beat in ordered:
        number += 1
        beat.number = number

        if beat.is_raw():
            index += 1
            groups.append(SceneGroup(
                name=beat.raw.get("class") or f"{prefix}_{index:02d}_{_camel(beat.id)}",
                kind="raw", beats=[beat],
                raw_scene=beat.raw.get("scene", ""),
                raw_code=beat.raw.get("code", ""),
            ))
            current = None
            current_key = None
            continue

        key = (beat.section, beat.scene_type)
        if current is None or key != current_key:
            index += 1
            current = SceneGroup(
                name=f"{prefix}_{index:02d}_{_camel(beat.section or beat.id)}"
                     + ("3D" if beat.scene_type == "3d" else ""),
                kind="deck3d" if beat.scene_type == "3d" else "deck",
            )
            groups.append(current)
            current_key = key
        current.beats.append(beat)

    return groups


# ── runtime ──────────────────────────────────────────────────────────────────

def expand_reveals(step):
    """A step whose visual carries a reveal sequence becomes several steps.

    The layout decided *where* the diagram goes; how it arrives is the
    compiler's call, so the reveal lives here rather than in every layout that
    can hold a figure.
    """
    from .layouts import Element, Step

    revealer = next((e for e in step.elements
                     if getattr(e.mobject, "presenting_reveal", None)), None)
    if revealer is None:
        return [step]

    groups = list(revealer.mobject.presenting_reveal)
    others = [e for e in step.elements if e is not revealer]
    out = []
    for index, group in enumerate(groups):
        elements = [Element(group, revealer.anim, revealer.slot)]
        if index == 0:
            elements += others
        out.append(Step(elements, pause=step.pause))
    return out or [step]


def _overlaps(a, b, tol: float = 0.02) -> bool:
    dx = min(a.get_right()[0], b.get_right()[0]) - max(a.get_left()[0], b.get_left()[0])
    dy = min(a.get_top()[1], b.get_top()[1]) - max(a.get_bottom()[1], b.get_bottom()[1])
    return dx > tol and dy > tol


def _animation(name: str, mobject):
    from manim import Create, FadeIn, GrowFromCenter, Write

    return {"write": Write, "fadein": FadeIn, "create": Create,
            "grow": GrowFromCenter}[name](mobject)


def run_beats(scene, deck: Deck, beat_ids, *, deck_dir: Path | None = None) -> None:
    """Play a run of beats on `scene`. Shared by the 2d and 3d scene bases."""
    from manim import FadeOut

    chrome = Chrome(DeckMeta(deck.meta.get("title", ""), deck.section_names()))
    beats = [deck.beat(bid) for bid in beat_ids]
    # Numbered here, from the whole deck, because a scene only knows its own
    # run of beats — `Beat.number` is set by scene_groups() at compile time and
    # is not carried in the screenplay.
    numbers = {b.id: i for i, b in
               enumerate(deck.main_beats() + deck.backup_beats(), start=1)}
    on_screen: list = []
    needs_break = False

    # Prime the scene with the state the previous scene ended on, added with no
    # animation. A manim scene cannot share mobjects with another one, so
    # without this every scene's video starts blank and the deck cuts to an
    # empty slide at each scene split — the same discontinuity as a beat
    # boundary, just less often. With the state primed, no transition is needed
    # anywhere and the export can leave the slides alone: cross-dissolving two
    # videos is what puts a ghost on the letters.
    order = deck.main_beats() + deck.backup_beats()
    if beats:
        position = next((i for i, b in enumerate(order) if b.id == beats[0].id), 0)
        previous = order[position - 1] if position > 0 else None
        # A raw beat runs code the library never sees, so its final state cannot
        # be reconstructed; that boundary stays a plain cut.
        if previous is not None and not previous.is_raw():
            prior = layout_for(previous)
            prior_built = prior.build(
                content_for(previous, deck, number=numbers[previous.id],
                            deck_dir=deck_dir),
                target=deck.target)
            on_screen = [m for step in prior_built.steps
                         for sub in expand_reveals(step) for m in sub.mobjects()]
            scene.add(*on_screen)
            chrome.sync(
                scene, tier=prior.chrome, section=previous.section,
                number=numbers[previous.id], title=previous.heading or None,
                animate=False, layout=prior.name,
                label=f"Backup · {previous.section}" if previous.backup else None,
            )

    def close_slide() -> None:
        """End the current slide on its settled state."""
        scene.wait(SETTLE_S)
        scene.next_slide()

    for beat in beats:
        if needs_break:
            close_slide()
            needs_break = False

        layout = layout_for(beat)
        built = layout.build(content_for(beat, deck, number=numbers[beat.id],
                                         deck_dir=deck_dir),
                             target=deck.target)

        stale: list = []
        if on_screen:
            if beat.transition == "cut":
                stale = on_screen
            else:
                # `build` keeps the previous beat on screen, but only what the
                # new beat is not about to draw over. Keeping everything writes
                # the new claim on top of the old one and both become
                # unreadable — measured geometrically, because two layouts can
                # occupy the same region under different slot names.
                incoming = built.all_mobjects()
                stale = [m for m in on_screen
                         if any(_overlaps(m, n) for n in incoming)]
            on_screen = [m for m in on_screen if m not in stale]

        # The outgoing beat is still on screen when this slide's video starts,
        # and leaves *inside* it. That is the whole trick: a slide's video plays
        # on entry, so anything cleared before it starts is already gone in
        # frame 0 — the viewer sees the full previous slide, then a near-empty
        # one, then the content animating back in. That dip is the flicker.
        # Leaving the old content in place makes frame 0 identical to the
        # previous slide's last frame, so the hand-off between videos is
        # invisible and the only transition is the one we animate.
        tier = layout.chrome
        leaving, arriving = chrome.sync(
            scene, tier=tier, section=beat.section, number=numbers[beat.id],
            title=beat.heading or None, animate=True, layout=layout.name,
            collect=True,
            label=f"Backup · {beat.section}" if beat.backup else None,
        )

        going = [FadeOut(m) for m in stale] + leaving
        if going:
            scene.play(*going, run_time=0.35)

        static = getattr(layout, "static", False)
        drawn: list = []

        for step in [sub for step in built.steps for sub in expand_reveals(step)]:
            if not step.elements:
                continue
            if needs_break and step.pause:
                close_slide()
                needs_break = False
            if static:
                if arriving:
                    scene.play(*arriving, run_time=0.3)
                    arriving = []
                scene.add(*step.mobjects())
                scene.wait(0.4)
            else:
                # The incoming title arrives with the beat's first content, not
                # against the outgoing one.
                scene.play(*arriving,
                           *[_animation(e.anim, e.mobject) for e in step.elements
                             if e.anim != "none"])
                arriving = []
            drawn += step.mobjects()
            needs_break = step.pause

        if arriving:                      # a beat with no drawable steps
            scene.play(*arriving, run_time=0.3)
            arriving = []

        # What was actually put on stage, not what the layout returned. A step
        # carrying a reveal sequence is expanded into its sub-groups, and those
        # are what get added — so clearing the parent group later removes
        # nothing and the beat stays visible under the next one.
        on_screen = on_screen + drawn

    # Settle the final slide. The break is taken *before* each step rather than
    # after, so the scene ends on real content — a next_slide() at the very end
    # would leave a trailing slide holding nothing but this wait.
    scene.wait(SETTLE_S)


class DeckSceneBase:
    """Mixin carrying the deck wiring for a generated scene class."""

    deck_path: str = ""
    beat_ids: tuple[str, ...] = ()

    def _deck(self) -> Deck:
        return load(Path(self.deck_path))

    def construct(self):                      # pragma: no cover - manim entry point
        from manim import ManimColor

        from .tokens import PALETTE

        # A plain hex string here renders fine and then crashes manim-slides on
        # save, which reads `.to_hex()` off it. Set a real colour and repaint.
        self.camera.background_color = ManimColor(PALETTE.ground)
        self.camera.init_background()
        deck = self._deck()
        run_beats(self, deck, self.beat_ids, deck_dir=Path(self.deck_path).parent)


def _apply_reversing_preference() -> None:
    """Let a render opt out of manim-slides' reversed-animation pass.

    Reversing costs about as much again as the animation itself — 25-30s per
    slide at 2K — and it buys only animated *backward* navigation. Set
    PRESENTING_SKIP_REVERSING=1 when the deck is needed sooner than that;
    stepping back then jumps instead of animating.
    """
    if os.environ.get("PRESENTING_SKIP_REVERSING") != "1":
        return
    from manim_slides.slide.base import BaseSlide

    BaseSlide.skip_reversing = True


def make_scene_bases():
    """Built lazily so importing this module does not require a manim renderer."""
    _apply_reversing_preference()
    from manim import ThreeDScene
    from manim_slides import Slide, ThreeDSlide

    class DeckScene(DeckSceneBase, Slide):
        pass

    class DeckScene3D(DeckSceneBase, ThreeDSlide):
        pass

    return DeckScene, DeckScene3D


# ── emission ─────────────────────────────────────────────────────────────────

HEADER = '''"""{title}

Generated from {screenplay} by presenting_lib.compile. Do not hand-edit: change
the screenplay and re-compile. Positioning lives in presenting_lib/layouts —
there is deliberately none here.

Render (2K — this is the deck, not a draft):
    uv run manim-slides render {module} {scenes} -qp
Present:
    uv run manim-slides present {scenes}
Export a self-contained HTML deck (this is how the deck gets watched back):
    uv run manim-slides convert --one-file --offline \\
        --use-template identity/out/revealjs.html \\
        {scenes} {slug}.html
"""

from pathlib import Path

from presenting_lib.compile import make_scene_bases

DECK_PATH = Path(__file__).resolve().parent / "{screenplay_rel}"

DeckScene, DeckScene3D = make_scene_bases()
'''


def emit(deck: Deck, groups: list[SceneGroup], *, module_path: Path,
         screenplay_path: Path) -> str:
    import os

    scenes = " ".join(g.name for g in groups)
    # Both paths stay relative: the module resolves the screenplay next to
    # itself so the deck directory can be moved or copied, and the command
    # lines are meant to be pasted from the manim-videos root.
    screenplay_rel = os.path.relpath(screenplay_path, module_path.parent)
    repo = Path(__file__).resolve().parent.parent
    try:
        module_rel = module_path.relative_to(repo)
        screenplay_display = screenplay_path.relative_to(repo)
    except ValueError:
        module_rel, screenplay_display = module_path, screenplay_path

    out = [HEADER.format(
        title=deck.meta.get("title", deck.slug),
        screenplay=screenplay_display,
        screenplay_rel=screenplay_rel,
        module=module_rel,
        scenes=scenes,
        slug=deck.slug,
    )]

    imports = [g.raw_scene for g in groups if g.raw_scene]
    for ref in sorted(set(imports)):
        module, _, cls = ref.partition(":")
        out.append(f"from {module} import {cls}")
    if imports:
        out.append("")

    for group in groups:
        if group.kind == "raw":
            beat = group.beats[0]
            if group.raw_scene:
                cls = group.raw_scene.partition(":")[2]
                out.append(f"\nclass {group.name}({cls}):")
                out.append(f'    """raw beat {beat.id!r} — reuses an existing scene, untouched."""')
                out.append("")
                # Where this beat sits in the deck. A raw scene skips the
                # catalog, so nothing else can tell it — and without it a bare
                # canvas cannot draw the footer every other slide carries.
                out.append(f"    section_name = {beat.section!r}")
                out.append(f"    slide_number = {beat.number or 1}")
                out.append(f"    deck_sections = {tuple(deck.section_names())!r}")
                out.append("")
            else:
                out.append(f"\n# raw beat {beat.id!r} — supplied verbatim by the screenplay")
                out.append(group.raw_code.rstrip())
                out.append("")
            continue

        base = "DeckScene3D" if group.kind == "deck3d" else "DeckScene"
        ids = ", ".join(repr(b.id) for b in group.beats)
        out.append(f"\nclass {group.name}({base}):")
        out.append(f'    """{group.beats[0].section or deck.slug}"""')
        out.append("")
        out.append("    deck_path = str(DECK_PATH)")
        out.append(f"    beat_ids = ({ids},)" if len(group.beats) == 1
                   else f"    beat_ids = ({ids})")
        out.append("")

    return "\n".join(out).rstrip("\n") + "\n"


def compile_deck(screenplay_path: Path | str, out_path: Path | str,
                 *, strict: bool = True) -> tuple[Path, list[Finding]]:
    screenplay_path = Path(screenplay_path).resolve()
    out_path = Path(out_path).resolve()
    deck = load(screenplay_path)
    findings = [Finding("note", "", f"downscaled {d}")
                for d in assets.normalize_images(screenplay_path.parent)]
    findings += validate(deck)
    if strict:
        raise_on_errors(findings)
    groups = scene_groups(deck)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(emit(deck, groups, module_path=out_path,
                             screenplay_path=screenplay_path))
    return out_path, findings


def command_lines(deck: Deck, groups: list[SceneGroup], module_path: Path) -> str:
    scenes = " ".join(g.name for g in groups)
    return "\n".join([
        f"uv run manim-slides render {module_path} {scenes} -qp",
        f"uv run manim-slides present {scenes}",
        # The quotes around fade are part of the value: manim-slides drops it
        # into the reveal.js config verbatim, so an unquoted one emits a bare
        # JS identifier and Reveal.initialize throws.
        f"uv run manim-slides convert --one-file --offline "
        f"--use-template identity/out/revealjs.html "
        f"{scenes} {deck.slug}.html",
    ])
