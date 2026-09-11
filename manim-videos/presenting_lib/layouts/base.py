"""What a layout is.

A layout is a fixed set of named slots plus a chrome tier. It takes `Content`
— the fields a beat carries — and returns `Built`: an ordered list of reveal
steps. The layout decides *where*; the compiler decides *how* (which animation,
where the slide breaks). Keeping those apart is what lets a beat be reordered,
demoted or re-timed without touching how it is drawn.

This catalog is the manim target's. The slides target is written per deck and
reads these names as a description of intent, not as geometry to copy — a slide
deck and a manim video are different media and are meant to look different.

A layout that is handed content it has no slot for raises rather than silently
dropping it. Silently dropping is how a screenplay ends up with a claim nobody
ever sees on screen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable

from manim import Mobject, VGroup

from ..chrome import BARE, FULL, NONE
from ..errors import LayoutContractError, UnknownLayout
from ..slots import Slot

# Content fields every layout tolerates — they are deck-level, not slot-level.
UNIVERSAL = frozenset({"title", "section", "number", "beat_id", "notes", "backup_of"})


@dataclass
class Content:
    """The subset of a beat that a layout can place.

    Everything is optional; each layout declares which of these it accepts, and
    which it requires. Free-form extras go in `extra` and are the escape hatch
    for a layout's own vocabulary.
    """

    title: str | None = None
    section: str = ""
    number: int = 1
    beat_id: str = ""
    notes: str = ""

    claim: str | None = None
    on_slide: list[str] | None = None
    caption: str | None = None
    subtitle: str | None = None
    author: str | None = None
    date: str | None = None
    affiliation: str | None = None

    visual: object | None = None          # Mobject, callable(Slot)->Mobject, or VisualSpec
    items: list[str] | None = None
    callouts: list | None = None          # str, or (text, (u, v)) anchored in the visual
    label_l: str | None = None
    label_r: str | None = None
    panel_l: object | None = None
    panel_r: object | None = None
    term: str | None = None
    definition: str | None = None
    equation: str | None = None
    annotations: list | None = None       # str, or (text, accent_name)
    table: object | None = None
    accent_rows: list[int] | None = None
    accent_cols: list[int] | None = None
    statement: str | None = None
    prompt: str | None = None
    task: str | None = None
    example: str | None = None
    instructions: str | None = None
    constraints: list[str] | str | None = None
    backup_of: str | None = None

    extra: dict = field(default_factory=dict)

    def present(self) -> set[str]:
        return {
            name
            for name, value in vars(self).items()
            if name != "extra" and value not in (None, "", [], {})
        }


@dataclass
class Element:
    """One mobject, with a hint about how it should arrive.

    `slot` is the slot the mobject is bound to, and review checks it against
    that slot's rectangle. Leave it empty for anything that legitimately spans
    slots — a leader line runs from a callout into the figure and belongs to
    neither, so binding it to either one reports a false overflow *and* a false
    collision.
    """

    mobject: Mobject
    anim: str = "fadein"      # write | fadein | create | grow | none
    slot: str = ""

    def __post_init__(self):
        if self.anim not in ("write", "fadein", "create", "grow", "none"):
            raise ValueError(f"unknown animation hint {self.anim!r}")


@dataclass
class Step:
    """A group of elements that arrive together, then the slide waits."""

    elements: list[Element] = field(default_factory=list)
    pause: bool = True        # False = keep going without a click

    def add(self, mobject, anim: str = "fadein", slot: str = "") -> "Step":
        self.elements.append(Element(mobject, anim, slot))
        return self

    def mobjects(self) -> list[Mobject]:
        return [e.mobject for e in self.elements]


@dataclass
class Built:
    """A laid-out beat, ready for the compiler."""

    layout: str
    chrome: str
    title: str | None
    steps: list[Step]

    def all_mobjects(self) -> list[Mobject]:
        """A flat list, not a VGroup — images and placeholders are `Group`s and
        a VGroup refuses to hold them."""
        return [e.mobject for step in self.steps for e in step.elements]

    def slot_of(self, mobject) -> str:
        for step in self.steps:
            for element in step.elements:
                if element.mobject is mobject:
                    return element.slot
        return ""


class Layout:
    """Base class. Subclasses declare slots and implement `render`."""

    name: str = ""
    chrome: str = FULL
    slots: dict[str, Slot] = {}
    accepts: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()
    #: slots whose text budget should be measured. Defaults to every text slot.
    text_slots: tuple[str, ...] | None = None

    # ── contract ──────────────────────────────────────────────────────────
    def validate(self, content: Content) -> None:
        present = content.present()
        allowed = UNIVERSAL | set(self.accepts)
        stray = sorted(present - allowed)
        if stray:
            raise LayoutContractError(
                f"layout {self.name!r} has no slot for: {', '.join(stray)}.\n"
                f"  It accepts: {', '.join(sorted(self.accepts)) or '(nothing)'}.\n"
                "  Either pick a layout that has that slot, or drop the field — a\n"
                "  layout silently ignoring content is how a claim ends up written\n"
                "  but never shown."
            )
        missing = [name for name in self.requires if name not in present]
        if missing:
            raise LayoutContractError(
                f"layout {self.name!r} needs {', '.join(missing)} and did not get it."
            )

    def build(self, content: Content, *, target: str = "manim") -> Built:
        self.validate(content)
        steps = list(self.render(content, target=target))
        return Built(layout=self.name, chrome=self.chrome,
                     title=content.title if self.chrome == FULL else None,
                     steps=steps)

    # ── subclass hook ─────────────────────────────────────────────────────
    def render(self, content: Content, *, target: str = "manim") -> Iterable[Step]:
        raise NotImplementedError

    # ── helpers for subclasses ────────────────────────────────────────────
    def text(self, slot_name: str, value: str, *, content: Content, target: str,
             style: str | None = None, on=None, align: str | None = None,
             weight: str = "NORMAL", slant: str = "NORMAL"):
        from ..tokens import GROUND

        slot = self.slots[slot_name]
        # YAML happily hands back an int for `date: 2026`. Coerce here rather
        # than making every screenplay remember to quote scalars.
        return slot.fit_text(
            str(value), style=style, on=on or GROUND, align=align, weight=weight,
            slant=slant, layout=self.name, target=target,
        )

    def visual(self, slot_name: str, spec, *, content: Content):
        from ..placeholders import resolve_visual

        slot = self.slots[slot_name]
        return slot.place(resolve_visual(spec, slot, beat_id=content.beat_id))

    def active_slots(self, content: Content) -> set[str]:
        """Which slots this content actually uses.

        Several layouts carry alternates — a tall visual slot when there is no
        caption, a short one when there is. Anything filling slots without
        building has to know which of a pair is live, or it drops the same
        picture in twice.
        """
        return set(self.slots)

    def measured_text_slots(self) -> tuple[str, ...]:
        if self.text_slots is not None:
            return self.text_slots
        return tuple(name for name, slot in self.slots.items() if slot.role == "text")


# ── registry ─────────────────────────────────────────────────────────────────

_REGISTRY: dict[str, Layout] = {}


def register(layout_cls: type[Layout]) -> type[Layout]:
    instance = layout_cls()
    if not instance.name:
        raise ValueError(f"{layout_cls.__name__} has no name")
    _REGISTRY[instance.name] = instance
    return layout_cls


def get_layout(name: str) -> Layout:
    if name == "raw":
        raise UnknownLayout(
            "layout 'raw' is the escape hatch: the compiler passes its scene code "
            "through untouched and the library never sees it."
        )
    try:
        return _REGISTRY[name]
    except KeyError:
        raise UnknownLayout(
            f"no layout {name!r}. Catalog: {', '.join(sorted(_REGISTRY))}, plus 'raw'."
        ) from None


def catalog() -> dict[str, Layout]:
    return dict(_REGISTRY)
