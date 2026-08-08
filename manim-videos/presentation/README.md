# Presentation — prebuilt exports

Two prebuilt exports of the deck (scenes `PyIntro_01_Timeline`, `PyIntro_02_Manim`,
`PyIntro_03_Philosophy`, `PyIntro_04_Performance`, `PyIntro_05_CommandLine`,
`PyIntro_06_Venv`, `PyIntro_07_Jupyter`):

- **`python_intro.html`** — a self-contained reveal.js presentation with every
  video embedded (animated).
- **`python_intro.pdf`** — one page per slide (each slide's final frame; static).

This folder is **committed** (unlike `slides/` and `media/`, which are gitignored),
so on another machine you just `git pull` and open a file — no `uv`, manim, or
LaTeX needed to present.

## Present
Open `python_intro.html` in any browser (double-click, or `xdg-open python_intro.html`).

Navigation: **→ / Space** next · **←** previous · **F** fullscreen · **Esc** overview.

The browser fits the 16:9 video to the window (`background-size: contain`), so the
aspect ratio stays correct — clean letterbox bars instead of a stretched image.
Fullscreen on a 16:9 monitor fills the screen edge-to-edge.

## Rebuild (after editing scenes/python_intro.py)
```bash
cd manim-videos
SCENES="PyIntro_01_Timeline PyIntro_02_Manim PyIntro_03_Philosophy PyIntro_04_Performance \
PyIntro_05_CommandLine PyIntro_06_Venv PyIntro_07_Jupyter"
uv run manim-slides render scenes/python_intro.py $SCENES -q h --disable_caching
uv run manim-slides convert $SCENES presentation/python_intro.html -cdata_uri=true -ccontrols=true
# PDF (one page per slide)
uv run manim-slides convert --to pdf $SCENES presentation/python_intro.pdf
```
