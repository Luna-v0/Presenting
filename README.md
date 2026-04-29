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

The repo-local plugin lives in `plugins/presenting-manim` and is registered in `.agents/plugins/marketplace.json`.
Its MCP server renders against `manim-videos`, and its skills are intended for scene creation, iteration, and low-friction preview renders.
