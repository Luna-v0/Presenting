#!/usr/bin/env python3
"""tokens.yaml -> identity/out/presenting.mplstyle.

Charts are a separate path from diagrams (plan §3.8): matplotlib with this
style, to PNG for both targets. One series in an accent, everything else muted.

Usage:  uv run python identity/export_matplotlib.py
"""

from __future__ import annotations

from _common import BANNER, IDENTITY, T, write_if_changed

# A bare #RRGGBB in an .mplstyle is stripped as a comment and the key silently
# falls back to the matplotlib default. Every colour value is quoted, and
# verify() below reloads the written file to prove it took.
def q(colour: str) -> str:
    return f'"{colour}"'


def build() -> str:
    p, ty, g = T.palette, T.type, T.geometry
    L = []
    add = L.append

    add("# " + BANNER.format(script="export_matplotlib.py"))
    add("")
    add(f"figure.facecolor:   {q(p.ground)}")
    add(f"axes.facecolor:     {q(p.ground)}")
    add(f"savefig.facecolor:  {q(p.ground)}")
    add("savefig.transparent: False")
    add("figure.dpi:         200")
    add("savefig.dpi:        200")
    add("savefig.bbox:       tight")
    add("")
    add(f"text.color:         {q(p.ink)}")
    add(f"axes.labelcolor:    {q(p.ink)}")
    add(f"axes.titlecolor:    {q(p.ink)}")
    add(f"xtick.color:        {q(p.muted)}")
    add(f"ytick.color:        {q(p.muted)}")
    add(f"xtick.labelcolor:   {q(p.muted)}")
    add(f"ytick.labelcolor:   {q(p.muted)}")
    add("")
    add(f"axes.edgecolor:     {q(p.structure_stroke)}")
    add("axes.linewidth:     1.2")
    add("axes.spines.top:    False")
    add("axes.spines.right:  False")
    add("axes.grid:          True")
    add(f"grid.color:         {q(p.structure_fill)}")
    add("grid.linewidth:     0.8")
    add("grid.alpha:         1.0")
    add("")
    add("# Muted first, deliberately. An accent is a categorical encoding with a")
    add("# fixed deck-wide meaning, so a two-series chart must not be handed both")
    add("# of them just for existing — that spends the encoding by accident, and")
    add("# it does it inside a style file where the screenplay validator cannot")
    add("# see it. presenting_lib.charts applies an accent only when a beat names")
    add("# the series it is about.")
    add("# No leading # inside the cycler: it would be stripped as a comment and")
    add("# the whole construction becomes unparseable.")
    add(f"axes.prop_cycle:    cycler('color', ['{p.muted[1:]}', "
        f"'{p.structure_stroke[1:]}', '{p.green.mid[1:]}', '{p.yellow.mid[1:]}'])")
    add("lines.linewidth:    2.4")
    add("lines.solid_capstyle: round")
    add(f"patch.edgecolor:    {q(p.structure_stroke)}")
    add("patch.force_edgecolor: True")
    add("")
    add(f"font.family:        {q(ty.family_body)}")
    add(f"font.size:          {ty.base_font_size / 2.5:.1f}")
    add(f"axes.titlesize:     {ty.base_font_size / 2.5 * ty.scale['claim']:.1f}")
    add(f"axes.labelsize:     {ty.base_font_size / 2.5:.1f}")
    add(f"xtick.labelsize:    {ty.base_font_size / 2.5 * ty.scale['caption']:.1f}")
    add(f"ytick.labelsize:    {ty.base_font_size / 2.5 * ty.scale['caption']:.1f}")
    add(f"legend.fontsize:    {ty.base_font_size / 2.5 * ty.scale['caption']:.1f}")
    add("legend.frameon:     False")
    add("")
    add(f"# stroke weight {g.stroke_weight} / corner radius {g.corner_radius} "
        "are manim-side; matplotlib has no equivalent.")
    return "\n".join(L) + "\n"


def verify(path) -> None:
    """Reload the written style and assert the colours actually took.

    Without this the exporter reports success while matplotlib quietly uses its
    own defaults — the same class of failure as a silently overridden colour
    rendering light-on-light.
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import to_hex

    p = T.palette
    with plt.rc_context():
        plt.style.use(str(path))
        expected = {
            "figure.facecolor": p.ground,
            "axes.facecolor": p.ground,
            "text.color": p.ink,
            "axes.edgecolor": p.structure_stroke,
            "grid.color": p.structure_fill,
            "xtick.color": p.muted,
        }
        bad = {
            key: (plt.rcParams[key], want)
            for key, want in expected.items()
            if to_hex(plt.rcParams[key]).lower() != want.lower()
        }
        if bad:
            raise SystemExit(f"{path.name}: values did not survive the round trip: {bad}")
        cycle = [c.lower() for c in plt.rcParams["axes.prop_cycle"].by_key()["color"]]
        if cycle[0] != p.muted.lower() or cycle[1] != p.structure_stroke.lower():
            raise SystemExit(f"{path.name}: prop_cycle should start muted: {cycle}")
    print(f"verified   {path.name}: palette round-trips through matplotlib")


if __name__ == "__main__":
    out = IDENTITY / "out" / "presenting.mplstyle"
    write_if_changed(out, build())
    verify(out)
