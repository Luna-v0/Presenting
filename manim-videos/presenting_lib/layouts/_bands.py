"""Shared band arithmetic, so every layout carves the same content area."""

from __future__ import annotations

import numpy as np
from manim import Line

from ..chrome import CONTENT_BARE, CONTENT_FULL, CONTENT_NONE
from ..slots import Slot
from ..tokens import GEOMETRY, PALETTE

GUTTER = GEOMETRY.gutter


def band(area: Slot, name: str, *, top: float, height: float, width: float | None = None,
         **kwargs) -> Slot:
    """A horizontal band of `area`, measured down from its top."""
    width = area.w if width is None else width
    return Slot(name, area.x, top - height / 2, width, height, **kwargs)


def below(area: Slot, name: str, *, under: Slot, gap: float = GUTTER,
          bottom: float | None = None, width: float | None = None, **kwargs) -> Slot:
    """Everything from just under `under` down to `bottom` (default: area floor)."""
    bottom = area.bottom if bottom is None else bottom
    top = under.bottom - gap
    return Slot(name, area.x, (top + bottom) / 2, area.w if width is None else width,
                top - bottom, **kwargs)


def columns(area: Slot, count: int, *, gap: float = GUTTER) -> list[float]:
    """Centre x of each of `count` equal columns, and the column width."""
    width = (area.w - gap * (count - 1)) / count
    xs = [area.left + width / 2 + i * (width + gap) for i in range(count)]
    return xs, width


def rule(y: float, width: float, *, colour: str | None = None) -> Line:
    return Line(
        np.array([-width / 2, y, 0.0]),
        np.array([width / 2, y, 0.0]),
        color=colour or PALETTE.green.mid,
        stroke_width=GEOMETRY.stroke_weight,
    )


__all__ = ["band", "below", "columns", "rule", "GUTTER",
           "CONTENT_FULL", "CONTENT_BARE", "CONTENT_NONE"]
