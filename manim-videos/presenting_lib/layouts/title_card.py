"""The opening slide. Chrome is special: the title *is* the content."""

from __future__ import annotations

from manim import VGroup

from ..chrome import BARE
from ..slots import Slot, safe_area
from ..tokens import GROUND, MUTED
from ._bands import rule
from .base import Content, Layout, Step, register

_AREA = safe_area()


@register
class TitleCard(Layout):
    name = "title-card"
    chrome = BARE
    accepts = ("title", "subtitle", "author", "date", "affiliation")
    requires = ("title",)
    slots = {
        "title": Slot("title", 0.0, 1.65, 12.0, 1.9, style="display", align="center"),
        "subtitle": Slot("subtitle", 0.0, -0.15, 11.0, 0.8, style="claim", align="center"),
        "author": Slot("author", 0.0, -1.45, 10.0, 0.6, style="body", align="center"),
        "affiliation": Slot("affiliation", 0.0, -2.15, 10.0, 0.55, style="caption",
                            align="center"),
        "date": Slot("date", 0.0, -2.75, 10.0, 0.5, style="caption", align="center"),
    }

    def render(self, content: Content, *, target: str = "manim"):
        title = self.text("title", content.title, content=content, target=target,
                          style="display", weight="BOLD")
        # Follows the rendered title: a two-line title would otherwise have a
        # line drawn through it.
        under = rule(title.get_bottom()[1] - 0.25, min(title.width + 0.8, 12.0))
        first = Step().add(title, "write", "title").add(under, "create", "rule")

        second = Step()
        if content.subtitle:
            second.add(self.text("subtitle", content.subtitle, content=content,
                                 target=target, style="claim", slant="ITALIC"),
                       "fadein", "subtitle")
        for name, surface, style in (("author", GROUND, "body"),
                                     ("affiliation", MUTED, "caption"),
                                     ("date", MUTED, "caption")):
            value = getattr(content, name)
            if value:
                second.add(self.text(name, value, content=content, target=target,
                                     style=style, on=surface), "fadein", name)
        steps = [first]
        if second.elements:
            steps.append(second)
        return steps
