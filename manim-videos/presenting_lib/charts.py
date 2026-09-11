"""Charts: matplotlib with the exported style, to PNG for both targets.

A separate path from diagrams on purpose. A diagram is drawn with library
primitives so it inherits the palette natively; a chart has axes, ticks and a
legend that matplotlib is simply better at, so it renders to an image and the
image goes in the visual slot. When a chart has to *animate*, build it as
mobjects instead — that is a `raw` beat, not this module.

A chart earns its place if the beat spends time on it. One series or bar in an
accent, everything else muted, so there is one thing to look at while it is
being walked through.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence

from manim import Group, ImageMobject

from .slots import Slot
from .tokens import PALETTE

STYLE_PATH = Path(__file__).resolve().parent.parent / "identity" / "out" / "presenting.mplstyle"
DEFAULT_CACHE = Path(__file__).resolve().parent.parent / "media" / "charts"

# Manim units per inch when a chart is rendered for a slot. 8 frame units tall
# maps to a 1080p frame, so ~1.6 units/inch keeps text in the chart close to
# the deck's own caption size without hand-tuning per chart.
UNITS_PER_INCH = 1.6


@dataclass
class ChartSpec:
    """What to plot, and which one series the beat is about."""

    kind: str = "line"                    # line | bar | scatter | custom
    x: Sequence = field(default_factory=list)
    series: dict[str, Sequence] = field(default_factory=dict)
    accent: str | None = None             # series name drawn in green
    accent_b: str | None = None           # second series, drawn in yellow
    xlabel: str = ""
    ylabel: str = ""
    title: str = ""
    source: str = ""                      # shown on the placeholder if unrendered
    draw: Callable | None = None          # custom: draw(ax) -> None

    def cache_key(self, width_in: float, height_in: float) -> str:
        payload = repr((self.kind, list(self.x), {k: list(v) for k, v in self.series.items()},
                        self.accent, self.accent_b, self.xlabel, self.ylabel,
                        self.title, round(width_in, 3), round(height_in, 3),
                        getattr(self.draw, "__qualname__", None)))
        return hashlib.sha1(payload.encode()).hexdigest()[:16]


#: Unaccented series all share `muted`, so they have to be told apart by line
#: style instead. Colour is spoken for; dash patterns are not.
_DASHES = ((), (5, 2), (1, 1.6), (7, 2, 1.5, 2))


def _colour_for(spec: ChartSpec, name: str) -> str:
    if name == spec.accent:
        return PALETTE.green.mid
    if name == spec.accent_b:
        return PALETTE.yellow.mid
    return PALETTE.muted


def _dash_for(spec: ChartSpec, name: str, index: int) -> tuple:
    if name in (spec.accent, spec.accent_b):
        return ()
    quiet = [n for n in spec.series if n not in (spec.accent, spec.accent_b)]
    return _DASHES[quiet.index(name) % len(_DASHES)] if name in quiet else ()


def render_png(spec: ChartSpec, *, width_in: float, height_in: float,
               out_dir: Path | None = None) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir = out_dir or DEFAULT_CACHE
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"chart-{spec.cache_key(width_in, height_in)}.png"
    if path.exists():
        return path

    with plt.rc_context():
        if STYLE_PATH.exists():
            plt.style.use(str(STYLE_PATH))
        fig, ax = plt.subplots(figsize=(width_in, height_in))

        if spec.draw is not None:
            spec.draw(ax)
        elif spec.kind == "bar":
            names = list(spec.series)
            for i, name in enumerate(names):
                ax.bar([f"{v}" for v in spec.x], spec.series[name],
                       color=_colour_for(spec, name), label=name,
                       zorder=3 if name in (spec.accent, spec.accent_b) else 2)
        elif spec.kind == "scatter":
            for name, values in spec.series.items():
                ax.scatter(spec.x, values, color=_colour_for(spec, name), label=name,
                           zorder=3 if name in (spec.accent, spec.accent_b) else 2)
        else:
            for index, (name, values) in enumerate(spec.series.items()):
                accented = name in (spec.accent, spec.accent_b)
                line, = ax.plot(spec.x, values, color=_colour_for(spec, name),
                                label=name, linewidth=2.6 if accented else 1.6,
                                zorder=3 if accented else 2)
                dashes = _dash_for(spec, name, index)
                if dashes:
                    line.set_dashes(dashes)

        if spec.xlabel:
            ax.set_xlabel(spec.xlabel)
        if spec.ylabel:
            ax.set_ylabel(spec.ylabel)
        if spec.title:
            ax.set_title(spec.title)
        if len(spec.series) > 1:
            ax.legend()
        fig.savefig(path)
        plt.close(fig)
    return path


def visual(spec: ChartSpec, *, out_dir: Path | None = None):
    """A `visual` callable for a beat: `visual=charts.visual(spec)`."""

    def make(slot: Slot):
        image = ImageMobject(str(render_png(
            spec,
            width_in=slot.w / UNITS_PER_INCH,
            height_in=slot.h / UNITS_PER_INCH,
            out_dir=out_dir,
        )))
        scale = min(slot.w / image.width, slot.h / image.height)
        image.scale(scale)
        return Group(image)

    return make
