"""A single statement, held. Bare chrome.

The thesis slide, or the warning. One of the two layouts where a full sentence
on screen is right.
"""

from __future__ import annotations

from manim import RoundedRectangle, VGroup

from ..chrome import FOOTER
from ..slots import Slot
from ..tokens import GEOMETRY, GROUND, PALETTE
from .base import Content, Layout, Step, register


@register
class Callout(Layout):
    name = "callout"
    chrome = FOOTER
    accepts = ("statement",)
    requires = ("statement",)
    slots = {
        "statement": Slot("statement", 0.0, 0.0, 10.6, 3.4, style="claim",
                          align="center"),
    }

    def render(self, content: Content, *, target: str = "manim"):
        slot = self.slots["statement"]
        label = slot.inset(0.55, 0.45).fit_text(
            content.statement, style="claim", on=GROUND, layout=self.name, target=target)
        frame = RoundedRectangle(
            width=min(label.width + 1.5, slot.w),
            height=label.height + 1.1,
            corner_radius=GEOMETRY.corner_radius,
            color=PALETTE.green.mid,
            stroke_width=GEOMETRY.stroke_weight,
            fill_opacity=0.0,
        )
        frame.move_to(slot.center)
        label.move_to(frame.get_center())
        return [Step().add(frame, "create", "statement").add(label, "write", "statement")]
