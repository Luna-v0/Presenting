"""geo-folium: every line of code that goes on a slide, run on the real Rio data.

Each `# %% <beat-id>` cell is the code of the screenplay beat with that id,
verbatim, in deck order (cells marked "backup" belong to backup beats; cells
marked "not on a slide" support the notebook only). The cells are also the
skeleton of the companion notebook, geo_folium_exercises.ipynb in
Data_Science_be_like, which is why they read `data/rio/...` (the notebook's
download cache) and save `map.html` the way a notebook would.
assets/make_notebooks.py builds the exercise and solution notebooks from them.

Run it in a throwaway environment, never a project's:

    uv run --no-project --with geopandas --with shapely --with folium \
        --with mapclassify --with matplotlib python verified_snippets.py [WORKDIR]

WORKDIR defaults to ./built next to this file (git-ignored); pass --no-figures
to skip the deck stills. The script copies ./data into WORKDIR/data/rio and runs there,
so the relative paths in the slide code are the real ones. It leaves behind
the deck's figures (PNG, on the deck identity) and the folium map (map.html).

Verified 2026-10-15 with Python 3.14.0, pandas 3.0.6, geopandas 1.2.0,
shapely 2.2.0 (GEOS 3.14.1), folium 0.20.0, mapclassify 2.11.0,
matplotlib 3.11.2, pyproj 3.8.0, pyogrio 0.13.0, numpy 2.5.4; and again with
Python 3.12, pandas 2.2.3, geopandas 1.0.1, shapely 2.0.7, folium 0.19.7.
Expected warnings: exactly one, from `crs-centroid-warning` (centroid on a
geographic CRS). Slide code lines stay at or under 60 characters, the most a
full-width code panel holds at the legibility floor. The checks at the bottom
fail loudly if the data or a library changes under the slides.
"""

# %% setup (not on a slide: makes the relative paths below real)
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
WORK = Path(ARGS[0]).resolve() if ARGS else HERE / "built"
WORK.mkdir(parents=True, exist_ok=True)
shutil.copytree(HERE / "data", WORK / "data" / "rio", dirs_exist_ok=True)
os.chdir(WORK)

# %% imports
import pandas as pd
import geopandas as gpd
import shapely
import folium
from folium import plugins

# ── Section 2: what you already know (pandas) ───────────────────────────────

# %% pandas-read
escolas = pd.read_csv("data/rio/escolas.csv")
escolas.head()

# %% pandas-filter
creches = escolas[escolas["tipo"] == "Creche Municipal"]

# %% pandas-groupby
por_tipo = escolas.groupby("tipo").size()

# %% pandas-merge
cre = pd.read_csv("data/rio/cre.csv")
por_cre = escolas.groupby("cre").size()
por_cre = por_cre.reset_index(name="n_escolas")
por_cre = por_cre.merge(cre, on="cre")
por_cre["por_km2"] = por_cre.n_escolas / por_cre.area_km2

# ── Section 3: one more column (GeoDataFrame) ───────────────────────────────

# %% geo-points
xy = gpd.points_from_xy(escolas.longitude, escolas.latitude)
pontos = gpd.GeoDataFrame(escolas, geometry=xy, crs=4326)

# %% geo-read
bairros = gpd.read_file("data/rio/bairros.geojson")

# %% geo-plot
ax = bairros.plot(color="white", edgecolor="grey")
pontos.plot(ax=ax, markersize=2)

# %% geo-pandas-still-works
creches = pontos[pontos["tipo"] == "Creche Municipal"]
pontos.groupby("tipo").size()

# ── Section 4: merge by location (spatial join) ─────────────────────────────

# %% sjoin-code
com_bairro = gpd.sjoin(pontos, bairros, predicate="within")
com_bairro[["denominacao", "nome", "regiao_adm"]].head()

# %% sjoin-count
n = com_bairro.groupby("codbairro").size()
n = n.reset_index(name="n_escolas")
bairros = bairros.merge(n, on="codbairro", how="left")
bairros["n_escolas"] = bairros["n_escolas"].fillna(0)

# %% sjoin-choropleth
bairros.plot(column="n_escolas", legend=True)

# %% per-capita (backup)
pop = pd.read_csv("data/rio/populacao_bairros.csv")
pop = pop[["codbairro", "populacao_2022"]]
bairros = bairros.merge(pop, on="codbairro", how="left")
taxa = bairros["n_escolas"] / bairros["populacao_2022"]
bairros["por_10mil"] = taxa * 10_000

# ── Section 5: what area do the points cover? ───────────────────────────────

# %% cre4-points
sel = pontos[pontos["cre"] == 4]
pts = sel.union_all()

# %% cre4-hull
hull = pts.convex_hull

