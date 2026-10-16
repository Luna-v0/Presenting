"""Build the class's one companion notebook from the verified slide code.

    uv run --no-project --with nbformat python make_notebooks.py [OUT_DIR]

OUT_DIR defaults to Data_Science_be_like's notebooks folder next to this repo
(/mnt/hd/Repos/ds_be_like/code/notebooks). Writes one notebook, geo_folium.ipynb,
with one part per activity block of the screenplay, in its order and wording.

Every exercise cell is a comment-only skeleton, so it never errors when run.
The cell right after it holds the real solution, collapsed in both Colab (its
first line is `# @title Solution { display-mode: "form" }`) and JupyterLab
(its metadata has `"jupyter": {"source_hidden": true}`), so "Run all" plays
top to bottom while the solutions stay out of sight.

Every solution that is also slide code is taken verbatim from the matching
`# %% <beat-id>` cell of verified_snippets.py, so the notebook and the slides
cannot drift apart. The notebook is written without outputs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE.parents[4] / "ds_be_like" / "code" / "notebooks"


def verified_cells() -> dict[str, str]:
    cells, name, buf = {}, None, []
    for line in (HERE / "verified_snippets.py").read_text().split("\n"):
        if line.startswith("# ═══"):
            break
        match = re.match(r"# %% (\S+)", line)
        if match:
            if name:
                cells[name] = "\n".join(buf).strip("\n")
            name, buf = match.group(1), []
            continue
        if not line.startswith("# ──"):
            buf.append(line)
    if name:
        cells[name] = "\n".join(buf).strip("\n")
    return cells


V = verified_cells()


def v(*ids: str) -> str:
    return "\n".join(V[i] for i in ids)


def as_comment(text: str) -> str:
    """Every line of text, commented out, so it is safe inside a code cell."""
    return "\n".join("# " + line if line.strip() else "#" for line in text.split("\n"))


# ── the notebook, as (kind, ...) entries ────────────────────────────────────
#   ("md", text)                      a markdown cell
#   ("md2", question, answer)         a visible question, then a hidden answer
#                                      (the answer is prose, so it is commented
#                                      out rather than run as code)
#   ("code", source)                  a given, runnable code cell
#   ("todo", label, stub, solution)   a visible comment-only skeleton, then the
#                                      hidden solution that actually runs

INTRO = """\
Companion notebook to the class **Points on a map**: GeoPandas and folium on
Rio de Janeiro's open data. There is one part per notebook block of the class,
in the same order:

1. pandas warm-up
2. GeoDataFrame
3. spatial join
4. shapes
5. the map

**Running it.** On Google Colab, geopandas and folium are already installed:
just run the cells. Locally, install them first:
`pip install geopandas folium mapclassify`.

**Data.** Four datasets from DATA.RIO, the open-data portal of the Prefeitura
da Cidade do Rio de Janeiro (Instituto Pereira Passos, IPP), all under the
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) licence:

