"""Screenshots of the deck's folium maps, for the four "what you get" beats.

    uv run --no-project --with geopandas --with shapely --with folium \
        --with mapclassify --with matplotlib python screenshot_maps.py

Each map is built with the same calls as the slide before it (taken from the
namespace verified_snippets.py leaves behind, so the data and the shapes are
the verified ones), saved as HTML under built/maps/, and photographed with a
headless Chrome or Chromium into built/folium_*.png, where the screenplay's
`asset:` lines find them. Needs network: the basemap tiles come from
OpenStreetMap, whose attribution stays visible in every shot.

The only departures from the slide code are presentational: each shot holds
one layer, the view is fitted to what the beat is about, and one popup in the
markers shot is opened (`show=True`) so the popup is visible in a still.
"""

from __future__ import annotations

import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "built"
MAPS = OUT / "maps"
#: Wide, because the claim-above-figure visual slot is about 3.3:1, and no
#: wider than 1600 px, beyond which manim pays per pixel for nothing visible.
SIZE = (1600, 600)
#: The browser window is taller than the map, and the shot is cropped back to
#: the map. With the map filling the window exactly, Leaflet sizes its tile
#: grid before headless Chrome settles the viewport and leaves a grey strip of
#: unloaded tiles along one edge.
WINDOW = (SIZE[0], SIZE[1] + 200)
#: Virtual time Chrome lets the page run before the shot: tiles and the
#: marker-cluster animation have settled well inside it.
WAIT_MS = 20000
#: The CIEP whose popup is open in the markers shot.
OPEN_POPUP = "Ciep Henfil"


def verified_namespace() -> dict:
    argv = sys.argv
    sys.argv = [str(HERE / "verified_snippets.py"), str(OUT), "--no-figures"]
    try:
        return runpy.run_path(str(HERE / "verified_snippets.py"),
                              run_name="verified_snippets")
    finally:
        sys.argv = argv


def browser() -> str:
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    raise SystemExit("needs Chrome or Chromium on PATH for the screenshots")


def shoot(html: Path, png: Path) -> None:
    from PIL import Image

    with tempfile.TemporaryDirectory() as profile:
        raw = Path(profile) / "raw.png"
        try:
            subprocess.run(
                [browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                 "--no-first-run", "--no-default-browser-check",
                 f"--user-data-dir={profile}", f"--window-size={WINDOW[0]},{WINDOW[1]}",
                 f"--virtual-time-budget={WAIT_MS}", f"--screenshot={raw}", html.as_uri()],
                check=True, capture_output=True, timeout=300)
        except subprocess.CalledProcessError as e:
            raise SystemExit(f"{html.name}: {e.stderr.decode()[-2000:]}") from e
        with Image.open(raw) as image:
            image.crop((0, 0, SIZE[0], SIZE[1])).save(png)
    print("screenshot", png.name)


def main() -> None:
    ns = verified_namespace()
    folium, plugins = ns["folium"], ns["plugins"]
    escolas, cieps, bairros = ns["escolas"], ns["cieps"], ns["bairros"]
    hull, circle, centro = ns["hull"], ns["circle"], ns["centro"]

    def fresh(bounds):
        minx, miny, maxx, maxy = bounds
        m = folium.Map(location=[-22.91, -43.45], zoom_start=11,
                       width=SIZE[0], height=SIZE[1])
        m.fit_bounds([[miny, minx], [maxy, maxx]])
        return m

    city = bairros.total_bounds
    maps = {}

    m = fresh(city)
    for _, row in cieps.iterrows():
        folium.Marker(
            [row["latitude"], row["longitude"]],
            popup=folium.Popup(row["denominacao"],
                               show=row["denominacao"] == OPEN_POPUP),
        ).add_to(m)
    maps["folium_markers"] = m

    m = fresh(city)
    cluster = plugins.MarkerCluster(name="schools")
    cluster.add_to(m)
    for _, row in escolas.iterrows():
        folium.Marker(
            [row["latitude"], row["longitude"]],
            popup=row["denominacao"],
        ).add_to(cluster)
    maps["folium_cluster"] = m

    m = fresh(city)
    coords = escolas[["latitude", "longitude"]].values.tolist()
    plugins.HeatMap(coords, name="heat", radius=12).add_to(m)
    maps["folium_heatmap"] = m

    m = fresh(circle.bounds)
    folium.GeoJson(hull, name="convex hull").add_to(m)
    folium.GeoJson(circle, name="minimal circle").add_to(m)
    folium.Marker([centro.y, centro.x]).add_to(m)
    maps["folium_shapes"] = m

    MAPS.mkdir(parents=True, exist_ok=True)
    for name, m in maps.items():
        html = MAPS / f"{name}.html"
        m.save(str(html))
        shoot(html, OUT / f"{name}.png")


if __name__ == "__main__":
    main()
