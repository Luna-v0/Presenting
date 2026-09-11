"""The figure takes the whole frame. Chrome tier `none` — no footer, no dots.

The 3b1b case: nothing on screen but the thing being talked about. The compiler
has to animate the chrome *out* before this beat and back in after it, which is
why chrome tier is per-beat state rather than a deck-level setting.
"""

from __future__ import annotations

from ..chrome import CONTENT_NONE, NONE
from ..slots import Slot
from .base import Content, Layout, Step, register


@register
class FullBleedFigure(Layout):
    name = "full-bleed-figure"
    chrome = NONE
    accepts = ("visual",)
    requires = ("visual",)
    slots = {"visual": Slot("visual", 0.0, 0.0, CONTENT_NONE.w, CONTENT_NONE.h,
                            role="visual")}
    text_slots = ()

    def render(self, content: Content, *, target: str = "manim"):
        return [Step().add(self.visual("visual", content.visual, content=content),
                           "fadein", "visual")]
