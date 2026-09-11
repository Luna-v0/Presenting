#!/usr/bin/env python3
"""tokens.yaml -> identity/out/presenting.sty (beamer colour + font theme).

Usage:  uv run python identity/export_beamer.py
"""

from __future__ import annotations

from _common import BANNER, IDENTITY, T, hex_body, write_if_changed


def build() -> str:
    p, ty, g = T.palette, T.type, T.geometry
    L = []
    add = L.append

    add("% " + BANNER.format(script="export_beamer.py"))
    add("\\ProvidesPackage{presenting}[Presenting identity]")
    add("\\RequirePackage{xcolor}")
    add("")
    add("% ── palette ────────────────────────────────────────────────────────")
    for name, value in [
        ("PresentingGround", p.ground),
        ("PresentingInk", p.ink),
        ("PresentingMuted", p.muted),
        ("PresentingStructureFill", p.structure_fill),
        ("PresentingStructureStroke", p.structure_stroke),
    ]:
        add(f"\\definecolor{{{name}}}{{HTML}}{{{hex_body(value)}}}")
    for ramp in (p.green, p.yellow):
        title = ramp.name.capitalize()
        add(f"\\definecolor{{Presenting{title}Tint}}{{HTML}}{{{hex_body(ramp.tint)}}}")
        add(f"\\definecolor{{Presenting{title}Mid}}{{HTML}}{{{hex_body(ramp.mid)}}}")
        add(f"\\definecolor{{Presenting{title}Dark}}{{HTML}}{{{hex_body(ramp.dark)}}}")
    add("")
    add("% Accent fills carry their own Dark. Ground and structure carry Ink.")
    add("% Never light text on a dark fill.")
    add("\\newcommand{\\greenmark}[1]{\\colorbox{PresentingGreenTint}"
        "{\\textcolor{PresentingGreenDark}{#1}}}")
    add("\\newcommand{\\yellowmark}[1]{\\colorbox{PresentingYellowTint}"
        "{\\textcolor{PresentingYellowDark}{#1}}}")
    add("")
    add("% ── beamer assignments ─────────────────────────────────────────────")
    add("\\setbeamercolor{background canvas}{bg=PresentingGround}")
    add("\\setbeamercolor{normal text}{fg=PresentingInk}")
    add("\\setbeamercolor{frametitle}{fg=PresentingInk,bg=}")
    add("\\setbeamercolor{title}{fg=PresentingInk,bg=}")
    add("\\setbeamercolor{structure}{fg=PresentingGreenMid}")
    add("\\setbeamercolor{block title}{fg=PresentingInk,bg=PresentingStructureFill}")
    add("\\setbeamercolor{block body}{fg=PresentingInk,bg=PresentingGround}")
    add("\\setbeamercolor{block title example}{fg=PresentingGreenDark,bg=PresentingGreenTint}")
    add("\\setbeamercolor{block body example}{fg=PresentingInk,bg=PresentingGround}")
    add("\\setbeamercolor{block title alerted}{fg=PresentingYellowDark,bg=PresentingYellowTint}")
    add("\\setbeamercolor{block body alerted}{fg=PresentingInk,bg=PresentingGround}")
    add("\\setbeamercolor{footline}{fg=PresentingMuted}")
    add("\\setbeamercolor{page number in head/foot}{fg=PresentingMuted}")
    add("\\setbeamercolor{itemize item}{fg=PresentingGreenMid}")
    add("\\setbeamercolor{itemize subitem}{fg=PresentingGreenMid}")
    add("\\setbeamertemplate{navigation symbols}{}")
    add("\\setbeamertemplate{frametitle}[default][center]  % title is centered")
    add("")
    add("% ── type ───────────────────────────────────────────────────────────")
    add(f"% requested display/body: {ty.requested['family_display'][0]}")
    subs = ty.substitutions()
    if subs:
        add("% NOT INSTALLED on the machine that generated this file; manim "
            "renders with the substitute:")
        for role, (asked, got) in subs.items():
            add(f"%   {role}: {asked} -> {got}")
    add("\\usepackage{iftex}")
    add("\\ifPDFTeX")
    add("  \\usepackage[T1]{fontenc}")
    add("  \\usepackage{tgtermes}")
    add("\\else")
    add("  \\usepackage{fontspec}")
    add(f"  \\setmainfont{{{ty.requested['family_body'][0]}}}")
    add(f"  \\setsansfont{{{ty.requested['family_display'][0]}}}")
    add(f"  \\setmonofont{{{ty.requested['family_mono'][0]}}}")
    add("\\fi")
    add("")
    add("% Type scale — multipliers on the body step, matching the manim library.")
    for style, mult in sorted(ty.scale.items(), key=lambda kv: -kv[1]):
        add(f"%   {style:<8} {mult}x")
    add(f"% min legible body: {ty.min_legible_body} (manim font_size units @1080p)")
    add("")
    add("% ── geometry ───────────────────────────────────────────────────────")
    add(f"% safe inset {g.safe_inset}, gutter {g.gutter}, stroke {g.stroke_weight}, "
        f"corner radius {g.corner_radius} (manim units, 14.222 x 8.0 frame)")
    add("\\endinput")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    write_if_changed(IDENTITY / "out" / "presenting.sty", build())
