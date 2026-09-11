"""Tutorials only: the task, with a worked example if one helps.

Paired with `activity-parking`, which is the slide that stays up while people
actually work.
"""

from __future__ import annotations

from manim import RoundedRectangle, VGroup

from ..chrome import CONTENT_FULL, FULL
from ..slots import Slot
from ..tokens import GEOMETRY, GROUND, PALETTE, STRUCTURE, TYPE
from ._bands import band, below
from .base import Content, Layout, Step, register

_TASK = band(CONTENT_FULL, "task", top=CONTENT_FULL.top, height=2.0, width=12.0,
             style="claim", align="top")
_EXAMPLE = below(CONTENT_FULL, "example", under=_TASK, gap=0.35, width=11.4,
                 style="body", align="center")


@register
class ActivitySetup(Layout):
    name = "activity-setup"
    chrome = FULL
    accepts = ("task", "example", "claim")
    requires = ("task",)
    slots = {"task": _TASK, "example": _EXAMPLE}

    def render(self, content: Content, *, target: str = "manim"):
        steps = [Step().add(
            self.text("task", content.task, content=content, target=target,
                      style="claim", align="top"), "write", "task")]

        if content.example:
            slot = self.slots["example"]
            label = slot.inset(0.5, 0.35).fit_text(
                content.example, style="body", on=STRUCTURE, align="center",
                family=TYPE.family_mono, layout=self.name, target=target)
            box = RoundedRectangle(
                width=min(label.width + 1.0, slot.w),
                height=min(label.height + 0.8, slot.h),
                corner_radius=GEOMETRY.corner_radius,
                color=PALETTE.structure_stroke, fill_color=PALETTE.structure_fill,
                fill_opacity=1.0, stroke_width=GEOMETRY.stroke_weight * 0.6,
            )
            box.move_to(slot.center)
            label.move_to(box.get_center())
            steps.append(Step().add(VGroup(box, label), "fadein", "example"))
        return steps