# %% cre4-circle
circle = shapely.minimum_bounding_circle(pts)

# %% cre4-centroid
centro = pts.centroid

# %% circle-geoseries (not on a slide: the same circle as a GeoSeries method)
circle_gs = sel.dissolve().minimum_bounding_circle()

# %% crs-centroid-warning (not on a slide: what students will see; warns)
centros = bairros.centroid

# %% crs-degrees (backup)
pts_m = sel.to_crs(31983).union_all()  # UTM 23S, metres
hull_km2 = pts_m.convex_hull.area / 1e6
circ_m = shapely.minimum_bounding_circle(pts_m)
circle_km2 = circ_m.area / 1e6
centros = bairros.to_crs(31983).centroid.to_crs(4326)

# ── Section 6: a map people can click (folium) ──────────────────────────────

# %% folium-map
m = folium.Map(location=[-22.91, -43.45], zoom_start=11)

# %% folium-markers
cieps = escolas[escolas["tipo"] == "CIEP"]
for _, row in cieps.iterrows():
    folium.Marker(
        [row["latitude"], row["longitude"]],
        popup=folium.Popup(row["denominacao"]),
    ).add_to(m)

# %% folium-cluster
cluster = plugins.MarkerCluster(name="schools")
cluster.add_to(m)
for _, row in escolas.iterrows():
    folium.Marker(
        [row["latitude"], row["longitude"]],
        popup=row["denominacao"],
    ).add_to(cluster)

# %% folium-heatmap
coords = escolas[["latitude", "longitude"]].values.tolist()
plugins.HeatMap(coords, name="heat", radius=12).add_to(m)

# %% folium-shapes
folium.GeoJson(hull, name="convex hull").add_to(m)
folium.GeoJson(circle, name="minimal circle").add_to(m)
folium.Marker([centro.y, centro.x]).add_to(m)

# %% folium-choropleth (backup)
folium.Choropleth(
    geo_data=bairros,
    data=bairros,
    columns=["codbairro", "por_10mil"],
    key_on="feature.properties.codbairro",
    fill_color="YlGn",
    nan_fill_color="lightgrey",
    legend_name="schools per 10,000 residents",
).add_to(m)

# %% folium-layers (backup)
folium.LayerControl().add_to(m)

# %% folium-save (backup)
m.save("map.html")


# ═══ Not slide code below: checks, and the deck's figures ═══════════════════

def checks() -> None:
    """Fail loudly if the data or a library changed under the slides."""
    assert len(escolas) == 1590, len(escolas)
    assert len(creches) == 247 and isinstance(creches, gpd.GeoDataFrame)
    assert por_tipo.idxmax() == "Escola Municipal" and por_tipo.max() == 911
    # merge is inner by default: the one school with cre 12 (an adult-education
    # reference centre) has no row in cre.csv and drops out.
    assert len(por_cre) == 11 and por_cre["n_escolas"].sum() == 1589
    assert pontos.crs.to_epsg() == 4326 and len(pontos) == 1590
    assert len(bairros) == 167
    # sjoin is inner by default: one school (E.M. Guandu, designacao 918072) sits
    # about 1.7 km outside the municipal boundary, so it matches no bairro. Same
    # at full resolution; it is the data, not the simplification.
    assert len(com_bairro) == 1589, f"{1590 - len(com_bairro)} schools in no bairro"
    assert not com_bairro.index.duplicated().any(), "a school matched two bairros"
    assert set(pontos.index) - set(com_bairro.index) == set(
        escolas.index[escolas["designacao"] == 918072])
    assert bairros["n_escolas"].sum() == 1589
    # Argentino (166) and Ingleses (167) have no Censo 2022 row.
    assert set(bairros.loc[bairros["populacao_2022"].isna(), "codbairro"]) == {166, 167}
    assert len(sel) == 166 and pts.geom_type == "MultiPoint"
    assert hull.geom_type == "Polygon" and circle.geom_type == "Polygon"
    # The circle comes back as a polygon inscribed in the true circle, so points
    # on the rim can sit a hair outside it; check against the exact radius.
    radius = shapely.minimum_bounding_radius(pts)
    rim = shapely.distance(sel.geometry.values, shapely.centroid(circle))
    assert rim.max() <= radius * (1 + 1e-6), (rim.max(), radius)
    assert circle.area > hull.area
    assert circle_gs.iloc[0].equals_exact(circle, 1e-9)
    assert len(cieps) == 101
    assert 2.5 < circle_km2 / hull_km2 < 3.5
    assert isinstance(m, folium.Map) and Path("map.html").stat().st_size > 0

    print("schools", len(escolas), "| creches", len(creches),
          "| bairros", len(bairros), "| joined", len(com_bairro))
    print("by type:", por_tipo.sort_values(ascending=False).head(3).to_dict())
    print(por_cre[["cre", "nome", "n_escolas", "por_km2"]].round(1).to_string(index=False))
    print("top bairros:", bairros.nlargest(3, "n_escolas")[["nome", "n_escolas"]]
          .to_dict("records"))
    print(f"CRE 4: {len(sel)} points | hull {hull_km2:.1f} km² | circle "
          f"{circle_km2:.1f} km² | ratio {circle_km2 / hull_km2:.2f}")
    print(f"centroid (lon, lat): {centro.x:.5f}, {centro.y:.5f}")
    print(f"map.html: {Path('map.html').stat().st_size / 1e6:.1f} MB")


