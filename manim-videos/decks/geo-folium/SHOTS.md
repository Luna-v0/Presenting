# Shots — Points on a map

Target: **manim**. 0 to find, 0 for us to build.

Keyed by beat id, never by position: moving a beat changes nothing here and breaks no path.

Nothing to source. Every visual in this deck is constructible on this target.

## Done — built by us

Every visual below exists and needs nothing from you. The PNGs live in the
git-ignored `assets/built/`; rebuild them from `decks/geo-folium/assets/`:

```bash
uv run --no-project --with geopandas --with shapely --with folium \
    --with mapclassify --with matplotlib python verified_snippets.py   # figures + map.html
uv run --no-project --with geopandas --with shapely --with folium \
    --with mapclassify --with matplotlib python screenshot_maps.py     # the 4 folium shots (needs network)
```

### Map figures (matplotlib on the deck identity, from the verified code)

| Beat | File | Built by |
|---|---|---|
| `opening-question` | `assets/built/schools_on_bairros.png` | `assets/verified_snippets.py` → `deck_figures()` |
| `geo-plot` | `assets/built/schools_on_bairros.png` + code | `assets/verified_snippets.py` → `deck_figures()`; drawn by `scenes.code_block:figure_with_code` |
| `sjoin-picture` | `assets/built/sjoin_campo_grande.png` | `assets/verified_snippets.py` → `deck_figures()` |
| `sjoin-choropleth` | `assets/built/schools_per_bairro.png` + code | `assets/verified_snippets.py` → `deck_figures()`; drawn by `scenes.code_block:figure_with_code` |
| `cre4-points` | `assets/built/cre4_points.png` + code | `assets/verified_snippets.py` → `deck_figures()`; drawn by `scenes.code_block:figure_with_code` |
| `cre4-hull` | `assets/built/cre4_hull.png` + code | `assets/verified_snippets.py` → `deck_figures()`; drawn by `scenes.code_block:figure_with_code` |
| `cre4-circle` | `assets/built/cre4_circle.png` + code | `assets/verified_snippets.py` → `deck_figures()`; drawn by `scenes.code_block:figure_with_code` |
| `cre4-centroid` | `assets/built/cre4_centroid.png` + code | `assets/verified_snippets.py` → `deck_figures()`; drawn by `scenes.code_block:figure_with_code` |
| `hull-vs-circle` | `assets/built/cre4_hull_vs_circle.png` | `assets/verified_snippets.py` → `deck_figures()` |

### Folium screenshots

| Beat | File | Built by |
|---|---|---|
| `folium-markers-shot` | `assets/built/folium_markers.png` | `assets/screenshot_maps.py` (headless Chromium, OSM tiles) |
| `folium-cluster-shot` | `assets/built/folium_cluster.png` | `assets/screenshot_maps.py` (headless Chromium, OSM tiles) |
| `folium-heatmap-shot` | `assets/built/folium_heatmap.png` | `assets/screenshot_maps.py` (headless Chromium, OSM tiles) |
| `folium-shapes-shot` | `assets/built/folium_shapes.png` | `assets/screenshot_maps.py` (headless Chromium, OSM tiles) |

Each screenshot carries the caption "Map © OpenStreetMap contributors · Data:
DATA.RIO, CC BY 4.0" through `visual.attribution`.

### Diagrams

| Beat | Visual | Built by |
|---|---|---|
| `path-recap` | graph (5 nodes) | the library's diagram builder |

### Code panels (19 beats)

Drawn at render time by `scenes.code_block:code` from the code in the beat,
which is byte-identical to the matching cell of `assets/verified_snippets.py`:
`pandas-read`, `pandas-filter`, `pandas-groupby`, `pandas-merge`, `geo-points`, `geo-read`, `geo-pandas-still-works`, `sjoin-code`, `sjoin-count`, `per-capita` (backup), `crs-degrees` (backup), `folium-map`, `folium-markers`, `folium-cluster`, `folium-heatmap`, `folium-shapes`, `folium-choropleth` (backup), `folium-layers` (backup), `folium-save`.
