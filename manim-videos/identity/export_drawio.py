#!/usr/bin/env python3
"""tokens.yaml -> draw.io Edit Style strings + a shape library.

draw.io is the manual escape hatch for spatial or hand-composed figures (plan
§0 non-goals) — it stays. This makes hand-drawn figures land in the same
palette as generated ones: paste a style string into Edit Style (Ctrl+E), or
import the .xml library once via Extras > Edit Diagram / File > Open Library.

Usage:  uv run python identity/export_drawio.py
"""

from __future__ import annotations

from xml.sax.saxutils import escape

from _common import BANNER, IDENTITY, T, write_if_changed

ROUNDED = "rounded=1;arcSize=12;"


def _style(fill: str | None, stroke: str, font: str, *, rounded=True, dashed=False) -> str:
    bits = [ROUNDED if rounded else "rounded=0;", "whiteSpace=wrap;", "html=1;"]
    bits.append(f"fillColor={fill};" if fill else "fillColor=none;")
    bits.append(f"strokeColor={stroke};")
    bits.append("strokeWidth=2;")
    bits.append(f"fontColor={font};")
    bits.append(f"fontFamily={T.type.family_body};")
    bits.append("fontSize=16;")
    if dashed:
        bits.append("dashed=1;")
    return "".join(bits)


def styles() -> dict[str, str]:
    p = T.palette
    edge_base = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeWidth=2;"
                 f"fontFamily={T.type.family_body};fontSize=14;")
    return {
        "node/structure": _style(p.structure_fill, p.structure_stroke, p.ink),
        "node/green": _style(p.green.tint, p.green.mid, p.green.dark),
        "node/yellow": _style(p.yellow.tint, p.yellow.mid, p.yellow.dark),
        "node/ghost": _style(None, p.structure_stroke, p.ink, dashed=True),
        "label": (f"text;html=1;align=center;fontColor={p.ink};"
                  f"fontFamily={T.type.family_body};fontSize=16;"),
        "caption": (f"text;html=1;align=center;fontColor={p.muted};"
                    f"fontFamily={T.type.family_body};fontSize=13;"),
        "edge/plain": edge_base + f"strokeColor={p.structure_stroke};fontColor={p.muted};",
        "edge/green": edge_base + f"strokeColor={p.green.mid};fontColor={p.green.dark};",
        "edge/yellow": edge_base + f"strokeColor={p.yellow.mid};fontColor={p.yellow.dark};",
    }


def build_reference() -> str:
    p = T.palette
    L = ["# " + BANNER.format(script="export_drawio.py"), ""]
    L += [
        "Select a shape in draw.io, press Ctrl+E (Edit Style), paste one line.",
        "",
        "Pairing rule: an accent fill carries its own dark text. Structure and",
        "ground carry ink. There is no light-on-dark shape in this identity —",
        "if you find yourself typing a light fontColor onto a dark fill, stop.",
        "",
        "## Canvas",
        "",
        f"File > Page Setup > Background: {p.ground}",
        "",
        "## Styles",
        "",
    ]
    for name, style in styles().items():
        L += [f"### {name}", "", "```", style, "```", ""]
    L += [
        "## Palette, for the colour picker",
        "",
        f"| ground | {p.ground} |",
        f"| ink | {p.ink} |",
        f"| muted | {p.muted} |",
        f"| structure fill | {p.structure_fill} |",
        f"| structure stroke | {p.structure_stroke} |",
        f"| green tint / mid / dark | {p.green.tint} / {p.green.mid} / {p.green.dark} |",
        f"| yellow tint / mid / dark | {p.yellow.tint} / {p.yellow.mid} / {p.yellow.dark} |",
        "",
    ]
    return "\n".join(L)


def build_library() -> str:
    """A draw.io shape library — File > Open Library, then drag from the panel."""
    entries = []
    swatches = [
        ("Structure", "node/structure", 160, 60),
        ("Green", "node/green", 160, 60),
        ("Yellow", "node/yellow", 160, 60),
        ("Ghost", "node/ghost", 160, 60),
    ]
    st = styles()
    for title, key, w, h in swatches:
        cell = (
            '<mxGraphModel><root>'
            '<mxCell id="0"/><mxCell id="1" parent="0"/>'
            f'<mxCell id="2" value="{title}" style="{st[key]}" vertex="1" parent="1">'
            f'<mxGeometry x="0" y="0" width="{w}" height="{h}" as="geometry"/>'
            '</mxCell></root></mxGraphModel>'
        )
        entries.append(
            f'{{"xml":"{escape(cell, {chr(34): "&quot;"})}",'
            f'"w":{w},"h":{h},"aspect":"fixed","title":"{title}"}}'
        )
    return "<mxlibrary>[" + ",".join(entries) + "]</mxlibrary>\n"


if __name__ == "__main__":
    write_if_changed(IDENTITY / "out" / "drawio-styles.md", build_reference())
    write_if_changed(IDENTITY / "out" / "presenting.drawiolib.xml", build_library())
