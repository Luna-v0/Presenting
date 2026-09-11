"""Tables built cell by cell, so the design arrives with the data.

manim's `Table` draws a grid and then drops text into it, which means the only
way to animate it is to draw the whole grid at once and then fill it — the
lines show up before there is anything to line up. The decks in this repo
already do it the other way round: a cell is a box *and* its text together, the
header lands first, then one row at a time. That reads as a table being built
rather than a table being filled in, and it is the shape this module keeps.

Structure carries the header, ground carries the body. An accented row uses its
ramp, so the fill brings its own text colour with it.
"""

from __future__ import annotations

from manim import Rectangle, VGroup

from .errors import SlotOverflow
from .measure import metrics
from .slots import Slot
from .tokens import GEOMETRY, GROUND, PALETTE, STRUCTURE, TYPE

CELL_PAD_X = 0.34
CELL_PAD_Y = 0.20
MIN_COL_W = 1.0


def _column_widths(rows: list[list[str]]) -> list[float]:
    m = metrics(TYPE.family("body"), TYPE.size("body"))
    count = max(len(row) for row in rows)
    widths = []
    for column in range(count):
        widest = max(
            (m.width_of(str(row[column])) for row in rows if column < len(row)),
            default=0.0,
        )
        widths.append(max(widest + 2 * CELL_PAD_X, MIN_COL_W))
    return widths


def _row_height() -> float:
    m = metrics(TYPE.family("body"), TYPE.size("body"))
    return m.single_line_height + 2 * CELL_PAD_Y


def _cell(value: str, width: float, height: float, *, surface, bold: bool,
          centre) -> VGroup:
    box = Rectangle(
        width=width, height=height,
        color=PALETTE.structure_stroke,
        fill_color=surface.fill or PALETTE.ground,
        fill_opacity=1.0,
        stroke_width=GEOMETRY.stroke_weight * 0.45,
    )
    box.move_to(centre)
    cell = VGroup(box)
    if str(value) != "":
        inner = Slot("cell", centre[0], centre[1], width - 2 * CELL_PAD_X * 0.7,
                     height - 2 * CELL_PAD_Y * 0.5, style="body")
        cell.add(inner.fit_text(str(value), style="body", on=surface,
                                weight="BOLD" if bold else "NORMAL"))
    return cell


def build(rows, slot: Slot, *, accent_rows=None, accent_cols=None,
          header: bool = True) -> tuple[VGroup, list[VGroup]]:
    """Lay a table out in `slot`.

    Returns the whole table plus a reveal sequence: the header, then one row at
    a time. The compiler turns that sequence into slides, the same way it does
    for a diagram.

    Row and column numbers in `accent_rows` / `accent_cols` are 1-based and
    count the header as row 1, matching how the screenplay reads.
    """
    import numpy as np

    rows = [[str(cell) for cell in row] for row in rows]
    if not rows:
        raise SlotOverflow(slot.name, "", layout="table-accented")

    accent_rows = set(accent_rows or [])
    accent_cols = set(accent_cols or [])
    widths = _column_widths(rows)
    height = _row_height()
    total_w, total_h = sum(widths), height * len(rows)

    scale = min(slot.w / total_w, slot.h / total_h, 1.0)
    if scale * TYPE.size("body") < TYPE.min_legible_body:
        raise SlotOverflow(
            slot.name, " | ".join(rows[0]),
            min_size=round(TYPE.min_legible_body, 1),
            tried_size=round(scale * TYPE.size("body"), 1),
            layout="table-accented",
        )

    # Lay out at full size, then scale the finished table — scaling the text
    # with the boxes keeps the padding proportional, which per-cell shrinking
    # does not.
    steps: list[VGroup] = []
    y = total_h / 2 - height / 2
    for index, row in enumerate(rows):
        x = -total_w / 2
        group = VGroup()
        for column, value in enumerate(row):
            width = widths[column]
            is_header = header and index == 0
            accented = (index + 1) in accent_rows or (column + 1) in accent_cols
            surface = (PALETTE.GREEN if accented
                       else STRUCTURE if is_header else GROUND)
            group.add(_cell(value, width, height, surface=surface,
                            bold=is_header, centre=np.array([x + width / 2, y, 0.0])))
            x += width
        steps.append(group)
        y -= height

    whole = VGroup(*steps)
    whole.scale(scale)
    whole.move_to(slot.center)
    whole.presenting_reveal = steps
    return whole, steps
