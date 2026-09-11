"""A claim and a list that arrives one item at a time.

Items are laid out at a fixed advance rather than by `arrange`, so the spacing
does not change depending on which lines happen to have descenders. On the
Slides target this expands into sibling slides — near-identical consecutive
slides are fine and the human's beamer decks already do it.
"""

from __future__ import annotations

import numpy as np
from manim import Dot, VGroup

from ..chrome import CONTENT_FULL, FULL
from ..errors import SlotOverflow
from ..slots import Slot
from ..tokens import GROUND, PALETTE, TYPE
from ._bands import band, below
from .base import Content, Layout, Step, register

_CLAIM = band(CONTENT_FULL, "claim", top=CONTENT_FULL.top, height=1.05,
              width=12.4, style="claim", align="top")
_ITEMS = below(CONTENT_FULL, "items", under=_CLAIM, gap=0.32, width=11.6,
               style="body", align="top-left")
#: No claim means no reason to leave the claim band empty.
_TALL_INSET = 0.3
_ITEMS_TALL = Slot("items_tall", _ITEMS.x,
                   (CONTENT_FULL.top - _TALL_INSET + CONTENT_FULL.bottom) / 2,
                   _ITEMS.w, CONTENT_FULL.h - _TALL_INSET,
                   style="body", align="top-left")

_BULLET_GAP = 0.42
_ITEM_GAP = 0.34


@register
class BuildList(Layout):
    name = "build-list"
    chrome = FULL
    accepts = ("claim", "items")
    requires = ("items",)
    slots = {"claim": _CLAIM, "items": _ITEMS, "items_tall": _ITEMS_TALL}
    text_slots = ("claim", "items")

    def active_slots(self, content: Content) -> set[str]:
        return {"claim", "items"} if content.claim else {"items_tall"}

    def render(self, content: Content, *, target: str = "manim"):
        steps = []
        if content.claim:
            steps.append(Step().add(
                self.text("claim", content.claim, content=content, target=target,
                          style="claim", align="top"), "write", "claim"))

        items = list(content.items or [])
        area = self.slots["items"] if content.claim else self.slots["items_tall"]
        text_slot = Slot("items", area.x + _BULLET_GAP / 2, area.y,
                         area.w - _BULLET_GAP, area.h,
                         style="body", align="top-left")

        blocks = [
            text_slot.fit_text(item, style="body", on=GROUND, align="top-left",
                               layout=self.name, target=target)
            for item in items
        ]

        total = sum(b.height for b in blocks) + _ITEM_GAP * max(len(blocks) - 1, 0)
        if total > area.h:
            raise SlotOverflow(
                "items", " / ".join(items), layout=self.name, target=target,
                min_size=round(TYPE.min_legible_body, 1),
            )

        # Centred on the slot, not hugging its top. The positions are computed
        # from the *finished* block, so nothing moves as items arrive — the
        # reason to top-align in the first place does not apply once the layout
        # knows every item up front, and top-aligning three short items in a
        # tall slot leaves half the slide empty.
        y = area.y + total / 2
        for block in blocks:
            block.move_to(np.array([text_slot.left, y, 0.0]),
                          aligned_edge=np.array([-1.0, 1.0, 0.0]))
            marker = Dot(radius=0.062, color=PALETTE.green.mid)
            marker.move_to(np.array([area.left + 0.08,
                                     block.get_top()[1] - block.submobjects[0].height / 2,
                                     0.0]))
            steps.append(Step().add(VGroup(marker, block), "fadein", area.name))
            y -= block.height + _ITEM_GAP
        return steps
