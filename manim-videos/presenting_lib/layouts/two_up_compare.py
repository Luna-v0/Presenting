"""Two panels side by side, each with a label above it."""

from __future__ import annotations

from ..chrome import CONTENT_FULL, FULL
from ..slots import Slot
from ._bands import columns
from .base import Content, Layout, Step, register

_XS, _W = columns(CONTENT_FULL, 2)
_LABEL_H = 0.72
_PANEL_TOP = CONTENT_FULL.top - _LABEL_H - 0.22
_PANEL_H = _PANEL_TOP - CONTENT_FULL.bottom


def _label(name, x):
    return Slot(name, x, CONTENT_FULL.top - _LABEL_H / 2, _W, _LABEL_H,
                style="claim", align="center")


def _panel(name, x):
    return Slot(name, x, _PANEL_TOP - _PANEL_H / 2, _W, _PANEL_H, role="visual")


@register
class TwoUpCompare(Layout):
    name = "two-up-compare"
    chrome = FULL
    accepts = ("claim", "label_l", "label_r", "panel_l", "panel_r")
    requires = ("label_l", "label_r")
    slots = {
        "label_l": _label("label_l", _XS[0]),
        "label_r": _label("label_r", _XS[1]),
        "panel_l": _panel("panel_l", _XS[0]),
        "panel_r": _panel("panel_r", _XS[1]),
    }
    text_slots = ("label_l", "label_r")

    def render(self, content: Content, *, target: str = "manim"):
        left = Step()
        left.add(self.text("label_l", content.label_l, content=content, target=target,
                           style="claim", weight="BOLD"), "write", "label_l")
        if content.panel_l is not None:
            left.add(self.visual("panel_l", content.panel_l, content=content),
                     "fadein", "panel_l")

        right = Step()
        right.add(self.text("label_r", content.label_r, content=content, target=target,
                            style="claim", weight="BOLD"), "write", "label_r")
        if content.panel_r is not None:
            right.add(self.visual("panel_r", content.panel_r, content=content),
                      "fadein", "panel_r")
        return [left, right]
