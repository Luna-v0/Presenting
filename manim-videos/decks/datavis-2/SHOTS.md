# Shots — Honest charts

Target: **manim**. 0 to find, 0 for us to build.

Keyed by beat id, never by position: moving a beat changes nothing here and breaks no path.

Nothing to source. Every visual in this deck is constructible on this target.

## Done — built by us

Every visual below exists and needs nothing from you. The PNGs live in the
git-ignored `assets/built/`; rebuild them from `decks/datavis-2/assets/`:

```bash
uv run --no-project --with seaborn --with matplotlib --with pandas \
    --with scipy --with scikit-learn python verified_snippets.py   # checks + all 53 figures
```

Re-running `shots.write` drops this section; nothing depends on it.

### Charts on claim-above-figure

| Beat | File | Kind |
|---|---|---|
| `opening-chart` | `assets/built/opening-chart.png` | constructible |
| `opening-split` | `assets/built/opening-split.png` | constructible |

### Before / after and misleading / honest pairs (two-up-compare)

| Beat | Files (left · right) | Kind |
|---|---|---|
| `b1-question` | `assets/built/b1-question-l.png` · `b1-question-r.png` | constructible |
| `b2-position` | `assets/built/b2-position-l.png` · `b2-position-r.png` | constructible |
| `b3-data-ink` | `assets/built/b3-data-ink-l.png` · `b3-data-ink-r.png` | constructible |
| `b4-colour` | `assets/built/b4-colour-l.png` · `b4-colour-r.png` | referential |
| `b5-annotate` | `assets/built/b5-annotate-l.png` · `b5-annotate-r.png` | constructible |
| `b6-title` | `assets/built/b6-title-l.png` · `b6-title-r.png` | constructible |
| `b7-sort` | `assets/built/b7-sort-l.png` · `b7-sort-r.png` | constructible |
| `b8-aspect` | `assets/built/b8-aspect-l.png` · `b8-aspect-r.png` | constructible |
| `c1-truncated` | `assets/built/c1-truncated-l.png` · `c1-truncated-r.png` | constructible |
| `c2-dual-axes` | `assets/built/c2-dual-axes-l.png` · `c2-dual-axes-r.png` | constructible |
| `c4-window` | `assets/built/c4-window-l.png` · `c4-window-r.png` | constructible |
| `c7-mean-median` | `assets/built/c7-mean-median-l.png` · `c7-mean-median-r.png` | constructible |
| `c9-spurious` | `assets/built/c9-spurious-l.png` · `c9-spurious-r.png` | constructible |
| `c10-survivors` | `assets/built/c10-survivors-l.png` · `c10-survivors-r.png` | constructible |
| `c11-base-rate` (backup) | `assets/built/c11-base-rate-l.png` · `c11-base-rate-r.png` | constructible |
| `c12-colour-scale` (backup) | `assets/built/c12-colour-scale-l.png` · `c12-colour-scale-r.png` | referential |
| `c13-log-scale` (backup) | `assets/built/c13-log-scale-l.png` · `c13-log-scale-r.png` | constructible |

### Charts with their code (full-bleed, `scenes.code_block:figure_with_code`)

| Beat | File | Kind |
|---|---|---|
| `b-fixes-code` | `assets/built/b-fixes-code.png` + code | constructible |
| `d-spread` | `assets/built/d-spread.png` + code | constructible |
| `d-raincloud` | `assets/built/d-raincloud.png` + code | constructible |
| `d-errorbars` | `assets/built/d-errorbars.png` + code | constructible |
| `d-countplot` | `assets/built/d-countplot.png` + code | constructible |
| `d-groupedbar` | `assets/built/d-groupedbar.png` + code | constructible |
| `d-stacked` | `assets/built/d-stacked.png` + code | constructible |
| `d-pie` | `assets/built/d-pie.png` + code | constructible |
| `d-area` | `assets/built/d-area.png` + code | constructible |
| `d-bubble` | `assets/built/d-bubble.png` + code | constructible |
| `d-pairplot` | `assets/built/d-pairplot.png` + code | constructible |
| `d-corr` | `assets/built/d-corr.png` + code | referential |
| `d-facets` | `assets/built/d-facets.png` + code | constructible |
| `d-confusion` | `assets/built/d-confusion.png` + code | referential |
| `fix-bad` | `assets/built/fix-bad.png` + code | referential |
| `fix-one-answer` | `assets/built/fix-one-answer.png` + code | constructible |
| `fix-per-mile` | `assets/built/fix-per-mile.png` + code | constructible |

### Code panels (`scenes.code_block:code`)

`toolbox-data`.

All built by `assets/verified_snippets.py`; every code panel is byte-identical to the matching
`# %% <beat-id>` cell there. `referential` marks the five figures whose colour map is the
point (jet, viridis, vlag, Greens, the rainbow bars of `fix-bad`), so the review's
off-palette check treats them as images rather than as deck colours.
