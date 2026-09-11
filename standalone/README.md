# Standalone skills

Skills that run **without this repository** — no venv, no manim, no
`presenting_lib`. Zip one of these directories and upload it wherever skills are
supported.

## `presenting-slides`

The whole slides path in one skill: work out the story, write the beats, build a
`.pptx`. Its only dependency is `python-pptx`.

It exists because the slides target genuinely does not need the repo, while the
manim target genuinely does — manim, LaTeX, ffmpeg, graphviz, the layout
library, and hours of rendering. Splitting on *target* rather than on *tool* is
what makes a pptx buildable from a bare Python environment.

The plugin's `render-slides` skill covers the same build stage and is also
repo-free, so either works in Claude Code. This one additionally folds in the
brief and screenplay stages, because outside the repo there are no separate
skills for them.

Both share `references/pptx-recipes.md`. If you change one, change the other —
or better, delete the one you stop using. The colour values in both are copies
of `manim-videos/identity/tokens.yaml`, which stays canonical for anything the
manim target also renders.

```bash
cd standalone/presenting-slides && zip -qr ../presenting-slides.zip .
```
