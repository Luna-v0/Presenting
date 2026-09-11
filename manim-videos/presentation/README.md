# Presentation — prebuilt exports

Prebuilt exports of the course decks. Each deck ships in two formats:

- **`<deck>.html`** — a self-contained reveal.js presentation with every video
  embedded (animated).
- **`<deck>.pdf`** — one page per slide (each slide's final frame; static).

| Deck | Source | Scenes |
| --- | --- | --- |
| `python_intro` | `scenes/python_intro.py` | `PyIntro_01_Timeline` `PyIntro_02_Manim` `PyIntro_03_Philosophy` `PyIntro_04_Performance` `PyIntro_05_Basics` `PyIntro_06_CommandLine` `PyIntro_07_Venv` `PyIntro_08_Jupyter` `PyIntro_09_Pause` `PyIntro_10_DataStructures` |
| `numpy_intro` | `scenes/numpy_intro.py` | `NpIntro_01_Array` `NpIntro_02_Dtype` `NpIntro_03_Aleatorio` `NpIntro_04_Algebra` `NpIntro_05_Recap` |
| `pandas_intro` | `scenes/pandas_intro.py` | `PdIntro_01_Tabela` `PdIntro_02_Merge` `PdIntro_03_Melt` `PdIntro_04_Recap` |

This folder is **committed** (unlike `slides/` and `media/`, which are gitignored),
so on another machine you just `git pull` and open a file — no `uv`, manim, or
LaTeX needed to present.

## Present
Open the `.html` in any browser (double-click, or `xdg-open pandas_intro.html`).

Navigation: **→ / Space** next · **←** previous · **F** fullscreen · **Esc** overview.

The browser fits the 16:9 video to the window (`background-size: contain`), so the
aspect ratio stays correct — clean letterbox bars instead of a stretched image.
Fullscreen on a 16:9 monitor fills the screen edge-to-edge.

## Rebuild
Run from `manim-videos/`. Re-renders need `--disable_caching`.

```bash
SCENES="PyIntro_01_Timeline PyIntro_02_Manim PyIntro_03_Philosophy PyIntro_04_Performance \
PyIntro_05_Basics PyIntro_06_CommandLine PyIntro_07_Venv PyIntro_08_Jupyter \
PyIntro_09_Pause PyIntro_10_DataStructures"
uv run manim-slides render scenes/python_intro.py $SCENES -q h --disable_caching
uv run manim-slides convert $SCENES presentation/python_intro.html -cdata_uri=true -ccontrols=true
uv run manim-slides convert --to pdf $SCENES presentation/python_intro.pdf
```

```bash
SCENES="NpIntro_01_Array NpIntro_02_Dtype NpIntro_03_Aleatorio NpIntro_04_Algebra NpIntro_05_Recap"
uv run manim-slides render scenes/numpy_intro.py $SCENES -q h --disable_caching
uv run manim-slides convert $SCENES presentation/numpy_intro.html -cdata_uri=true -ccontrols=true
uv run manim-slides convert --to pdf $SCENES presentation/numpy_intro.pdf
```

```bash
SCENES="PdIntro_01_Tabela PdIntro_02_Merge PdIntro_03_Melt PdIntro_04_Recap"
uv run manim-slides render scenes/pandas_intro.py $SCENES -q h --disable_caching
uv run manim-slides convert $SCENES presentation/pandas_intro.html -cdata_uri=true -ccontrols=true
uv run manim-slides convert --to pdf $SCENES presentation/pandas_intro.pdf
```