def deck_figures() -> None:
    """The stills the screenplay's map beats point at, on the deck identity.

    Written next to map.html (assets/built/ by default), which is where the
    screenplay looks for them.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    style = HERE.parents[2] / "identity" / "out" / "presenting.mplstyle"
    if style.exists():
        plt.style.use(str(style))
    ink, struct_fill, struct_stroke = "#232A24", "#CFC6AE", "#8C8470"
    green, green_tint, green_dark, yellow = "#3D6349", "#CCE0C6", "#1E3527", "#A87F20"

    def base(ax, view=None):
        bairros.plot(ax=ax, color=struct_fill, edgecolor=struct_stroke, linewidth=0.4)
        ax.set_axis_off()
        if view is not None:
            ax.set_xlim(view[0], view[2])
            ax.set_ylim(view[1], view[3])

    def save(fig, name):
        # No wider or taller than 1600 px: manim resamples every source pixel
        # of an image on every frame, and nothing beyond that is visible.
        fig.savefig(name)
        from PIL import Image

        with Image.open(name) as image:
            long_edge = max(image.size)
        if long_edge > 1600:
            fig.savefig(name, dpi=fig.dpi * 1600 / long_edge * 0.995)
        plt.close(fig)
        print("figure", name)

    fig, ax = plt.subplots(figsize=(12, 6))
    base(ax)
    pontos.plot(ax=ax, markersize=2, color=ink)
    save(fig, "schools_on_bairros.png")

    fig, ax = plt.subplots(figsize=(12, 6))
    ramp = LinearSegmentedColormap.from_list(
        "sand_to_green", [struct_fill, green_tint, green, green_dark])
    bairros.plot(ax=ax, column="n_escolas", cmap=ramp, edgecolor=struct_stroke,
                 linewidth=0.3, legend=True,
                 legend_kwds={"label": "schools per bairro", "shrink": 0.6})
    ax.set_axis_off()
    # The colour bar has to read from the back of the room, not just on screen.
    colourbar = fig.axes[-1]
    colourbar.tick_params(labelsize=20)
    colourbar.yaxis.label.set_size(22)
    save(fig, "schools_per_bairro.png")

    # One bairro and the schools the join gave it.
    target = bairros[bairros["nome"] == "Campo Grande"]
    inside = com_bairro[com_bairro["nome"] == "Campo Grande"]
    x0, y0, x1, y1 = target.total_bounds
    pad = 0.03
    fig, ax = plt.subplots(figsize=(10, 6))
    base(ax, (x0 - pad, y0 - pad, x1 + pad, y1 + pad))
    target.plot(ax=ax, color=green_tint, edgecolor=green, linewidth=1.6)
    pontos.drop(inside.index).plot(ax=ax, markersize=6, color=struct_stroke)
    inside.plot(ax=ax, markersize=10, color=green_dark)
    save(fig, "sjoin_campo_grande.png")

    pad = 0.02
    xmin, ymin, xmax, ymax = circle.bounds
    view = (xmin - pad, ymin - pad, xmax + pad, ymax + pad)
    for name, shapes, mark_centre in (
            ("cre4_points.png", [], False),
            ("cre4_hull.png", [(hull, green)], False),
            ("cre4_circle.png", [(circle, green)], False),
            ("cre4_centroid.png", [], True),
            ("cre4_hull_vs_circle.png", [(hull, green), (circle, yellow)], False)):
        fig, ax = plt.subplots(figsize=(8, 6))
        base(ax, view)
        for shape, colour in reversed(shapes):
            gpd.GeoSeries([shape]).plot(ax=ax, facecolor="none", edgecolor=colour,
                                        linewidth=2.4)
        sel.plot(ax=ax, markersize=8, color=ink)
        if mark_centre:
            ax.plot(centro.x, centro.y, marker="+", markersize=22, color=green, mew=3)
        save(fig, name)


checks()
if "--no-figures" not in sys.argv:
    deck_figures()
