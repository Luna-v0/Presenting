"""A figure on the left, up to three callouts down the right, leaders in green.

A callout may name an anchor in the figure as (u, v) in 0..1 normalised
coordinates; when it does, a leader line is drawn from the callout to that
point. Without an anchor there is no leader — a leader pointing at nothing is
worse than no leader.

A leader stops at the *edge* of whatever it points at, never inside it. The
anchor names a target; running the line on to the target's centre draws it
across the label it is pointing to.
"""

from __future__ import annotations

import numpy as np
from manim import Line, VGroup

from ..chrome import CONTENT_FULL, FULL
from ..errors import LayoutContractError
from ..slots import Slot
from ..tokens import GEOMETRY, PALETTE, STRUCTURE
from .base import Content, Layout, Step, register

_COL_W = 4.15
_FIG_W = CONTENT_FULL.w - _COL_W - GEOMETRY.gutter
_FIG_X = CONTENT_FULL.left + _FIG_W / 2
_COL_X = CONTENT_FULL.right - _COL_W / 2
_SLOT_H = 1.42
_GAP = (CONTENT_FULL.h - 3 * _SLOT_H) / 2


def _callout_slot(i: int) -> Slot:
    top = CONTENT_FULL.top - i * (_SLOT_H + _GAP)
    return Slot(f"callout{i + 1}", _COL_X, top - _SLOT_H / 2, _COL_W, _SLOT_H,
                style="body", align="center")


LEADER_GAP = 0.09


def _shapes(mobject) -> list:
    """Every drawable in `mobject` except text, and never inside text.

    A `Text` is a VGroup of per-glyph shapes, and a glyph is always the
    smallest thing containing a point that lands on a label. Clipping to it
    stops the leader on the letters instead of on the box around them — which
    is the difference between pointing at a node and drawing through it.
    """
    from manim import MathTex, Text

    out = []
    for child in getattr(mobject, "submobjects", []):
        if isinstance(child, (Text, MathTex)):
            continue
        if child.has_points():
            out.append(child)
        out += _shapes(child)
    return out


def _clip_to_target(start: np.ndarray, end: np.ndarray, figure) -> np.ndarray:
    """Pull `end` back to the boundary of the smallest shape containing it.

    The anchor points at a node; the line has to stop on that node's edge. The
    smallest containing shape is the node itself rather than the whole diagram,
    which is why the candidates are sorted by area.
    """
    candidates = []
    for mob in _shapes(figure):
        left, right = mob.get_left()[0], mob.get_right()[0]
        bottom, top = mob.get_bottom()[1], mob.get_top()[1]
        if left <= end[0] <= right and bottom <= end[1] <= top:
            area = max(right - left, 1e-6) * max(top - bottom, 1e-6)
            candidates.append((area, left, right, bottom, top))
    if not candidates:
        return end

    _, left, right, bottom, top = min(candidates)
    direction = end - start
    if abs(direction[0]) < 1e-9 and abs(direction[1]) < 1e-9:
        return end

    # The first place the segment crosses the box, coming from `start`.
    crossings = []
    for edge, axis in ((left, 0), (right, 0), (bottom, 1), (top, 1)):
        if abs(direction[axis]) < 1e-9:
            continue
        t = (edge - start[axis]) / direction[axis]
        if not 0.0 <= t <= 1.0:
            continue
        point = start + t * direction
        other = 1 - axis
        lo, hi = (bottom, top) if other == 1 else (left, right)
        if lo - 1e-6 <= point[other] <= hi + 1e-6:
            crossings.append(t)
    if not crossings:
        return end
    best = min(crossings)
    hit = start + best * direction
    back = np.linalg.norm(direction)
    if back > 1e-9:
        hit = hit - direction / back * LEADER_GAP
    return hit


@register
class FigureWithCallouts(Layout):
    name = "figure-with-callouts"
    chrome = FULL
    accepts = ("claim", "visual", "callouts")
    requires = ("visual", "callouts")
    slots = {
        "visual": Slot("visual", _FIG_X, CONTENT_FULL.y, _FIG_W, CONTENT_FULL.h,
                       role="visual"),
        "callout1": _callout_slot(0),
        "callout2": _callout_slot(1),
        "callout3": _callout_slot(2),
    }
    text_slots = ("callout1", "callout2", "callout3")

    def render(self, content: Content, *, target: str = "manim"):
        callouts = list(content.callouts or [])
        if len(callouts) > 3:
            raise LayoutContractError(
                f"{self.name!r} has three callout slots; got {len(callouts)}. "
                "A fourth is a second beat."
            )

        figure = self.visual("visual", content.visual, content=content)
        steps = [Step().add(figure, "fadein", "visual")]

        fig_slot = self.slots["visual"]
        for i, entry in enumerate(callouts):
            text, anchor = (entry, None) if isinstance(entry, str) else entry
            slot_name = f"callout{i + 1}"
            box = self._boxed(slot_name, text, content=content, target=target)
            step = Step().add(box, "fadein", slot_name)
            if anchor is not None:
                u, v = anchor
                point = np.array([
                    fig_slot.left + u * fig_slot.w,
                    fig_slot.bottom + v * fig_slot.h,
                    0.0,
                ])
                end = _clip_to_target(box.get_left(), point, figure)
                leader = Line(box.get_left(), end, color=PALETTE.green.mid,
                              stroke_width=GEOMETRY.stroke_weight * 0.6, buff=0.12)
                # No slot: it spans from the callout into the figure on purpose.
                step.add(leader, "create")
            steps.append(step)
        return steps

    def _boxed(self, slot_name: str, text: str, *, content: Content, target: str) -> VGroup:
        from manim import RoundedRectangle

        slot = self.slots[slot_name]
        label = slot.inset(0.28, 0.18).fit_text(
            text, style="body", on=STRUCTURE, layout=self.name, target=target)
        box = RoundedRectangle(
            width=slot.w, height=max(label.height + 0.55, 0.8),
            corner_radius=GEOMETRY.corner_radius,
            color=PALETTE.structure_stroke, fill_color=PALETTE.structure_fill,
            fill_opacity=1.0, stroke_width=GEOMETRY.stroke_weight * 0.6,
        )
        box.move_to(slot.center)
        label.move_to(box.get_center())
        return VGroup(box, label)
