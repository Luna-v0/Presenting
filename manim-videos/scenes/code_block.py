"""Code on a slide, alone or under the figure it produces.

Two builders for the screenplay's generic `visual.builder` hook
(`presenting_lib.compile.visual_for` imports `module:function`, calls it with
`args`, and hands the returned `build(slot)` to the layout):

    visual:
      kind: constructible
      sub: geometry
      intent: the read_csv call, verbatim from assets/verified_snippets.py
      builder: scenes.code_block:code
      args:
        code: |
          escolas = pd.read_csv("data/escolas.csv")

    visual:
      kind: constructible            # referential when the image is a still to source
      sub: geometry
      intent: the hull drawn around the points
      builder: scenes.code_block:figure_with_code
      args:
        image: decks/geo-folium/assets/built/cre4_hull.png
        code: hull = pts.convex_hull

Code is never wrapped: a wrapped line of code is a different line of code. The
type steps down from body to the legibility floor until the whole block fits,
then raises `SlotOverflow` — the same contract as `Slot.fit_text`. Monospace,
ink on the structure fill (the box `activity-setup` puts its example in), no
syntax colour: the deck has two accents and both already mean something.

An empty or whitespace-only `code` raises `LayoutContractError` as soon as the
builder is asked for, which is during `compile.validate`, so the beat is named
in a validation error instead of rendering as an empty box.

`image` is resolved against manim-videos/, the directory every render runs
from. If it is not there yet, the figure half is the library's labelled
placeholder, so a deck renders before its stills exist.
"""

from __future__ import annotations

from pathlib import Path

from manim import Group, ImageMobject, RoundedRectangle, Text, VGroup

from presenting_lib.errors import LayoutContractError, SlotOverflow
from presenting_lib.placeholders import VisualSpec, placeholder
from presenting_lib.slots import Slot, floor_size
from presenting_lib.tokens import GEOMETRY, PALETTE, STRUCTURE, TYPE

REPO = Path(__file__).resolve().parent.parent
PAD_X, PAD_Y = 0.4, 0.3
GAP = 0.25
#: The most of the slot's height a code panel may take under a figure.
CODE_SHARE = 0.45


def _sizes():
    """Body down to the legibility floor, one step at a time."""
    size, floor = TYPE.size("body"), floor_size("body")
    while size > floor + 1e-9:
        yield size
        size -= 1.0
    yield floor


def _require_code(code: str) -> str:
    """The code itself, or LayoutContractError: an empty panel says nothing."""
    if not isinstance(code, str) or not code.strip():
        raise LayoutContractError(
            f"code_block was given no code ({code!r}). A code panel with nothing in "
            "it renders as an empty box; put the beat's code under visual.args.code.")
    return code


def _code_text(code: str, max_w: float, max_h: float, *, slot_name: str) -> Text:
    """The largest monospace block that fits, or SlotOverflow."""
    source = _require_code(code).expandtabs(4).rstrip("\n")
    colour = STRUCTURE.check_text_colour(None)
    for size in _sizes():
        # One Text for the whole block, so Pango lays the lines out: baselines
        # stay even and leading spaces keep their width, which is what makes
        # indentation survive.
        mob = Text(source, font=TYPE.family_mono, font_size=size, color=colour)
        if mob.width <= max_w and mob.height <= max_h:
            return mob
    floor = round(floor_size("body"), 1)
    raise SlotOverflow(slot_name, source, layout="code_block", min_size=floor,
                       tried_size=floor)


def _panel(text: Text) -> VGroup:
    box = RoundedRectangle(
        width=text.width + 2 * PAD_X, height=text.height + 2 * PAD_Y,
        corner_radius=GEOMETRY.corner_radius,
        color=PALETTE.structure_stroke, fill_color=PALETTE.structure_fill,
        fill_opacity=1.0, stroke_width=GEOMETRY.stroke_weight * 0.6,
    )
    text.move_to(box.get_center())
    return VGroup(box, text)


def _region(slot: Slot) -> Slot:
    """A full-frame slot (full-bleed-figure) still keeps to the safe area."""
    if slot.w >= GEOMETRY.frame_width - 1e-6:
        return slot.inset(GEOMETRY.safe_inset)
    return slot


def code(*, code: str):
    """A code panel filling as much of the slot as the code needs."""
    _require_code(code)

    def build(slot: Slot):
        region = _region(slot)
        text = _code_text(code, region.w - 2 * PAD_X, region.h - 2 * PAD_Y,
                          slot_name=f"{slot.name}:code")
        panel = _panel(text)
        panel.move_to(region.center)
        return panel

    return build


def figure_with_code(*, image: str, code: str, intent: str = "",
                     kind: str = "constructible", sub: str = "geometry"):
    """A figure with the code that made it in a panel underneath."""
    _require_code(code)

    def build(slot: Slot):
        region = _region(slot)
        text = _code_text(code, region.w - 2 * PAD_X,
                          region.h * CODE_SHARE - 2 * PAD_Y,
                          slot_name=f"{slot.name}:code")
        panel = _panel(text)

        fig_h = region.h - panel.height - GAP
        fig_slot = Slot(f"{slot.name}:figure", region.x, region.top - fig_h / 2,
                        region.w, fig_h, role="visual")
        path = REPO / image
        if path.exists():
            figure = ImageMobject(str(path))
            figure.scale(min(fig_slot.w / figure.width, fig_slot.h / figure.height))
        else:
            figure = placeholder(VisualSpec(kind=kind, sub=sub, intent=intent,
                                            asset=image), fig_slot)

        # Stack figure over panel and centre the pair, so a wide figure that
        # does not use its full height does not leave a gap above the code.
        total = figure.height + GAP + panel.height
        top = region.y + total / 2
        figure.move_to([region.x, top - figure.height / 2, 0.0])
        panel.move_to([region.x, top - figure.height - GAP - panel.height / 2, 0.0])
        return Group(figure, panel)

    return build
