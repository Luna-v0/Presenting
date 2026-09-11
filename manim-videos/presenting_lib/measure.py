"""Fast text measurement, so fitting text to a slot is not a render loop.

Building a manim `Text` costs ~27 ms because it round-trips through Pango and
SVG. Greedy word-wrapping at three candidate sizes would be hundreds of those
per slot, which makes a fit check too expensive to run on every beat — and a
check nobody runs is the reason text ends up off-frame in the first place.

So: **search with Pillow, verify with manim.** Pillow measures glyph advances
from the same TTF in ~15 us, which is fast enough to wrap freely. Pillow's
pixel advances are converted to manim units by calibrating against one real
manim render per (family, size) — Pango hints glyph advances at small sizes, so
the ratio is not exactly linear and is not assumed to be. The mobject the slot
finally returns is measured for real; Pillow only decides where to look.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from PIL import ImageFont

PX_REF = 200  # Pillow measures at this pixel size; large enough that rounding is noise
_CALIBRATION_SAMPLE = "Handgloves preferences 0123 — the quick brown fox"


@lru_cache(maxsize=64)
def font_file(family: str, weight: str = "NORMAL", slant: str = "NORMAL") -> str:
    from matplotlib import font_manager as fm

    props = fm.FontProperties(
        family=family,
        weight="bold" if str(weight).upper() == "BOLD" else "normal",
        style="italic" if str(slant).upper() in ("ITALIC", "OBLIQUE") else "normal",
    )
    return fm.findfont(props)


@lru_cache(maxsize=64)
def _pil_font(family: str, weight: str, slant: str) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(font_file(family, weight, slant), PX_REF)


@dataclass(frozen=True)
class FontMetrics:
    """Everything needed to lay text out without rendering it."""

    family: str
    font_size: float
    units_per_px: float   # manim units per Pillow px at PX_REF
    line_advance: float   # manim units between baselines at this font_size
    single_line_height: float

    def width_of(self, text: str, weight: str = "NORMAL", slant: str = "NORMAL") -> float:
        pil = _pil_font(self.family, weight, slant)
        return pil.getlength(text) * self.units_per_px

    def block_size(self, lines: list[str], weight="NORMAL", slant="NORMAL") -> tuple[float, float]:
        if not lines:
            return 0.0, 0.0
        width = max(self.width_of(line, weight, slant) for line in lines)
        height = self.single_line_height + self.line_advance * (len(lines) - 1)
        return width, height


@lru_cache(maxsize=128)
def metrics(family: str, font_size: float, weight: str = "NORMAL",
            slant: str = "NORMAL") -> FontMetrics:
    """Calibrate Pillow against manim for one (family, size). Three real renders."""
    from manim import Text

    kwargs = dict(font=family, font_size=font_size)
    if str(weight).upper() == "BOLD":
        kwargs["weight"] = "BOLD"
    if str(slant).upper() in ("ITALIC", "OBLIQUE"):
        kwargs["slant"] = "ITALIC"

    one = Text(_CALIBRATION_SAMPLE, **kwargs)
    two = Text(_CALIBRATION_SAMPLE + "\n" + _CALIBRATION_SAMPLE, **kwargs)
    px = _pil_font(family, weight, slant).getlength(_CALIBRATION_SAMPLE)

    return FontMetrics(
        family=family,
        font_size=font_size,
        units_per_px=one.width / px,
        line_advance=two.height - one.height,
        single_line_height=one.height,
    )


_WS = re.compile(r"[ \t]+")


def wrap(text: str, m: FontMetrics, max_width: float, *, weight="NORMAL",
         slant="NORMAL") -> list[str] | None:
    """Greedy word wrap to `max_width`. None if a single word cannot fit.

    Explicit newlines in the source are honoured as hard breaks — a screenplay
    that wrote a line break meant it.
    """
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = [w for w in _WS.split(paragraph.strip()) if w]
        if not words:
            lines.append("")
            continue
        current = words[0]
        if m.width_of(current, weight, slant) > max_width:
            return None
        for word in words[1:]:
            candidate = f"{current} {word}"
            if m.width_of(candidate, weight, slant) <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
                if m.width_of(current, weight, slant) > max_width:
                    return None
        lines.append(current)
    return lines
