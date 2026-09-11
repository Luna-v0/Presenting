# catalog-demo — the working sample

One beat per layout, rendered. This deck exists so every entry in the catalog
gets exercised by a real compile rather than only by a unit test, and so the
catalog can be looked at instead of read.

```bash
cd manim-videos
uv run python -c "
from presenting_lib.compile import compile_deck
print(compile_deck('decks/catalog-demo/screenplay.md',
                   'decks/catalog-demo/out/catalog_demo_scenes.py')[0])"
```

The generated module's header carries the render / present / convert commands.
`out/catalog-demo.html` is the export — one file, opens in any browser.

## What it covers that ft-v2 does not

Every layout ft-v2 never reached: `full-bleed-figure`, `figure-with-callouts`,
`two-up-compare`, `term-reveal`, `table-accented`, `discussion`,
`activity-setup`, `activity-parking`, `backup`. Plus three compiler paths ft-v2
does not exercise:

- **`scene_type: 3d`** — `the-3d-split` forces its own `DeckScene3D` class.
- **`transition: build`** — `the-build-transition` keeps the previous beat on
  screen instead of clearing it.
- **`raw` with inline code** — ft-v2's raw beats reference existing scenes;
  `the-raw-beat` carries its scene class in the screenplay itself.
- **A chart inside a deck**, and **two deliberate placeholders**, so the
  missing-asset path is visible rather than asserted.

## Bugs it found

1. A blank line inside a `|` block scalar produced a `Text` with no points, and
   every alignment call on it failed deep inside manim.
2. `table-accented` was slicing off the header row — the one part of a table
   nobody can infer.
3. A `content:` entry describing a visual (a `two-up-compare` panel) reached the
   layout as a raw dict and the placer choked on it.
4. Leader lines in `figure-with-callouts` were tagged with a callout's slot, so
   review reported a false overflow on every one of them. A leader spans from
   the callout into the figure and belongs to neither.
5. The `.mplstyle` prop_cycle handed **both accents** to any two-series chart
   just for existing — spending a categorical encoding by accident, inside a
   style file where the screenplay validator cannot see it. The cycle now starts
   muted, and unaccented series are told apart by dash pattern instead.

## Two beats render deliberately unmarked

`the-table` and `the-term` both want an accent and neither gets one, because
`accents.green.meaning` and `accents.yellow.meaning` are unassigned in
`identity/tokens.yaml`. The validator refuses them, and the slides say so. That
is the block working, not a rendering fault — see PIPELINE.md, open decision 1.
