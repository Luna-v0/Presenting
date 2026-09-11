# Presenting

Presentation repo centered on Manim.

## Layout

- `manim-videos/`: active Manim project managed with `uv`
  - `presenting_lib/`, `identity/`, `decks/`: the presentation pipeline — see
    [manim-videos/PIPELINE.md](manim-videos/PIPELINE.md)
  - `scenes/`: hand-written scenes, unchanged
- `plugins/presenting-manim/`: repo-local Codex plugin with a Manim MCP server and skills
- `old/motion-canvas/`: archived Motion Canvas work kept intact for reference

## The pipeline

```
whiteboard photo ──┐
                   ├──> brief ──> screenplay ──> shot list ──> render ──┬── manim  (manim-slides + library)
topic (interview) ─┘      ▲            ▲                                └── slides (pptx → Drive)
                          │            │                                        │
                          └── deck-review ◀────────────────────────────────────┘
```

Six skills drive it, all in `plugins/presenting-manim/skills/`:
`presentation-brief`, `screenplay`, `shot-list`, `render-manim`,
`render-slides`, `deck-review`. The library, identity tokens and layout catalog
they share live in `manim-videos/`. `decks/ft-v2/` is the reference deck.

## Setup

```bash
cd manim-videos
uv sync

cd ../plugins/presenting-manim
uv sync
```

## Quick Start

Render the known-good sample scene:

```bash
cd manim-videos
uv run manim scenes/title_card.py TitleCard -ql
```

Render the manim-beamer slideshow demo (gradient descent), then present or export HTML.
The deck is split across three scenes (`BeamerDemoPart1`, `BowlDescent3D`, `BeamerDemoPart2`)
so the 3D paraboloid scene can use a `ThreeDScene` while the rest stay on
manim-beamer's `MovingCameraScene`-based runner. `manim-slides` plays them as one show.

```bash
cd manim-videos
uv run manim-slides render scenes/beamer_demo.py BeamerDemoPart1 BowlDescent3D BeamerDemoPart2 -ql
uv run manim-slides present BeamerDemoPart1 BowlDescent3D BeamerDemoPart2
uv run manim-slides convert BeamerDemoPart1 BowlDescent3D BeamerDemoPart2 beamer_demo.html
```

## Course decks (Python / NumPy / pandas)

Three `manim-slides` decks used in class, each one scene file plus a prebuilt
export in `manim-videos/presentation/` (HTML for presenting, PDF for handing out):

| Deck | Source | Scenes |
| --- | --- | --- |
| Python intro | `manim-videos/scenes/python_intro.py` | `PyIntro_01_Timeline` … `PyIntro_10_DataStructures` |
| NumPy refresh | `manim-videos/scenes/numpy_intro.py` | `NpIntro_01_Array` `NpIntro_02_Dtype` `NpIntro_03_Aleatorio` `NpIntro_04_Algebra` `NpIntro_05_Recap` |
| pandas refresh | `manim-videos/scenes/pandas_intro.py` | `PdIntro_01_Tabela` `PdIntro_02_Merge` `PdIntro_03_Melt` `PdIntro_04_Recap` |

Each scene file's module docstring carries its own render/present commands, and
`manim-videos/presentation/README.md` has the full rebuild recipe per deck.
Re-renders need `--disable_caching`:

```bash
cd manim-videos
uv run manim-slides render scenes/pandas_intro.py \
    PdIntro_01_Tabela PdIntro_02_Merge PdIntro_03_Melt PdIntro_04_Recap \
    -q h --disable_caching
uv run manim-slides present PdIntro_01_Tabela PdIntro_02_Merge PdIntro_03_Melt PdIntro_04_Recap
```

To present without any tooling, open `manim-videos/presentation/<deck>.html` in a browser.

## Fine-tuning LLMs Part 2 deck

**There are two versions of this deck.** `manim-videos/decks/ft-v2/` is the same
talk in the v3 screenplay format, compiled through `presenting_lib` — that is
the one to edit, and the migration reference for the pipeline (see
[its README](manim-videos/decks/ft-v2/README.md)). The hand-written original
below still renders and is kept as the visual reference the port was compared
against.

The screenplay is `manim-videos/screenplays/ft_v2.md`; the manim-slides
implementation is `manim-videos/scenes/ft_v2.py`. The deck splices in two
animation scenes (`BradleyTerryToElo` from `bradley_terry_elo.py` and `NLHF`
from `nlhf.py`) as standalone slides between manim-beamer scenes — both
inherit from `manim-slides`' `Slide`, so internal `next_slide()` calls
become click-through pause points.

Drop any referenced images into `manim-videos/scenes/assets/` (e.g.
`rl_robot.png`, `rlhf_loop.png`, `results_nlhf.png`). Until a file exists, a
labelled placeholder takes its place — nothing else breaks.

### Render

Quality flags: `-ql` (480p15), `-qh` (1080p60), `-qp` (1440p60 / 2K), `-qk` (4K).
**Decks ship at `-qp`.** A talk gets shown on a projector or a large display,
where anything lower is visibly soft; `-ql` is for a fast structural check while
a screenplay is still moving, never for something you hand over. First render is
the slow one; per-scene caching makes reruns cheap.

```bash
cd manim-videos
uv run manim-slides render scenes/ft_v2.py \
    FtV2_01_Recap FtV2_BTAnim FtV2_02_RecapAfter FtV2_03_Continuing \
    FtV2_04_FeedbackNoHumans FtV2_05_WhyBT FtV2_06_NLHFIntro \
    FtV2_NLHFAnim FtV2_NLHFResults FtV2_07_NoMoreBT FtV2_08_Outro -qp
```

### Present (live, PySide6 window)

```bash
uv run manim-slides present \
    FtV2_01_Recap FtV2_BTAnim FtV2_02_RecapAfter FtV2_03_Continuing \
    FtV2_04_FeedbackNoHumans FtV2_05_WhyBT FtV2_06_NLHFIntro \
    FtV2_NLHFAnim FtV2_NLHFResults FtV2_07_NoMoreBT FtV2_08_Outro
```

Controls: `→` / `Space` next, `←` previous, `R` replay current animation,
`F` fullscreen, `Esc` quits.

### Export to a self-contained HTML deck

```bash
uv run manim-slides convert \
    FtV2_01_Recap FtV2_BTAnim FtV2_02_RecapAfter FtV2_03_Continuing \
    FtV2_04_FeedbackNoHumans FtV2_05_WhyBT FtV2_06_NLHFIntro \
    FtV2_NLHFAnim FtV2_NLHFResults FtV2_07_NoMoreBT FtV2_08_Outro \
    ft_v2.html
```

Open `ft_v2.html` in any browser — same keybindings, no Python on the host.

The repo-local plugin lives in `plugins/presenting-manim` and is registered in `.agents/plugins/marketplace.json`.
Its MCP server renders against `manim-videos`, and its skills are intended for scene creation, iteration, and low-friction preview renders.
