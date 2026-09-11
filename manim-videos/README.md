# Manim Videos

Active Manim workspace for this repository. Two things live here:

- **The Presenting pipeline** — brief → screenplay → shot list → render →
  review → revise. See [PIPELINE.md](PIPELINE.md).
- **Hand-written scenes** in `scenes/`, unchanged and still rendering.

## Setup

```bash
uv sync
```

## Smoke tests

```bash
uv run manim scenes/title_card.py TitleCard -ql
uv run pytest tests/ -q
```

## The pipeline in one command each

```bash
# validate a screenplay
uv run python -c "
from presenting_lib import screenplay as sp, compile as C
d = sp.load('decks/<slug>/screenplay.md'); [print(f) for f in C.validate(d)]"

# compile it to manim-slides scenes (the header carries the render commands)
uv run python -c "
from presenting_lib.compile import compile_deck
print(compile_deck('decks/<slug>/screenplay.md', 'decks/<slug>/out/<slug>_scenes.py')[0])"

# review a rendered deck
uv run python scripts/extract_frames.py <Scene> ... --out media/review
uv run python scripts/review_deck.py decks/<slug>/screenplay.md --frames media/review
```

`decks/ft-v2/` is the migration reference — the Fine-tuning Part 2 talk ported
from `screenplays/ft_v2.md` and compiled through the library. See
[decks/ft-v2/README.md](decks/ft-v2/README.md).

## Identity

`identity/tokens.yaml` is the single source of colour, type and geometry.
Change it, then re-run all four exporters:

```bash
for s in beamer drawio matplotlib revealjs; do uv run python identity/export_$s.py; done
```

Re-measure the character budgets after any change to the type scale or the
layout catalog:

```bash
uv run python scripts/measure_slots.py
uv run python scripts/measure_slots.py --calibrate   # the legibility ladder
```

## Notes

- Put new hand-written scenes under `scenes/`. Pipeline decks go in `decks/`.
- Positioning belongs in `presenting_lib/layouts/`, never in a generated scene
  file — those are overwritten on every compile.
- `main.py` and `rule_to_python.py` are older experiments and may need cleanup
  before they render on the current Manim version.
