"""A claim and a table, built row by row, with one row or column marked.

The mark is the point of the layout: an unmarked table is a wall of numbers and
the audience has to be told where to look. Accent fills carry their own dark
text, so a marked row stays readable.

The table arrives the way the decks in this repo already build them — header
first, then one row at a time, each cell bringing its own box. See
presenting_lib/tables.py for why that is not manim's `Table`.
"""

from __future__ import annotations

from manim import VGroup

from ..chrome import CONTENT_FULL, FULL
from ..slots import Slot
from ._bands import band, below
from .base import Content, Layout, Step, register

_CLAIM = band(CONTENT_FULL, "claim", top=CONTENT_FULL.top, height=1.0, width=12.4,
              style="claim", align="top")
_TABLE = below(CONTENT_FULL, "table", under=_CLAIM, gap=0.3, role="mixed")
_TABLE_TALL = Slot("table_tall", CONTENT_FULL.x, CONTENT_FULL.y,
                   CONTENT_FULL.w, CONTENT_FULL.h, role="mixed")


@register
class TableAccented(Layout):
    name = "table-accented"
    chrome = FULL
    accepts = ("claim", "table", "accent_rows", "accent_cols", "caption")
    requires = ("table",)
    slots = {"claim": _CLAIM, "table": _TABLE, "table_tall": _TABLE_TALL}
    text_slots = ("claim",)

    def active_slots(self, content: Content) -> set[str]:
        return {"claim", "table"} if content.claim else {"table_tall"}

    def render(self, content: Content, *, target: str = "manim"):
        from .. import tables

        steps = []
        if content.claim:
            steps.append(Step().add(
                self.text("claim", content.claim, content=content, target=target,
                          style="claim", align="top"), "write", "claim"))

        slot_name = "table" if content.claim else "table_tall"
        table = content.table
        if isinstance(table, VGroup):
            whole = self.slots[slot_name].place(table)
        else:
            whole, _ = tables.build(
                table, self.slots[slot_name],
                accent_rows=content.accent_rows,
                accent_cols=content.accent_cols,
            )
        steps.append(Step().add(whole, "fadein", slot_name))
        return steps