- [Limite de Bairros](https://www.data.rio/datasets/PCRJ::limite-de-bairros/about):
  the 167 neighbourhood polygons;
- Escolas Municipais: the 1,590 units of the Secretaria Municipal de Educação,
  with latitude and longitude;
- Limites CRE: the 11 regional education offices, with their area;
- Censo 2022, população por bairros (preliminary): residents per bairro.

The setup cell downloads them once into `data/rio/` and reuses them after that.

**Your own points.** Everything that needs only coordinates works with any CSV
that has `latitude` and `longitude` columns: read your file instead of
`escolas.csv`. The cells that use school columns (`tipo`, `cre`,
`denominacao`) are the only ones you would need to adapt."""

DATA_CELL = '''\
# The four DATA.RIO files, cached in data/rio/.
# Source: Prefeitura da Cidade do Rio de Janeiro / Instituto Pereira Passos (IPP),
# DATA.RIO (https://www.data.rio), licence CC BY 4.0.
import json
import shutil
import urllib.parse
import urllib.request
from pathlib import Path

DATA = Path("data/rio")
# Only if DATA.RIO cannot be reached: the same four files, kept with the class
# slides (the Presenting repository cloned next to ds_be_like).
FALLBACK = Path("../../../Presenting/manim-videos/decks/geo-folium/assets/data")
FILES = ["escolas.csv", "cre.csv", "populacao_bairros.csv", "bairros.geojson"]
ARCGIS = "https://pgeo3.rio.rj.gov.br/arcgis/rest/services/"


def arcgis(layer, **params):
    """Query the city's ArcGIS server: a GeoJSON dict, or a table of attributes."""
    params = {"where": "1=1", "f": "json", **params}
    rows = []
    for _ in range(20):                         # the largest layer fits in one page
        query = urllib.parse.urlencode({**params, "resultOffset": len(rows)})
        with urllib.request.urlopen(f"{ARCGIS}{layer}/query?{query}", timeout=120) as r:
            page = json.load(r)
        if params["f"] != "json":
            return page
        rows += [feature["attributes"] for feature in page["features"]]
        if not page.get("exceededTransferLimit"):
            return pd.DataFrame(rows)
    raise RuntimeError(f"{layer}: the server kept paginating")


def download():
    escolas = arcgis("Educacao/SME/FeatureServer/1", returnGeometry="false",
                     outFields="designacao,denominacao,tipo,cre,latitude,longitude")
    escolas["cre"] = escolas["cre"].astype(int)
    escolas["denominacao"] = escolas["denominacao"].str.strip()

    cre = arcgis("Educacao/SME/FeatureServer/0", returnGeometry="false",
                 outFields="codigo,nome,Shape__Area")
    cre = pd.DataFrame({"cre": cre["codigo"].astype(int), "nome": cre["nome"],
                        "area_km2": (cre["Shape__Area"] / 1e6).round(2)})

    pop = arcgis("Censo/Limites_administrativos_Censo_2022/MapServer/2",
                 returnGeometry="false", outFields="codbairro,nome,Total_de_pessoas_2022")
    pop = pd.DataFrame({"codbairro": pop["codbairro"].astype(int), "nome": pop["nome"],
                        "populacao_2022": pop["Total_de_pessoas_2022"]})

    geo = arcgis("Cartografia/Limites_administrativos/FeatureServer/4", f="geojson",
                 outSR=4326, outFields="codbairro,nome,regiao_adm,rp")
    bairros = gpd.GeoDataFrame.from_features(geo["features"], crs=4326)
    bairros["codbairro"] = bairros["codbairro"].astype(int)
    bairros["regiao_adm"] = bairros["regiao_adm"].str.strip()
    geoms = bairros.geometry.to_numpy()
    if hasattr(shapely, "coverage_simplify"):   # shapely >= 2.1: ~4 MB down to ~1 MB
        geoms = shapely.coverage_simplify(geoms, tolerance=0.00005)
    bairros["geometry"] = shapely.set_precision(geoms, grid_size=0.00001)
    bairros = bairros[["codbairro", "nome", "regiao_adm", "rp", "geometry"]]

    # A short answer from the server must not become the cache.
    if len(escolas) < 1000 or len(cre) != 11 or len(pop) < 150 or len(bairros) < 150:
        raise RuntimeError("incomplete download")
    escolas.sort_values("designacao").to_csv(DATA / "escolas.csv", index=False)
    cre.sort_values("cre").to_csv(DATA / "cre.csv", index=False)
    pop.sort_values("codbairro").to_csv(DATA / "populacao_bairros.csv", index=False)
    bairros.sort_values("codbairro").to_file(DATA / "bairros.geojson", driver="GeoJSON")


DATA.mkdir(parents=True, exist_ok=True)
if all((DATA / name).exists() for name in FILES):
    print("using the files already in", DATA)
else:
    try:
        download()
        print("downloaded the four DATA.RIO files into", DATA)
    except Exception as error:
        print("DATA.RIO unreachable:", error)
        for name in FILES:
            shutil.copy(FALLBACK / name, DATA / name)
        print("copied them from", FALLBACK)'''

NOTEBOOK = [
    ("md", "# Points on a map: GeoPandas and folium\n\n" + INTRO
     + "\n\nCells marked **TODO** are yours: write your code where the cell "
       "says `# your code here`. Solutions hidden under each exercise, as the "
       "cell right after it; run all and it defines what later cells need."),
    ("md", "## Setup"),
    ("code", V["imports"]),
    ("code", DATA_CELL),

    # ── Part 1 ──
    ("md", "## Part 1: pandas warm-up\n\n"
           "Warm up on today's data with the four pandas moves: read the schools, "
           "keep one type, count per CRE, merge in the CRE table.\n\n"
           "Load `escolas.csv`, keep only the crèches, count schools per type and per "
           "CRE, then merge `cre.csv` in and compute schools per km². Which CRE is the "
           "densest, and which school drops out of the merge?"),
    ("todo", "1.1 Read `data/rio/escolas.csv` into `escolas` and look at the first rows.",
     "escolas = ____\nescolas.head()",
     v("pandas-read")),
    ("todo", "1.2 Keep only the crèches (`tipo == \"Creche Municipal\"`). How many are there?",
     "creches = ____\nlen(creches)",
     v("pandas-filter") + "\nlen(creches)"),
    ("todo", "1.3 Count schools per type with `groupby`.",
     "por_tipo = ____\npor_tipo.sort_values(ascending=False)",
     v("pandas-groupby") + "\npor_tipo.sort_values(ascending=False)"),
    ("todo", "1.4 Count schools per CRE, merge `cre.csv` in on the `cre` column, and "
             "compute schools per km². Which CRE is the densest?",
     'cre = pd.read_csv("data/rio/cre.csv")\n'
     "por_cre = ____  # schools per CRE: a DataFrame with a column n_escolas\n"
     "por_cre = ____  # merge cre in on the \"cre\" column\n"
     'por_cre["por_km2"] = ____\n'
     'por_cre.sort_values("por_km2", ascending=False)',
     v("pandas-merge") + '\npor_cre.sort_values("por_km2", ascending=False)'),
    ("todo", "1.5 `merge` keeps only the rows that match. Which school drops out, "
             "and why?",
     "escolas[____]",
     'escolas[~escolas["cre"].isin(cre["cre"])]'),
    ("md2", "*Your answer:*",
     "*Answer:* the adult-education reference centre has CRE 12, and `cre.csv` has "
     "no row for CRE 12. `merge` is an inner join by default, so the row is "
     "dropped without a warning."),

    # ── Part 2 ──
    ("md", "## Part 2: GeoDataFrame\n\n"
           "Turn the schools into a GeoDataFrame, read the bairros, and draw both on "
           "one map. Then look for a school that seems to be outside the city.\n\n"
           "Build `pontos` from `escolas` with `points_from_xy` and `crs=4326`, read "
           "`bairros.geojson`, and plot the bairros with the schools on top. Plot only "
           "the CIEPs in a second figure. One school looks like it sits outside the "
           "city: which one?\n\n"
           "A GeoDataFrame is the same DataFrame with one more column, `geometry`. "
           "x is the longitude."),
    ("todo", "2.1 Turn `escolas` into a GeoDataFrame `pontos` (longitude first, "
             "`crs=4326`).",
     "xy = ____\npontos = ____\npontos.head()",
     v("geo-points") + "\npontos.head()"),
    ("todo", "2.2 Read `data/rio/bairros.geojson` into `bairros`.",
     "bairros = ____\nbairros.head()",
     v("geo-read") + "\nbairros.head()"),
    ("md", "Everything from pandas still works on a GeoDataFrame:"),
    ("code", 'pontos.groupby("tipo").size()'),
    ("todo", "2.3 Plot the bairros, then the schools on top of them.",
     "ax = ____\npontos.plot(ax=ax, markersize=2)",
     v("geo-plot")),
    ("todo", "2.4 The same filter as in Part 1, now on `pontos`: plot only the CIEPs.",
     'cieps_geo = ____\nax = bairros.plot(color="white", edgecolor="grey")\n'
     "cieps_geo.plot(ax=ax, markersize=8)",
     'cieps_geo = pontos[pontos["tipo"] == "CIEP"]\n'
     'ax = bairros.plot(color="white", edgecolor="grey")\n'
     "cieps_geo.plot(ax=ax, markersize=8)"),
    ("md2", "2.5 One school looks like it sits outside the city. Which one?\n\n"
            "*Your answer:*",
     "2.5 One school looks like it sits outside the city. Which one?\n\n"
     "*Answer:* the lone dot north of Campo Grande, on the city's western edge: "
     "Escola Municipal Guandu. Part 3 finds it with code."),

    # ── Part 3 ──
    ("md", "## Part 3: spatial join\n\n"
           "Join the schools to the bairros, count schools per bairro, and map the "
           "counts. Then find the school from part 2 that the join drops.\n\n"
           "`sjoin` `pontos` to `bairros` with `predicate=\"within\"`, count schools per "
           "bairro, merge the counts onto `bairros` and plot them. Which bairro has the "
           "most schools, and which school is missing from the join? Stretch: merge "
           "`populacao_bairros.csv` and map schools per 10,000 residents.\n\n"
           "`sjoin` is `merge` with location as the key: each school gets the columns of "
           "the bairro it falls within."),
    ("todo", "3.1 Join `pontos` to `bairros` with `predicate=\"within\"`.",
     'com_bairro = ____\ncom_bairro[["denominacao", "nome", "regiao_adm"]].head()',
     v("sjoin-code")),
    ("todo", "3.2 Count schools per bairro (`codbairro`), and merge the counts back "
             "onto `bairros`. Use `how=\"left\"` so bairros with no school stay.",
     "n = ____  # schools per codbairro\n"
     'n = n.reset_index(name="n_escolas")\n'
     "bairros = ____  # left merge onto bairros\n"
     'bairros["n_escolas"] = bairros["n_escolas"].fillna(0)',
     v("sjoin-count")),
    ("todo", "3.3 Plot the bairros coloured by `n_escolas`, with a legend.",
     "____",
     v("sjoin-choropleth")),
    ("todo", "3.4 Which bairros have the most schools?",
     'bairros.nlargest(3, ____)[["nome", "n_escolas"]]',
     'bairros.nlargest(3, "n_escolas")[["nome", "n_escolas"]]'),
    ("todo", "3.5 `sjoin` keeps only the schools that fall within a bairro. Which "
             "school is missing from `com_bairro`?",
     'pontos[____][["denominacao", "latitude", "longitude"]]',
     'pontos[~pontos.index.isin(com_bairro.index)][["denominacao", "latitude", "longitude"]]'),
    ("todo", "3.6 *Stretch.* Merge `populacao_bairros.csv` in on `codbairro` (not on the "
             "name: the two files spell one bairro differently), and map schools per "
             "10,000 residents. Two bairros have no 2022 population: they show grey.",
     'pop = pd.read_csv("data/rio/populacao_bairros.csv")\n'
     'pop = pop[["codbairro", "populacao_2022"]]\n'
     "bairros = ____  # left merge on codbairro\n"
     'taxa = bairros["n_escolas"] / bairros["populacao_2022"]\n'
     'bairros["por_10mil"] = taxa * 10_000\n'
     'bairros.plot(column="por_10mil", legend=True, missing_kwds={"color": "lightgrey"})',
     v("per-capita")
     + '\nbairros.plot(column="por_10mil", legend=True, missing_kwds={"color": "lightgrey"})'),

    # ── Part 4 ──
    ("md", "## Part 4: shapes\n\n"
           "Pick another CRE or one school type, wrap its schools in a hull and a "
           "circle, find the centroid, and plot all three over the points.\n\n"
           "Choose a CRE or a school type. Compute the convex hull, the minimal circle "
           "and the centroid, and plot them over the points. Which shape would you "
           "report as \"the area these schools cover\", and why?\n\n"
           "Each shape is one library call: no algorithm needed."),
    ("todo", "4.1 Select your points (the class used `cre == 4`) and fuse them into "
             "one shape with `union_all()`.",
     "sel = ____  # one CRE, or one school type\npts = ____  # all the points as one shape\n"
     "len(sel)",
     v("cre4-points") + "\nlen(sel)"),
    ("todo", "4.2 The convex hull, the minimal circle and the centroid of `pts`.",
     "hull = ____\ncircle = ____\ncentro = ____",
     v("cre4-hull", "cre4-circle", "cre4-centroid")),
    ("todo", "4.3 Plot the hull and the circle over the bairros and your points, "
             "zoomed to the circle.",
     'ax = bairros.plot(color="white", edgecolor="grey")\n'
     "shapes = ____  # a GeoSeries holding hull and circle, crs=4326\n"
     'shapes.plot(ax=ax, facecolor="none", edgecolor=["green", "orange"])\n'
     "sel.plot(ax=ax, markersize=4)\n"
     'ax.plot(centro.x, centro.y, "k+", markersize=15)\n'
     "xmin, ymin, xmax, ymax = circle.buffer(0.005).bounds\n"
     "ax.set_xlim(xmin, xmax)\n"
     "ax.set_ylim(ymin, ymax)",
     'ax = bairros.plot(color="white", edgecolor="grey")\n'
     "shapes = gpd.GeoSeries([hull, circle], crs=4326)\n"
     'shapes.plot(ax=ax, facecolor="none", edgecolor=["green", "orange"])\n'
     "sel.plot(ax=ax, markersize=4)\n"
     'ax.plot(centro.x, centro.y, "k+", markersize=15)\n'
     "xmin, ymin, xmax, ymax = circle.buffer(0.005).bounds\n"
     "ax.set_xlim(xmin, xmax)\n"
     "ax.set_ylim(ymin, ymax)"),
    ("md2", "4.4 Which shape would you report as \"the area these schools cover\", "
            "and why?\n\n*Your answer:*",
     "4.4 Which shape would you report as \"the area these schools cover\", and why?\n\n"
     "*One answer:* the hull, because it hugs the points: the circle takes in water and "
     "neighbourhoods the schools do not serve. For the 4th CRE the circle is about three "
     "times the hull. Neither is \"the\" area: the number depends on the shape you choose, "
     "so say which one you used."),
    ("todo", "4.5 *Stretch.* Areas in km². Latitude and longitude are degrees, not metres, "
             "so reproject to a metric CRS with `.to_crs()` before measuring "
             "(EPSG:31983 is UTM zone 23S, in metres).",
     "pts_m = sel.to_crs(31983).union_all()  # UTM 23S, metres\n"
     "hull_km2 = ____\ncirc_m = ____\ncircle_km2 = ____\n"
     "round(hull_km2, 1), round(circle_km2, 1)",
     "\n".join(V["crs-degrees"].split("\n")[:4])
     + "\nround(hull_km2, 1), round(circle_km2, 1)"),

    # ── Part 5 ──
    ("md", "## Part 5: the map\n\n"
           "Build one map with everything: markers for a subset, every school in a "
           "cluster, a heat layer, and your shapes from part 4. Save it as one file.\n\n"
           "On one folium map: markers with popups for a subset you choose, every school "
           "in a MarkerCluster, a HeatMap, and the hull, circle and centroid from part 4; "
           "then save it with `m.save(\"map.html\")` and open the file in a browser. "
           "Stretch: a choropleth of schools per 10,000 residents and a LayerControl.\n\n"
           "folium wants `[lat, lon]`, which is `[y, x]`."),
    ("todo", "5.1 A map centred on `[-22.91, -43.45]` at zoom 11.",
     "m = ____",
     v("folium-map")),
    ("todo", "5.2 One marker with a popup per school of a small subset (the class used "
             "the 101 CIEPs).",
     "cieps = ____  # a small subset, e.g. the CIEPs\n"
     "for _, row in cieps.iterrows():\n"
     "    folium.Marker(\n"
     "        ____,  # [lat, lon]\n"
     '        popup=folium.Popup(row["denominacao"]),\n'
     "    ).add_to(m)",
     v("folium-markers")),
    ("todo", "5.3 Every school, added to a `MarkerCluster` instead of the map.",
     "cluster = ____\ncluster.add_to(m)\n"
     "for _, row in escolas.iterrows():\n"
     "    folium.Marker(\n"
     '        [row["latitude"], row["longitude"]],\n'
     '        popup=row["denominacao"],\n'
     "    ).add_to(cluster)",
     v("folium-cluster")),
    ("todo", "5.4 A `HeatMap` from a list of `[lat, lon]` pairs.",
     "coords = ____\n"
     'plugins.HeatMap(coords, name="heat", radius=12).add_to(m)',
     v("folium-heatmap")),
    ("todo", "5.5 Your hull and circle from part 4 with `folium.GeoJson`, and the "
             "centroid as a marker.",
     'folium.GeoJson(____, name="convex hull").add_to(m)\n'
     'folium.GeoJson(____, name="minimal circle").add_to(m)\n'
     "folium.Marker(____).add_to(m)  # the centroid, as [y, x]",
     v("folium-shapes")),
    ("todo", "5.6 *Stretch* (needs 3.6). A choropleth of schools per 10,000 residents, "
             "then a `LayerControl` to switch layers on and off.",
     "folium.Choropleth(\n"
     "    geo_data=bairros,\n"
     "    data=bairros,\n"
     '    columns=["codbairro", "por_10mil"],\n'
     "    key_on=____,  # where codbairro sits in each GeoJSON feature\n"
     '    fill_color="YlGn",\n'
     '    nan_fill_color="lightgrey",\n'
     '    legend_name="schools per 10,000 residents",\n'
     ").add_to(m)\n"
     "folium.LayerControl().add_to(m)",
     v("folium-choropleth", "folium-layers")),
    ("todo", "5.7 Save the map as `map.html` and show it here.",
     "m.save(____)\nm",
     v("folium-save") + "\nm"),
    ("md", "`map.html` is one file: it opens in any browser, with no Python. "
           "That is the map you can send to someone."),
]


SOLUTION_TITLE = '# @title Solution { display-mode: "form" }\n'
HIDDEN = {"jupyter": {"source_hidden": True}}


def build() -> nbformat.NotebookNode:
    cells = []
    for entry in NOTEBOOK:
        kind = entry[0]
        if kind == "md":
            cells.append(new_markdown_cell(entry[1]))
        elif kind == "md2":
            _, question, answer = entry
            cells.append(new_markdown_cell(question))
            cells.append(new_code_cell(SOLUTION_TITLE + as_comment(answer),
                                       metadata={"tags": ["solution"], **HIDDEN}))
        elif kind == "code":
            cells.append(new_code_cell(entry[1]))
        elif kind == "todo":
            _, label, stub, solution = entry
            num, text = label.split(" ", 1)
            cells.append(new_markdown_cell(f"**TODO {num}** {text}"))
            cells.append(new_code_cell(as_comment(stub) + "\n# your code here",
                                       metadata={"tags": ["todo"]}))
            cells.append(new_code_cell(SOLUTION_TITLE + solution,
                                       metadata={"tags": ["solution"], **HIDDEN}))
    nb = new_notebook(cells=cells)
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }
    return nb


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    out.mkdir(parents=True, exist_ok=True)
    nb = build()
    nbformat.validate(nb)
    nbformat.write(nb, out / "geo_folium.ipynb")
    print(out / "geo_folium.ipynb", len(nb.cells), "cells")


if __name__ == "__main__":
    main()
