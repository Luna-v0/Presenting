"""One sentence, centred, nothing else. Bare chrome.

One of only two layouts where full sentences belong on screen (the other is
`callout`). Everywhere else, on-slide text is fragments.
"""

from __future__ import annotations

from ..chrome import FOOTER
from ..slots import Slot
from .base import Content, Layout, Step, register


@register
class ClaimOnly(Layout):
    name = "claim-only"
    chrome = FOOTER
    accepts = ("claim",)
    requires = ("claim",)
    slots = {
        "claim": Slot("claim", 0.0, 0.0, 11.0, 4.2, style="claim", align="center"),
    }

    def render(self, content: Content, *, target: str = "manim"):
        return [Step().add(
            self.text("claim", content.claim, content=content, target=target,
                      style="claim"), "write", "claim")]
