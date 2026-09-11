"""Slots: the only way content gets positioned.

A layout is a set of named rectangles. Content goes into a rectangle; nothing
calls `.next_to`, `.shift`, or `font_size=` at a call site. That constraint is
what makes "text is outside the safe area" a thing the library can *know*
rather than a thing a human has to notice on a projector.

`fit_text` is the load-bearing method. It shrinks, but only down to the
legibility floor — below that it raises `SlotOverflow` rather than rendering
something nobody at the back of the room can read. Manim renders text off-frame
and exits zero; that silence is the root cause of the bad-text problem, and a
hard failure is the only kind of feedback an agent reliably fixes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path

import numpy as np
from manim import DOWN, LEFT, ORIGIN, RIGHT, UP, MathTex, Text, VGroup

from .errors import SlotOverflow
from .measure import metrics, wrap
from .tokens import GEOMETRY, GROUND, TYPE, Surface

BUDGETS_PATH = Path(__file__).resolve().parent.parent / "identity" / "budgets.json"

# Shrinking below the step beneath you is not a smaller title, it is a title
# that does not fit. Body and caption bottom out at the measured legibility
# floor; everything above them bottoms out one step down.
_FLOOR_STEP = {
    "display": "title",
    "title": "claim",
    "claim": "body",
    "body": None,
    "caption": None,
    "footer": None,
}

#: Pillow measures a hair narrow; leaving 1.5% of the slot unclaimed during the
#: search means the real render usually agrees on the first try.
_SEARCH_MARGIN = 0.985

_ALIGN_VECTORS = {
    "center": (0.0, 0.0),
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
    "top": (0.0, 1.0),
    "bottom": (0.0, -1.0),
    "top-left": (-1.0, 1.0),
    "top-right": (1.0, 1.0),
    "bottom-left": (-1.0, -1.0),
    "bottom-right": (1.0, -1.0),
}


@lru_cache(maxsize=1)
def _budgets() -> dict:
    if BUDGETS_PATH.exists():
        return json.loads(BUDGETS_PATH.read_text())
    return {}


def budget_for(target: str, layout: str, slot: str) -> int | None:
    return (_budgets().get(target, {}).get(layout, {}) or {}).get(slot)


def floor_size(style: str) -> float:
    """The smallest this style may shrink to before overflow becomes an error.

    Chrome is exempt from the legibility floor. That floor is about text the
    room has to read; a section label and a page number are glanced at, and
    holding them to it makes the footer shout over the slide.
    """
    if style in TYPE.CHROME_STYLES:
        return TYPE.size(style)
    below = _FLOOR_STEP.get(style)
    step_floor = TYPE.size(below) if below else 0.0
    return max(step_floor, TYPE.min_legible_body)


@dataclass(frozen=True)
class Slot:
    """A named rectangle in frame coordinates, centred on (x, y)."""

    name: str
    x: float
    y: float
    w: float
    h: float
    role: str = "text"          # text | visual | mixed
    align: str = "center"
    style: str = "body"         # default type step
    line_spacing: float = 1.0   # multiplier on the font's natural line advance

    # ── geometry ──────────────────────────────────────────────────────────
    @property
    def left(self) -> float:
        return self.x - self.w / 2

    @property
    def right(self) -> float:
        return self.x + self.w / 2

    @property
    def bottom(self) -> float:
        return self.y - self.h / 2

    @property
    def top(self) -> float:
        return self.y + self.h / 2

    @property
    def center(self) -> np.ndarray:
        return np.array([self.x, self.y, 0.0])

    def inset(self, dx: float = 0.0, dy: float | None = None) -> "Slot":
        dy = dx if dy is None else dy
        return replace(self, w=self.w - 2 * dx, h=self.h - 2 * dy)

    def anchor_point(self, align: str | None = None) -> np.ndarray:
        ax, ay = _ALIGN_VECTORS[align or self.align]
        return np.array([self.x + ax * self.w / 2, self.y + ay * self.h / 2, 0.0])

    def anchor_edge(self, align: str | None = None) -> np.ndarray:
        ax, ay = _ALIGN_VECTORS[align or self.align]
        return ax * RIGHT + ay * UP

    def contains(self, mobject, tol: float = 1e-6) -> bool:
        return (
            mobject.get_left()[0] >= self.left - tol
            and mobject.get_right()[0] <= self.right + tol
            and mobject.get_bottom()[1] >= self.bottom - tol
            and mobject.get_top()[1] <= self.top + tol
        )

    # ── placement ─────────────────────────────────────────────────────────
    def place(self, mobject, *, align: str | None = None, fit: bool = True,
              pad: float = 0.0):
        """Scale a mobject down to fit (never up) and position it by `align`."""
        box_w, box_h = self.w - 2 * pad, self.h - 2 * pad
        if fit and mobject.width > 0 and mobject.height > 0:
            scale = min(box_w / mobject.width, box_h / mobject.height, 1.0)
            if scale < 1.0:
                mobject.scale(scale)
        target = self.inset(pad).anchor_point(align or self.align)
        mobject.move_to(target, aligned_edge=self.anchor_edge(align or self.align))
        return mobject

    # ── text ──────────────────────────────────────────────────────────────
    def fit_text(self, text: str, *, style: str | None = None,
                 on: Surface = GROUND, color: str | None = None,
                 weight: str = "NORMAL", slant: str = "NORMAL",
                 align: str | None = None, layout: str | None = None,
                 target: str = "manim", family: str | None = None) -> VGroup:
        """Wrap and size `text` to this slot, or raise `SlotOverflow`.

        Returns a VGroup of one Text per line, positioned at an even line
        advance — manim's own newline handling spaces by rendered glyph height,
        so lines without descenders sit closer together than lines with them.
        """
        style = style or self.style
        colour = on.check_text_colour(color)
        family = family or TYPE.family(style)
        nominal = TYPE.size(style)
        floor = floor_size(style)
        align = align or self.align

        # Pillow prefilters, manim decides. Pango rounds glyph advances, so
        # Pillow can under-measure a string by a few percent — a candidate size
        # that passes the prefilter still gets built and measured for real, and
        # a real overflow steps down rather than raising. Only the floor raises.
        size = nominal
        while size is not None and size >= floor - 1e-9:
            m = metrics(family, size, weight, slant)
            lines = wrap(text, m, self.w * _SEARCH_MARGIN, weight=weight, slant=slant)
            if lines is not None:
                height = (m.single_line_height
                          + m.line_advance * self.line_spacing * (len(lines) - 1))
                if height <= self.h:
                    group = _stack(lines, family=family, font_size=size, color=colour,
                                   weight=weight, slant=slant,
                                   line_advance=m.line_advance * self.line_spacing,
                                   align=align)
                    if len(group) == 0:
                        return group
                    _at(group, self, align)
                    if self.contains(group, tol=0.02):
                        return group
            size = _next_size_down(size, floor)

        raise SlotOverflow(
            self.name, text,
            budget=budget_for(target, layout, self.name) if layout else None,
            layout=layout, target=target,
            min_size=round(floor, 1), tried_size=round(floor, 1),
        )

    def fit_math(self, tex: str, *, on: Surface = GROUND, color: str | None = None,
                 align: str | None = None, max_scale: float = 2.6,
                 layout: str | None = None, target: str = "manim") -> MathTex:
        """Place an equation. Scales freely — an equation is figure, not body text.

        It grows as well as shrinks: a short formula rendered at its nominal
        size sits marooned in the middle of a slot built to hold it, and on a
        beat whose whole point is the formula that reads as a mistake. The cap
        stops a two-symbol expression becoming a billboard.

        The legibility floor still applies, measured on the rendered height of
        the expression rather than on a font size, because LaTeX has no font
        size we could compare against the scale.
        """
        colour = on.check_text_colour(color)
        mob = MathTex(tex, color=colour, font_size=TYPE.size("claim"))
        scale = min(self.w / mob.width, self.h / mob.height, max_scale)
        mob.scale(scale)

        min_height = TYPE.min_legible_body / TYPE.base_font_size * 0.34
        if mob.height < min_height:
            raise SlotOverflow(
                self.name, tex,
                budget=budget_for(target, layout, self.name) if layout else None,
                layout=layout, target=target,
                min_size=round(TYPE.min_legible_body, 1), tried_size=None,
            )
        return self.place(mob, align=align, fit=False)


def _next_size_down(size: float, floor: float) -> float | None:
    nxt = size - 1.0
    if nxt < floor - 1e-9:
        return floor if size > floor + 1e-9 else None
    return nxt


def _stack(lines, *, family, font_size, color, weight, slant, line_advance, align):
    """One Text per line at an exact, even line advance."""
    kwargs = dict(font=family, font_size=font_size, color=color)
    if str(weight).upper() == "BOLD":
        kwargs["weight"] = "BOLD"
    if str(slant).upper() in ("ITALIC", "OBLIQUE"):
        kwargs["slant"] = "ITALIC"

    # A blank line still consumes its slot in the ladder — that is what makes a
    # paragraph break a paragraph break — but it does not become a mobject.
    # Rendering it as a space produces a Text with no points, and every
    # alignment call on it fails deep inside manim.
    mobs = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        mob = Text(line, **kwargs)
        mob.move_to(np.array([0.0, -i * line_advance, 0.0]))
        mobs.append(mob)

    group = VGroup(*mobs)
    if not mobs:
        return group

    horizontal = "left" if "left" in align else "right" if "right" in align else "center"
    if horizontal == "left":
        for mob in mobs:
            mob.align_to(group, LEFT)
    elif horizontal == "right":
        for mob in mobs:
            mob.align_to(group, RIGHT)
    else:
        for mob in mobs:
            mob.set_x(group.get_x())
    return group


def _at(group: VGroup, slot: Slot, align: str):
    group.move_to(slot.anchor_point(align), aligned_edge=slot.anchor_edge(align))
    return group


def safe_area() -> Slot:
    g = GEOMETRY
    return Slot("safe", 0.0, 0.0, g.safe_width, g.safe_height, role="mixed")


def frame() -> Slot:
    g = GEOMETRY
    return Slot("frame", 0.0, 0.0, g.frame_width, g.frame_height, role="mixed")
