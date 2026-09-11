"""The slide that stays on screen while people work.

Unusual for manim: this one must hold still and stay legible for ten minutes
rather than animate. The compiler renders it static by construction — no
reveal steps, no timed anything — and review should check it for legibility
over duration rather than at a glance.
"""

from __future__ import annotations

import numpy as np
from manim import Dot, RoundedRectangle, VGroup

from ..chrome import CONTENT_FULL, FULL
from ..errors import SlotOverflow
from ..slots import Slot
from ..tokens import GEOMETRY, GROUND, PALETTE, STRUCTURE, TYPE
from ._bands import GUTTER
from .base import Content, Layout, Step, register

_CONSTRAINTS_W = 4.6
_INSTRUCTIONS_W = CONTENT_FULL.w - _CONSTRAINTS_W - GUTTER
#: Everything on this slide arrives at once and then holds for ten minutes, so
#: there is no reveal order to protect and no reason to hug the top edge.
_INSTRUCTIONS = Slot("instructions", CONTENT_FULL.left + _INSTRUCTIONS_W / 2,
                     CONTENT_FULL.y, _INSTRUCTIONS_W, CONTENT_FULL.h,
                     style="body", align="left")
_CONSTRAINTS = Slot("constraints", CONTENT_FULL.right - _CONSTRAINTS_W / 2,
                    CONTENT_FULL.y, _CONSTRAINTS_W, CONTENT_FULL.h,
                    style="body", align="top-left")


@register
class ActivityParking(Layout):
    name = "activity-parking"
    chrome = FULL
    accepts = ("instructions", "constraints", "claim")
    requires = ("instructions",)
    slots = {"instructions": _INSTRUCTIONS, "constraints": _CONSTRAINTS}
    #: static by construction — everything arrives in one step and then holds.
    static = True

    def render(self, content: Content, *, target: str = "manim"):
        step = Step(pause=True)
        step.add(self.text("instructions", content.instructions, content=content,
                           target=target, style="body", align="left"),
                 "fadein", "instructions")

        constraints = content.constraints
        if constraints:
            if isinstance(constraints, str):
                constraints = [constraints]
            slot = self.slots["constraints"]
            body = slot.inset(0.35, 0.3).fit_text(
                "\n".join(f"— {c}" for c in constraints), style="body",
                on=STRUCTURE, align="top-left", layout=self.name, target=target)
            box = RoundedRectangle(
                width=slot.w, height=min(body.height + 0.8, slot.h),
                corner_radius=GEOMETRY.corner_radius,
                color=PALETTE.structure_stroke, fill_color=PALETTE.structure_fill,
                fill_opacity=1.0, stroke_width=GEOMETRY.stroke_weight * 0.6,
            )
            box.move_to(np.array([slot.x, slot.y, 0.0]))
            body.move_to(box.get_center())
            step.add(VGroup(box, body), "fadein", "constraints")
        return [step]
