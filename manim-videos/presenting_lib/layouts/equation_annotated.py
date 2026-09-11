"""An equation with up to two annotations under it — the two-accent case.

Highlighting two terms of one formula, one green and one yellow, is the reason
the one-accent-per-beat rule died. An annotation may name an accent; when it
does, the annotation box and the term it marks share that accent's ramp, and
the accent's fill carries its own dark text.

The accents' *meanings* are deck-wide and still unassigned (identity/tokens.yaml,
plan §11.1). The library will draw them correctly regardless — it is
`compile.validate_accents` that refuses to let a generated deck encode anything
with colour before the meanings exist.
"""

from __future__ import annotations

from manim import RoundedRectangle, VGroup

from ..chrome import CONTENT_FULL, FULL
from ..errors import LayoutContractError
from ..slots import Slot
from ..tokens import GEOMETRY, PALETTE, STRUCTURE
from ._bands import columns
from .base import Content, Layout, Step, register

_EQ_H = 2.5
_EQUATION = Slot("equation", CONTENT_FULL.x, CONTENT_FULL.top - _EQ_H / 2,
                 11.8, _EQ_H, role="mixed", align="center")
_XS, _COL_W = columns(CONTENT_FULL, 2)
_ANN_TOP = _EQUATION.bottom - 0.45
_ANN_H = _ANN_TOP - CONTENT_FULL.bottom


def _annotation(i: int) -> Slot:
    return Slot(f"annotation{i + 1}", _XS[i], _ANN_TOP - _ANN_H / 2, _COL_W, _ANN_H,
                style="body", align="center")


@register
class EquationAnnotated(Layout):
    name = "equation-annotated"
    chrome = FULL
    accepts = ("equation", "annotations", "claim")
    requires = ("equation",)
    slots = {
        "equation": _EQUATION,
        "annotation1": _annotation(0),
        "annotation2": _annotation(1),
    }
    text_slots = ("annotation1", "annotation2")

    def render(self, content: Content, *, target: str = "manim"):
        steps = [Step().add(
            self.slots["equation"].fit_math(content.equation, layout=self.name,
                                            target=target),
            "write", "equation")]

        annotations = list(content.annotations or [])
        if len(annotations) > 2:
            raise LayoutContractError(
                f"{self.name!r} has two annotation slots; got {len(annotations)}. "
                "Two accents means two annotations — a third would need a third accent."
            )
        for i, entry in enumerate(annotations):
            text, accent = (entry, None) if isinstance(entry, str) else entry
            surface = PALETTE.surface(accent) if accent else STRUCTURE
            slot = self.slots[f"annotation{i + 1}"]
            label = slot.inset(0.3, 0.2).fit_text(
                text, style="body", on=surface, layout=self.name, target=target)
            box = RoundedRectangle(
                width=slot.w, height=min(label.height + 0.6, slot.h),
                corner_radius=GEOMETRY.corner_radius,
                color=surface.stroke or PALETTE.structure_stroke,
                fill_color=surface.fill or PALETTE.structure_fill,
                fill_opacity=1.0,
                stroke_width=GEOMETRY.stroke_weight * 0.7,
            )
            box.move_to(slot.center)
            label.move_to(box.get_center())
            steps.append(Step().add(VGroup(box, label), "fadein", slot.name))
        return steps
