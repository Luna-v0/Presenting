"""Marking a term, and why the two targets do it differently.

Same tokens, different treatment. A pale tint fading in is a much weaker beat
than a stroke drawing itself in the accent's mid — so in manim the stroke
animates and the tint arrives underneath it, while in Slides nothing moves and
the tint has to do all the work on its own.

Nothing here decides *what* to mark. That is a categorical encoding with a fixed
deck-wide meaning, and while `accents.*.meaning` is unassigned in
identity/tokens.yaml, `compile.validate` refuses generated beats that use one.
"""

from __future__ import annotations

from manim import Create, FadeIn, SurroundingRectangle, VGroup

from .tokens import GEOMETRY, PALETTE


def mark(mobject, accent: str = "green", *, target: str = "manim",
         buff: float = 0.12):
    """Wrap `mobject` in its accent. Returns (marks, animations).

    `marks` is the VGroup to add to the scene; `animations` is empty for the
    static target, where the mark simply exists.
    """
    ramp = PALETTE.accent(accent)

    tint = SurroundingRectangle(
        mobject, buff=buff, corner_radius=GEOMETRY.corner_radius * 0.5,
        stroke_width=0, fill_color=ramp.tint, fill_opacity=1.0,
    )
    stroke = SurroundingRectangle(
        mobject, buff=buff, corner_radius=GEOMETRY.corner_radius * 0.5,
        color=ramp.mid, stroke_width=GEOMETRY.stroke_weight, fill_opacity=0.0,
    )

    if target != "manim":
        # Static: no stroke at all. A hairline outline that never draws itself
        # reads as a box, not as a mark — the tint alone is stronger.
        return VGroup(tint), []

    return VGroup(tint, stroke), [FadeIn(tint, run_time=0.4),
                                  Create(stroke, run_time=0.6)]


def text_colour_on(accent: str) -> str:
    """The only text colour permitted on that accent's tint."""
    return PALETTE.accent(accent).dark
