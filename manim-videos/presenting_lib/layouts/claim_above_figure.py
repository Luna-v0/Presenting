"""The workhorse. A claim across the top, the figure under it.

Expect most beats to land here. The claim slot is deliberately shallow — two
lines at the claim step — because a claim that needs three lines is a paragraph,
and a paragraph on a slide is documentation.
"""

from __future__ import annotations

from ..chrome import CONTENT_FULL, FULL
from ..slots import Slot
from ..tokens import MUTED
from ._bands import band, below
from .base import Content, Layout, Step, register

_CLAIM = band(CONTENT_FULL, "claim", top=CONTENT_FULL.top, height=1.15,
              width=12.4, style="claim", align="top")
_CAPTION = Slot("caption", CONTENT_FULL.x, CONTENT_FULL.bottom + 0.21, 12.0, 0.42,
                style="caption", align="center")


@register
class ClaimAboveFigure(Layout):
    name = "claim-above-figure"
    chrome = FULL
    accepts = ("claim", "visual", "caption")
    requires = ("claim",)
    slots = {
        "claim": _CLAIM,
        # Two visual slots: the tall one when there is no caption, the short one
        # when an attribution line has to sit under the figure.
        "visual": below(CONTENT_FULL, "visual", under=_CLAIM, gap=0.28, role="visual"),
        "visual_short": below(CONTENT_FULL, "visual_short", under=_CLAIM, gap=0.28,
                              bottom=_CAPTION.top + 0.12, role="visual"),
        "caption": _CAPTION,
    }
    text_slots = ("claim", "caption")

    def active_slots(self, content: Content) -> set[str]:
        visual = "visual_short" if content.caption else "visual"
        return {"claim", visual} | ({"caption"} if content.caption else set())

    def render(self, content: Content, *, target: str = "manim"):
        steps = [Step().add(
            self.text("claim", content.claim, content=content, target=target,
                      style="claim", align="top"), "write", "claim")]

        if content.visual is not None:
            slot_name = "visual_short" if content.caption else "visual"
            figure = Step().add(
                self.visual(slot_name, content.visual, content=content),
                "fadein", slot_name)
            if content.caption:
                figure.add(self.text("caption", content.caption, content=content,
                                     target=target, style="caption", on=MUTED),
                           "fadein", "caption")
            steps.append(figure)
        return steps
