"""A term, then what it means. Optionally a figure alongside.

The term arrives first and alone — the beat is the moment of naming, and a
definition already on screen when the name lands spends that moment.
"""

from __future__ import annotations

from ..chrome import CONTENT_FULL, FULL
from ..slots import Slot
from ._bands import band, below, columns
from .base import Content, Layout, Step, register

_TERM = band(CONTENT_FULL, "term", top=CONTENT_FULL.top, height=1.1, width=12.0,
             style="title", align="center")
_DEF_FULL = below(CONTENT_FULL, "definition", under=_TERM, gap=0.42, width=11.0,
                  style="body", align="center")
_XS, _COL_W = columns(CONTENT_FULL, 2)
_DEF_HALF = Slot("definition_half", _XS[0], _DEF_FULL.y, _COL_W, _DEF_FULL.h,
                 style="body", align="center")
_VISUAL = Slot("visual", _XS[1], _DEF_FULL.y, _COL_W, _DEF_FULL.h, role="visual")


@register
class TermReveal(Layout):
    name = "term-reveal"
    chrome = FULL
    accepts = ("term", "definition", "visual")
    requires = ("term", "definition")
    slots = {"term": _TERM, "definition": _DEF_FULL,
             "definition_half": _DEF_HALF, "visual": _VISUAL}
    text_slots = ("term", "definition", "definition_half")

    def active_slots(self, content: Content) -> set[str]:
        if content.visual is not None:
            return {"term", "definition_half", "visual"}
        return {"term", "definition"}

    def render(self, content: Content, *, target: str = "manim"):
        steps = [Step().add(
            self.text("term", content.term, content=content, target=target,
                      style="title", weight="BOLD"), "write", "term")]

        slot_name = "definition_half" if content.visual is not None else "definition"
        second = Step().add(
            self.text(slot_name, content.definition, content=content, target=target,
                      style="body"), "fadein", slot_name)
        if content.visual is not None:
            second.add(self.visual("visual", content.visual, content=content),
                       "fadein", "visual")
        steps.append(second)
        return steps
