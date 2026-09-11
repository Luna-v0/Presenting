"""A section break. Bare chrome — nothing but the name of what comes next.

The progress dots advance here (the compiler bumps the section index), but the
footer is not on screen to show it. That is deliberate: the dot moves while the
audience is looking at the section name, and they see the new state on the
first content beat after it.
"""

from __future__ import annotations

from ..chrome import FOOTER
from ..slots import Slot
from ._bands import rule
from .base import Content, Layout, Step, register


@register
class SectionBreak(Layout):
    name = "section-break"
    chrome = FOOTER
    accepts = ("section", "claim")
    requires = ("section",)
    slots = {
        "section": Slot("section", 0.0, 0.55, 12.0, 2.0, style="display", align="center"),
        "claim": Slot("claim", 0.0, -1.35, 10.5, 1.2, style="body", align="center"),
    }

    def render(self, content: Content, *, target: str = "manim"):
        name = self.text("section", content.section, content=content, target=target,
                         style="display", weight="BOLD")
        under = rule(name.get_bottom()[1] - 0.28, min(name.width + 0.9, 12.0))
        step = Step().add(name, "write", "section").add(under, "create", "rule")
        steps = [step]
        if content.claim:
            steps.append(Step().add(
                self.text("claim", content.claim, content=content, target=target,
                          style="body", slant="ITALIC"), "fadein", "claim"))
        return steps
