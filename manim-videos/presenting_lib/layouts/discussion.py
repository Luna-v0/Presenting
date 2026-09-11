"""One prompt, and nothing to read while people think. Bare chrome.

Gated by the brief's `interaction` field, and never generated for a `showcase`
— a showcase with a discussion prompt is a failed showcase. The gate lives in
the screenplay skill; the layout itself is unopinionated so the human can still
place one by hand.
"""

from __future__ import annotations

from ..chrome import BARE
from ..slots import Slot
from ..tokens import PALETTE
from ._bands import rule
from .base import Content, Layout, Step, register


@register
class Discussion(Layout):
    name = "discussion"
    chrome = BARE
    accepts = ("prompt",)
    requires = ("prompt",)
    slots = {
        "prompt": Slot("prompt", 0.0, -0.1, 11.0, 3.6, style="claim", align="center"),
    }

    def render(self, content: Content, *, target: str = "manim"):
        prompt = self.text("prompt", content.prompt, content=content, target=target,
                           style="claim")
        above = rule(prompt.get_top()[1] + 0.55, 2.2)
        return [Step().add(above, "create", "rule").add(prompt, "write", "prompt")]
