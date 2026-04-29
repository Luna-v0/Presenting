# Presenting

Presentation repo centered on Manim.

## Layout

- `manim-videos/`: active Manim project managed with `uv`
- `plugins/presenting-manim/`: repo-local Codex plugin with a Manim MCP server and skills
- `old/motion-canvas/`: archived Motion Canvas work kept intact for reference

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

## Fine-tuning LLMs Part 2 deck

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

Quality flags: `-ql` (480p15 drafts), `-qh` (1080p60), `-qp` (1440p60 / 2K), `-qk` (4K).
First render is the slow one; per-scene caching makes reruns cheap.

```bash
cd manim-videos
uv run manim-slides render scenes/ft_v2.py \
    FtV2_01_Recap FtV2_BTAnim FtV2_02_RecapAfter FtV2_03_Continuing \
    FtV2_04_FeedbackNoHumans FtV2_05_WhyBT FtV2_06_NLHFIntro \
    FtV2_NLHFAnim FtV2_NLHFResults FtV2_07_NoMoreBT FtV2_08_Outro -qh
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
