#!/usr/bin/env python3
"""tokens.yaml -> identity/out/revealjs.html (the HTML export template).

    uv run python identity/export_revealjs.py

manim-slides ships a reveal.js template that uses the `black` theme, whose page
background is #191919. Every slide is a video sitting on that page, and during a
`fade` transition both the outgoing and incoming slide backgrounds are partly
transparent — so for a few frames the dark page shows through and the deck
flashes on *every* slide change.

It looks like a rendering bug and is not: the videos are continuous, the frames
are all correct, and it happens identically on hand-written scenes the compiler
never touches. It is the page behind them.

This takes the stock template from the installed manim-slides and injects the
ground colour behind everything, so a gap during a transition is the same sand
as the slides and nothing shows through. Read from the installed package rather
than vendored, so it tracks whatever version is in the venv.
"""

from __future__ import annotations

import re
from pathlib import Path

from _common import BANNER, IDENTITY, REPO, T, write_if_changed


def stock_template() -> Path:
    import manim_slides

    path = Path(manim_slides.__file__).parent / "templates" / "revealjs.html"
    if not path.exists():
        raise SystemExit(f"manim-slides template not found at {path}")
    return path


def build() -> str:
    source = stock_template().read_text()
    ground = T.palette.ground

    injected = f"""
    <!-- {BANNER.format(script='export_revealjs.py')} -->
    <style>
      /* The page behind the slides. reveal.js fades slide backgrounds in and
         out, so whatever sits behind them is visible mid-transition — with the
         stock black theme that is #191919, and the deck flashes dark on every
         slide change. Painting it the deck's own ground makes the gap
         invisible. */
      /* Override the theme's own variable first — every reveal.js rule that
         paints a background reads it, so this catches the ones not listed
         below as well. */
      :root,
      .reveal-viewport {{
        /* !important, because the theme declares these later in the document
           and custom properties resolve by order, not by where we injected. */
        --r-background-color: {ground} !important;
        --r-background: {ground} !important;
      }}
      html,
      body,
      .reveal-viewport,
      .reveal,
      .reveal .backgrounds,
      .reveal .slide-background {{
        background-color: {ground} !important;
      }}
    </style>
  </head>"""

    if "</head>" not in source:
        raise SystemExit("template has no </head>; manim-slides layout changed")
    return source.replace("</head>", injected.lstrip("\n"), 1)


def verify(path: Path) -> None:
    text = path.read_text()
    ground = T.palette.ground
    if text.count(ground) < 1:
        raise SystemExit(f"{path.name}: ground colour did not make it into the template")
    if f"--r-background-color: {ground} !important" not in text:
        raise SystemExit(f"{path.name}: the theme variable override is missing")
    for token in ("{{ transition }}", "{{ background_transition }}", "data-background-video"):
        if token not in text:
            raise SystemExit(f"{path.name}: lost {token!r} — the injection broke the template")
    print(f"verified   {path.name}: ground {ground} painted behind the slides")


if __name__ == "__main__":
    out = IDENTITY / "out" / "revealjs.html"
    write_if_changed(out, build())
    verify(out)
