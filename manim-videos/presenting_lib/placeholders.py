"""Placeholders, so a deck with zero assets still renders end to end.

That property is what turns "go find PNGs" into a stage rather than a blocker,
and in a pipeline with a review loop it matters more than it looks: you need to
watch a rough deck back *before* committing to any assets, because watching it
is how you find out which assets are worth sourcing.

Three kinds, each labelled with what it is waiting for:

    referential    a file that has to be found or photographed
    constructible  a diagram that has to be built — labelled with its *intent*
    chart          a plot — labelled with its data source
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from manim import (
    DashedVMobject,
    Group,
    ImageMobject,
    Rectangle,
    VGroup,
)

from .slots import Slot
from .tokens import GEOMETRY, GROUND, MUTED, PALETTE, STRUCTURE, TYPE

REPO = Path(__file__).resolve().parent.parent
ASSET_ROOTS = [REPO / "scenes" / "assets", REPO / "presentation_assets", REPO]

KINDS = ("constructible", "referential", "chart", "none")


@dataclass
class VisualSpec:
    """What a beat's visual slot is supposed to contain."""

    kind: str = "none"
    sub: str = ""
    intent: str = ""
    asset: str | None = None
    source: str = ""                      # chart: where the numbers come from
    builder: Callable[[Slot], object] | None = None

    def __post_init__(self):
        if self.kind not in KINDS:
            raise ValueError(f"visual.kind must be one of {KINDS}, got {self.kind!r}")

    def resolved_asset(self, deck_dir: Path | None = None) -> Path | None:
        if not self.asset:
            return None
        candidate = Path(self.asset)
        if candidate.is_absolute() and candidate.exists():
            return candidate
        roots = ([deck_dir, deck_dir / "assets" / "raw", deck_dir / "assets" / "built"]
                 if deck_dir else [])
        for root in [*roots, *ASSET_ROOTS]:
            if root and (root / candidate).exists():
                return root / candidate
        return None


def resolve_visual(spec, slot: Slot, *, beat_id: str = "", deck_dir: Path | None = None):
    """Turn whatever the beat declared into a mobject that fits `slot`."""
    if spec is None:
        return VGroup()
    if callable(spec) and not isinstance(spec, VisualSpec):
        return spec(slot)
    if not isinstance(spec, VisualSpec):
        return spec                                    # already a mobject
    if spec.kind == "none":
        return VGroup()

    path = spec.resolved_asset(deck_dir)
    if path is not None:
        image = ImageMobject(str(path))
        scale = min(slot.w / image.width, slot.h / image.height)
        image.scale(scale)
        return Group(image)

    if spec.builder is not None:
        return spec.builder(slot)

    return placeholder(spec, slot, beat_id=beat_id)


def placeholder(spec: VisualSpec, slot: Slot, *, beat_id: str = "") -> VGroup:
    """A labelled box saying what is missing and what it has to accomplish."""
    box = Rectangle(
        width=slot.w, height=slot.h,
        stroke_width=GEOMETRY.stroke_weight * 0.6,
        color=PALETTE.structure_stroke,
        fill_color=PALETTE.structure_fill,
        fill_opacity=0.35,
    )
    # A Rectangle is born centred on the origin. The tag and label below are
    # placed at the slot's absolute coordinates, so the box has to be moved
    # there too — otherwise the group spans from the origin to the slot and a
    # single move_to at the end centres that union, which puts every part of an
    # off-centre placeholder in the wrong place. Centred slots hid this.
    box.move_to(slot.center)
    outline = DashedVMobject(box, num_dashes=int((slot.w + slot.h) * 6), dashed_ratio=0.55)
    outline.set_fill(PALETTE.structure_fill, opacity=0.35)

    kind_line = {
        "referential": (f"[{spec.sub or 'image'}] "
                        f"{spec.asset or (f'assets/raw/{beat_id}.png' if beat_id else 'unsourced')}"),
        "constructible": f"[diagram: {spec.sub or 'figure'}]",
        "chart": "[chart]",
    }[spec.kind]

    body = {
        "referential": spec.intent or "no intent recorded",
        "constructible": spec.intent or "no intent recorded",
        "chart": spec.source or spec.intent or "no data source recorded",
    }[spec.kind]

    inner = slot.inset(min(0.45, slot.w * 0.08), min(0.35, slot.h * 0.1))
    tag_slot = Slot(f"{slot.name}_tag", inner.x, inner.top - 0.22, inner.w, 0.44,
                    style="caption", align="center")
    text_slot = Slot(f"{slot.name}_intent", inner.x, inner.y - 0.15,
                     inner.w, max(inner.h - 0.9, 0.5), style="body", align="center")

    tag = tag_slot.fit_text(kind_line, on=MUTED, style="caption")
    label = text_slot.fit_text(body, on=GROUND, style="body")

    return VGroup(outline, tag, label)


def missing_assets(specs) -> list[VisualSpec]:
    """Every spec that would render as a placeholder — what SHOTS.md is for."""
    return [s for s in specs
            if isinstance(s, VisualSpec) and s.kind != "none"
            and s.resolved_asset() is None and s.builder is None]
