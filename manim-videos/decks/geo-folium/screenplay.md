---
slug: geo-folium
title: Points on a map
subtitle: GeoPandas and folium on Rio de Janeiro's open data
author: Eduardo Dantas Luna
date: "2026"
target: manim
duration_min: 240
brief: ./brief.md
---

# Section 1 — Points on a map of Rio

> **Bridge.** Opening frame: 1,590 municipal schools on a map of Rio and one question, what area do they cover, which the class answers by the end with tools that are mostly the pandas they already know.

## 1.1 — Points on a map

```yaml
id: title
origin: generated
layout: title-card
time_s: 20
transition: cut
generated_hash: 1bba1dd11dd07a2c
```

## 1.2 — What area do they cover?

```yaml
id: opening-question
origin: generated
layout: claim-above-figure
time_s: 75
transition: cut
visual:
  kind: constructible
  sub: geometry
  intent: every municipal school as a dot over the 167 bairro outlines, the whole city; built by assets/verified_snippets.py
  asset: schools_on_bairros.png
generated_hash: 6200e5623a63d878
```

**Note.** Anything Rio related is good.

**Claim.** Here are 1,590 points on a map of Rio, and the question for the next four hours is what area they cover.

**On slide.**
- 1,590 municipal schools, 167 bairros

**Skip.** Why these schools. They are a public, non-political point set; the code does not care what the points are.

## 1.3 — Today

```yaml
id: todays-path
origin: generated
layout: build-list
time_s: 60
transition: cut
generated_hash: de6391c78a2c318a
```

**Claim.** The class goes from pandas they know to a GeoDataFrame, a merge by location, shapes around points, and an interactive map, with the notebook between each block.

**On slide.**
- pandas you know: read, filter, group, merge
- GeoDataFrame: the same table, one more column
- Merge by location: the spatial join
- Wrap the points: hull, circle, centroid
- folium: a map people can click
- Each block ends in the notebook; two breaks

## 1.4 — Today's data

```yaml
id: the-data
origin: generated
layout: table-accented
time_s: 60
transition: cut
content:
  table:
    - [file, rows, what]
    - [escolas.csv, "1,590", "schools, lat/lon"]
    - [bairros.geojson, "167", bairro polygons]
    - [cre.csv, "11", education regions]
    - [populacao_bairros.csv, "165", Censo 2022 population]
  accent_rows: [2]
generated_hash: d6df28a3f13668a0
```

**Note.** no need to focus on police work based but we could use the api I got about crimes

**Claim.** Four small files from the city's open-data portal, and the schools file is the one every block builds on.

**On slide.**
- Four files from data.rio, CC BY 4.0

**Skip.** How the polygons were simplified. It is in fetch_data.py for whoever asks.

# Section 2 — What you already know: pandas

> **Bridge.** Everything today is pandas plus one column, so the class starts from the four pandas moves they already use, on today's data, and ends on the one merge pandas cannot do.

## 2.1 — What you already know: pandas

```yaml
id: pandas-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: da8c169ed64b4fbf
```

**Note.** And for geopandas I think you could start by recap about pandas and use it as basis of comparison for it.

## 2.2 — Read

```yaml
id: pandas-read
origin: generated
layout: claim-above-figure
time_s: 60
transition: cut
visual:
  kind: constructible
  intent: cell pandas-read of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      escolas = pd.read_csv("data/rio/escolas.csv")
      escolas.head()
generated_hash: b974bdcf118f8a6d
```

**Claim.** The schools arrive as an ordinary CSV with a latitude and a longitude column, and pandas reads it like any other table.

**On slide.**
- A CSV with latitude and longitude columns

## 2.3 — Filter

```yaml
id: pandas-filter
origin: generated
layout: claim-above-figure
time_s: 45
transition: cut
visual:
  kind: constructible
  intent: cell pandas-filter of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      creches = escolas[escolas["tipo"] == "Creche Municipal"]
generated_hash: e842fb1754e9f068
```

**Claim.** Filtering rows by a condition is a boolean mask, and it will work unchanged on a GeoDataFrame.

**On slide.**
- Filter: a boolean mask (247 crèches)

## 2.4 — Group

```yaml
id: pandas-groupby
origin: generated
layout: claim-above-figure
time_s: 45
transition: cut
visual:
  kind: constructible
  intent: cell pandas-groupby of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      por_tipo = escolas.groupby("tipo").size()
generated_hash: b23909d9114c4808
```

**Claim.** Counting per category is a groupby, and counting per bairro later is the same groupby on a column the spatial join adds.

**On slide.**
- Count per category: groupby
- 911 escolas, 286 EDIs, 247 crèches

## 2.5 — Merge on a key

```yaml
id: pandas-merge
origin: generated
layout: claim-above-figure
time_s: 90
transition: cut
visual:
  kind: constructible
  intent: cell pandas-merge of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      cre = pd.read_csv("data/rio/cre.csv")
      por_cre = escolas.groupby("cre").size()
      por_cre = por_cre.reset_index(name="n_escolas")
      por_cre = por_cre.merge(cre, on="cre")
      por_cre["por_km2"] = por_cre.n_escolas / por_cre.area_km2
generated_hash: 12ed2ba1c0863adf
```

**Claim.** A merge joins two tables on a column they share, here the CRE code, which brings in each region's name and area.

**On slide.**
- Merge: two tables, one shared key column

**Skip.** The one school with CRE 12 that the inner merge drops. It comes back in section 4 with the other data warts.

## 2.6 — The key that is missing

```yaml
id: missing-key
origin: generated
layout: claim-only
time_s: 45
transition: cut
generated_hash: 8217f372c67fdf3e
```

**Claim.** To count schools per bairro, merge needs a bairro column, and the schools only have coordinates.

## 2.7 — Notebook, part 1

```yaml
id: act-pandas-setup
origin: generated
layout: activity-setup
time_s: 120
transition: cut
content:
  task: >
    Warm up on today's data with the four pandas moves: read the schools, keep
    one type, count per CRE, merge in the CRE table.
  example: |
    por_cre = por_cre.merge(cre, on="cre")
generated_hash: 6b002388b1dd8248
```

**Claim.** The first exercise is the recap itself, done by hand on the data the rest of the class uses.

## 2.8 — Part 1: pandas warm-up

```yaml
id: act-pandas-parking
origin: generated
layout: activity-parking
time_s: 900
transition: cut
content:
  instructions: >
    Open geo_folium.ipynb, Part 1. Load escolas.csv, keep only the
    crèches, count schools per type and per CRE, then merge cre.csv in and
    compute schools per km². Which CRE is the densest, and which school drops
    out of the merge?
  constraints:
    - 15 minutes
    - pairs welcome
    - solutions hidden under each exercise
generated_hash: f23d0d5b0fc4a47a
```

**Claim.** Fifteen minutes on pandas alone, so the geo blocks start from code that just ran.

# Section 3 — One more column: the GeoDataFrame

> **Bridge.** The merge failed because the key is a location, and GeoPandas adds exactly one thing to a DataFrame to hold a location: a geometry column.

## 3.1 — One more column: the GeoDataFrame

```yaml
id: geo-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 3.2 — A GeoDataFrame

```yaml
id: geodataframe-table
origin: generated
layout: table-accented
time_s: 75
transition: cut
content:
  table:
    - [designacao, tipo, latitude, longitude, geometry]
    - ["101001", Escola Municipal, "-22.8970", "-43.1837", "POINT (-43.1837 -22.8970)"]
    - ["101601", Creche Municipal, "-22.8792", "-43.2243", "POINT (-43.2243 -22.8792)"]
    - ["101501", CIEP, "-22.8809", "-43.2253", "POINT (-43.2253 -22.8809)"]
  accent_cols: [5]
generated_hash: dc527935e2c0238b
```

**Claim.** A GeoDataFrame is the same DataFrame with one extra column, geometry, holding a shape per row.

**On slide.**
- The same table, plus one column: geometry

**Skip.** Lines and polygons in the geometry column. The bairros show polygons two beats later.

## 3.3 — Points from lat/lon

```yaml
id: geo-points
origin: generated
layout: claim-above-figure
time_s: 90
transition: cut
visual:
  kind: constructible
  intent: cell geo-points of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      xy = gpd.points_from_xy(escolas.longitude, escolas.latitude)
      pontos = gpd.GeoDataFrame(escolas, geometry=xy, crs=4326)
generated_hash: f431c8a26e41d2a9
```

**Claim.** Two columns of numbers become points with one call, longitude first because it is x, and crs=4326 says they are plain latitude and longitude.

**On slide.**
- lat/lon columns to points: x is longitude
- crs=4326: plain latitude and longitude

**Skip.** What a CRS is beyond "4326 means lat/lon". The backup beat holds the one thing worth knowing.

## 3.4 — Shapes from a file

```yaml
id: geo-read
origin: generated
layout: claim-above-figure
time_s: 60
transition: cut
visual:
  kind: constructible
  intent: cell geo-read of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      bairros = gpd.read_file("data/rio/bairros.geojson")
generated_hash: 149aab3d7d0bc6fc
```

**Claim.** Boundaries come from a file instead: read_file is read_csv for GeoJSON, shapefiles and GeoPackages, and returns 167 bairro polygons.

**On slide.**
- read_file: GeoJSON, shapefile, GeoPackage
- 167 bairro polygons

## 3.5 — plot()

```yaml
id: geo-plot
origin: generated
layout: full-bleed-figure
time_s: 75
transition: cut
visual:
  kind: constructible
  sub: geometry
  intent: schools as dots over the bairro outlines, and the two lines that draw it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/geo-folium/assets/built/schools_on_bairros.png
    intent: schools as dots over the bairro outlines; built by assets/verified_snippets.py
    code: |
      ax = bairros.plot(color="white", edgecolor="grey")
      pontos.plot(ax=ax, markersize=2)
generated_hash: 7f67ba033e2b616a
```

**Claim.** Two plot calls on one axis draw the polygons and the points together, which is the first map.

**Skip.** Basemaps and contextily. folium gives a real basemap in section 6.

## 3.6 — pandas still works

```yaml
id: geo-pandas-still-works
origin: generated
layout: claim-above-figure
time_s: 45
transition: cut
visual:
  kind: constructible
  intent: cell geo-pandas-still-works of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      creches = pontos[pontos["tipo"] == "Creche Municipal"]
      pontos.groupby("tipo").size()
generated_hash: b22357c7257056fd
```

**Claim.** Every pandas move from the recap runs unchanged on a GeoDataFrame, and a filtered GeoDataFrame keeps its geometry.

**On slide.**
- Same filter, same groupby, still geo

## 3.7 — Notebook, part 2

```yaml
id: act-geo-setup
origin: generated
layout: activity-setup
time_s: 120
transition: cut
content:
  task: >
    Turn the schools into a GeoDataFrame, read the bairros, and draw both on
    one map. Then look for a school that seems to be outside the city.
  example: |
    pontos.plot(ax=ax, markersize=2)
generated_hash: a6f0a98938d9b5fe
```

**Claim.** The second exercise builds the two GeoDataFrames the rest of the class uses and plants the outlier the spatial join will find.

## 3.8 — Part 2: GeoDataFrame

```yaml
id: act-geo-parking
origin: generated
layout: activity-parking
time_s: 1200
transition: cut
content:
  instructions: >
    Part 2. Build pontos from escolas with points_from_xy and crs=4326, read
    bairros.geojson, and plot the bairros with the schools on top. Plot only
    the CIEPs in a second figure. One school looks like it sits outside the
    city: which one?
  constraints:
    - 20 minutes
    - pairs welcome
    - solutions hidden under each exercise
generated_hash: e73b580886642b8b
```

**Claim.** Twenty minutes to get from a CSV to a first map with their own hands.

## 3.9 — Break

```yaml
id: break-1
origin: generated
layout: claim-only
time_s: 900
transition: cut
generated_hash: d767ac6feab22a04
```

**Claim.** Fifteen-minute break; leave the notebook open, part 3 starts from it.

# Section 4 — Merge by location

> **Bridge.** With schools and bairros both carrying geometry, the bairro column the merge was missing can be computed from where each school is: a merge whose key is location.

## 4.1 — Merge by location

```yaml
id: sjoin-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 4.2 — The spatial join

```yaml
id: sjoin-code
origin: generated
layout: claim-above-figure
time_s: 90
transition: cut
visual:
  kind: constructible
  intent: cell sjoin-code of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      com_bairro = gpd.sjoin(pontos, bairros, predicate="within")
      com_bairro[["denominacao", "nome", "regiao_adm"]].head()
generated_hash: b56bf60772a84899
```

**Claim.** sjoin is merge with location as the key: each school gets the columns of the bairro it falls within.

**On slide.**
- sjoin: merge, with location as the key
- Each school gets its bairro's columns

**Skip.** The other predicates (intersects, contains, touches). within is the one this class needs.

## 4.3 — What the join did

```yaml
id: sjoin-picture
origin: generated
layout: claim-above-figure
time_s: 60
transition: cut
visual:
  kind: constructible
  sub: geometry
  intent: Campo Grande filled, its 101 schools dark, neighbouring schools muted; built by assets/verified_snippets.py
  asset: sjoin_campo_grande.png
generated_hash: 5bed3b3c297fd062
```

**Claim.** The join is a point-in-polygon test for every school, and Campo Grande is the bairro that gets the most, 101.

**On slide.**
- Point in polygon: Campo Grande gets 101 schools

## 4.4 — Count per bairro

```yaml
id: sjoin-count
origin: generated
layout: claim-above-figure
time_s: 90
transition: cut
visual:
  kind: constructible
  intent: cell sjoin-count of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      n = com_bairro.groupby("codbairro").size()
      n = n.reset_index(name="n_escolas")
      bairros = bairros.merge(n, on="codbairro", how="left")
      bairros["n_escolas"] = bairros["n_escolas"].fillna(0)
generated_hash: 1121fbd0ad9441a8
```

**Claim.** Once each school has a bairro code, counting per bairro is the recap's groupby, and an ordinary merge puts the counts back on the polygons.

**On slide.**
- groupby on the new column, merge back onto the polygons
- how="left" keeps bairros with no school

## 4.5 — Schools per bairro

```yaml
id: sjoin-choropleth
origin: generated
layout: full-bleed-figure
time_s: 60
transition: cut
visual:
  kind: constructible
  sub: geometry
  intent: bairros shaded by school count, sand to green, and the one line that draws it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/geo-folium/assets/built/schools_per_bairro.png
    intent: bairros shaded by school count; built by assets/verified_snippets.py
    code: |
      bairros.plot(column="n_escolas", legend=True)
generated_hash: 2ae7f5ef8200191e
```

**Claim.** Plotting a column colours each polygon by it, and the counts are highest in the large western bairros.

**Skip.** Per-capita rates. The backup beat has the population merge if there is time.

## 4.6 — Three data warts

```yaml
id: data-warts
origin: generated
layout: build-list
time_s: 75
transition: cut
generated_hash: 9be320981ea4d3c4
```

**Claim.** Real data loses rows quietly: merge and sjoin are both inner by default, and left merges leave NaN where the other table has no row.

**On slide.**
- 1 school sits 1.7 km outside the city: sjoin drops it
- 1 school has CRE 12, missing from cre.csv: merge drops it
- 2 bairros have no Censo 2022 row: NaN after the merge
- Inner by default: check row counts after every join

## 4.7 — Per capita

```yaml
id: per-capita
origin: generated
layout: claim-above-figure
time_s: 60
transition: cut
backup: true
demoted_because: only feeds the folium choropleth, which is "If there is a enough time"
visual:
  kind: constructible
  intent: cell per-capita of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      pop = pd.read_csv("data/rio/populacao_bairros.csv")
      pop = pop[["codbairro", "populacao_2022"]]
      bairros = bairros.merge(pop, on="codbairro", how="left")
      taxa = bairros["n_escolas"] / bairros["populacao_2022"]
      bairros["por_10mil"] = taxa * 10_000
generated_hash: 630d71bf133a612f
```

**Note.** If there is a enough time

**Claim.** A rate per resident is a plain pandas merge onto the GeoDataFrame, joined on the bairro code because the two files spell one bairro's name differently.

**On slide.**
- Per 10,000 residents: one more ordinary merge
- Join on codbairro, not on the name

## 4.8 — Notebook, part 3

```yaml
id: act-sjoin-setup
origin: generated
layout: activity-setup
time_s: 120
transition: cut
content:
  task: >
    Join the schools to the bairros, count schools per bairro, and map the
    counts. Then find the school from part 2 that the join drops.
generated_hash: 9ea835a347ba9861
```

**Claim.** The third exercise is the spatial join end to end, ending on the outlier they spotted by eye.

## 4.9 — Part 3: spatial join

```yaml
id: act-sjoin-parking
origin: generated
layout: activity-parking
time_s: 1200
transition: cut
content:
  instructions: >
    Part 3. sjoin pontos to bairros with predicate="within", count schools per
    bairro, merge the counts onto bairros and plot them. Which bairro has the
    most schools, and which school is missing from the join? Stretch: merge
    populacao_bairros.csv and map schools per 10,000 residents.
  constraints:
    - 20 minutes
    - pairs welcome
    - solutions hidden under each exercise
generated_hash: ce2a6c35f200fa1c
```

**Claim.** Twenty minutes on the one genuinely new operation of the class.

# Section 5 — What area do the points cover?

> **Bridge.** Once every point carries a location the opening question can be asked properly, and the answer turns out to depend on the shape chosen to wrap the points.

## 5.1 — What area do the points cover?

```yaml
id: area-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 5.2 — 166 schools

```yaml
id: cre4-points
origin: generated
layout: full-bleed-figure
time_s: 60
transition: cut
visual:
  kind: constructible
  sub: geometry
  intent: the 166 schools of the 4th CRE over the bairro outlines, and the two lines that select them and fuse them into one shape
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/geo-folium/assets/built/cre4_points.png
    intent: the 166 schools of the 4th CRE over the bairro outlines; built by assets/verified_snippets.py
    code: |
      sel = pontos[pontos["cre"] == 4]
      pts = sel.union_all()
generated_hash: 5cc96915588e773f
```

**Claim.** One regional education office's 166 schools, fused into a single multipoint shape, are the set the question is asked about.

**Skip.** Why the 4th CRE. Any set works; this one crosses the bay, which makes the shapes disagree visibly.

## 5.3 — Draw the area

```yaml
id: area-discussion
origin: generated
layout: discussion
time_s: 150
transition: cut
generated_hash: 23f06b3a5cd20327
```

**Claim.** If you had to draw the area these 166 schools cover, what shape would you draw, and what would it take in that it should not?

## 5.4 — Convex hull

```yaml
id: cre4-hull
origin: generated
layout: full-bleed-figure
time_s: 60
transition: cut
visual:
  kind: constructible
  sub: geometry
  intent: the convex hull around the 166 schools, in green, and the one line that computes it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/geo-folium/assets/built/cre4_hull.png
    intent: the convex hull around the 166 schools; built by assets/verified_snippets.py
    code: |
      hull = pts.convex_hull
generated_hash: 4645a67a7ab61b66
```

**Note.** just saying that a lib has functions that implements the poly algo and the min circle is good enough and we will take from that

**Claim.** The convex hull is the tightest convex polygon around the points, and the library computes it in one line.

**Skip.** How the hull is computed (Graham scan and friends). Out of scope by the brief.

## 5.5 — Minimal circle

```yaml
id: cre4-circle
origin: generated
layout: full-bleed-figure
time_s: 60
transition: cut
visual:
  kind: constructible
  sub: geometry
  intent: the smallest circle containing the 166 schools, in green, and the one line that computes it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/geo-folium/assets/built/cre4_circle.png
    intent: the minimal enclosing circle around the 166 schools; built by assets/verified_snippets.py
    code: |
      circle = shapely.minimum_bounding_circle(pts)
generated_hash: 2b6baa4408494a57
```

**Note.** just saying that a lib has functions that implements the poly algo and the min circle is good enough and we will take from that

**Claim.** The minimal circle is the smallest circle containing every point, and it is also one library call.

**Skip.** Welzl's algorithm. Out of scope by the brief.

## 5.6 — Centroid

```yaml
id: cre4-centroid
origin: generated
layout: full-bleed-figure
time_s: 45
transition: cut
visual:
  kind: constructible
  sub: geometry
  intent: the centroid of the 166 schools marked with a cross, and the one line that computes it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/geo-folium/assets/built/cre4_centroid.png
    intent: the centroid of the 166 schools, marked; built by assets/verified_snippets.py
    code: |
      centro = pts.centroid
generated_hash: 686243786460fc36
```

**Claim.** The centroid is the average position of the points, one attribute away, and it is where a single label or marker for the set goes.

**Skip.** The warning `bairros.centroid` prints in the notebook. The CRS backup beat explains it if someone asks.

## 5.7 — Same points, two answers

```yaml
id: hull-vs-circle
origin: generated
layout: claim-above-figure
time_s: 90
transition: cut
visual:
  kind: constructible
  sub: geometry
  intent: hull (green, the first shape) and circle (yellow, the second) over the same 166 schools; built by assets/verified_snippets.py
  asset: cre4_hull_vs_circle.png
generated_hash: 0f9511558627b39b
```

**Claim.** The same 166 schools cover 42 km² as a hull and 120 km² as a circle, so the area is a choice of shape, not a property of the points.

**On slide.**
- Same 166 schools: hull 42 km², circle 120 km²
- The area depends on the shape you choose

**Skip.** Concave hulls and buffers. Out of scope by the brief.

## 5.8 — Degrees are not metres

```yaml
id: crs-degrees
origin: generated
layout: claim-above-figure
time_s: 60
transition: cut
backup: true
demoted_because: user hasn't confirmed CRS is in scope
visual:
  kind: constructible
  intent: cell crs-degrees of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      pts_m = sel.to_crs(31983).union_all()  # UTM 23S, metres
      hull_km2 = pts_m.convex_hull.area / 1e6
      circ_m = shapely.minimum_bounding_circle(pts_m)
      circle_km2 = circ_m.area / 1e6
      centros = bairros.to_crs(31983).centroid.to_crs(4326)
generated_hash: 543cd609e7bc46c8
```

**Claim.** Latitude and longitude are degrees, not metres, so areas, distances and polygon centroids need to_crs to a metric CRS first, which is also what the centroid warning is about.

**On slide.**
- lat/lon are degrees, not metres
- .to_crs() before measuring

**Skip.** Projections, datums, EPSG codes beyond 4326 and 31983.

## 5.9 — Notebook, part 4

```yaml
id: act-area-setup
origin: generated
layout: activity-setup
time_s: 120
transition: cut
content:
  task: >
    Pick another CRE or one school type, wrap its schools in a hull and a
    circle, find the centroid, and plot all three over the points.
  example: |
    hull = pts.convex_hull
generated_hash: 52309f4079fdf897
```

**Claim.** The fourth exercise repeats the turn on a set of their own choosing, so the shape argument is theirs rather than the slide's.

## 5.10 — Part 4: shapes

```yaml
id: act-area-parking
origin: generated
layout: activity-parking
time_s: 1200
transition: cut
content:
  instructions: >
    Part 4. Choose a CRE or a school type. Compute the convex hull, the
    minimal circle and the centroid, and plot them over the points. Which
    shape would you report as "the area these schools cover", and why?
  constraints:
    - 20 minutes
    - pairs welcome
    - one plot per pair
generated_hash: 92d2efa0a518c7ad
```

**Claim.** Twenty minutes, ending with one plot per pair that the debrief can compare.

## 5.11 — Break

```yaml
id: break-2
origin: generated
layout: claim-only
time_s: 900
transition: cut
generated_hash: c20544c07b49aa8f
```

**Claim.** Fifteen-minute break; keep your hull and circle, part 5 puts them on a map.

# Section 6 — A map people can click

> **Bridge.** The answers so far are static plots; folium puts the same points and shapes on a map people can pan, zoom and click, which is the shareable form of everything before it.

## 6.1 — A map people can click

```yaml
id: folium-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 6.2 — A map

```yaml
id: folium-map
origin: generated
layout: claim-above-figure
time_s: 60
transition: cut
visual:
  kind: constructible
  intent: cell folium-map of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      m = folium.Map(location=[-22.91, -43.45], zoom_start=11)
generated_hash: 466447b0eb2749a2
```

**Claim.** A folium map is one object centred on a latitude and longitude, and in a notebook it renders as a live map you can pan and zoom.

**On slide.**
- One object: centre, zoom, a live basemap
- folium wants [lat, lon]: y first

**Skip.** Tile providers. The default OpenStreetMap tiles need no key; CartoDB's now ask for one.

## 6.3 — Markers and popups

```yaml
id: folium-markers
origin: generated
layout: claim-above-figure
time_s: 75
transition: cut
visual:
  kind: constructible
  intent: cell folium-markers of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      cieps = escolas[escolas["tipo"] == "CIEP"]
      for _, row in cieps.iterrows():
          folium.Marker(
              [row["latitude"], row["longitude"]],
              popup=folium.Popup(row["denominacao"]),
          ).add_to(m)
generated_hash: 9f20d1a1ff411c8b
```

**Claim.** A marker is a point with a popup, added to the map one row at a time, which is fine for the 101 CIEPs.

**On slide.**
- One Marker per row, a Popup with the name

## 6.4 — 101 markers

```yaml
id: folium-markers-shot
origin: generated
layout: claim-above-figure
time_s: 45
transition: cut
visual:
  kind: referential
  sub: screenshot
  intent: the 101 CIEP markers on an OpenStreetMap basemap of the city, one popup open; headless-Chrome screenshot of a folium map built by assets/screenshot_maps.py
  asset: folium_markers.png
  attribution: "Map © OpenStreetMap contributors · Data: DATA.RIO, CC BY 4.0"
generated_hash: ae98e5391400d5da
```

**Claim.** A hundred markers are readable and clickable.

**On slide.**
- 101 CIEPs, one popup open

## 6.5 — MarkerCluster

```yaml
id: folium-cluster
origin: generated
layout: claim-above-figure
time_s: 75
transition: cut
visual:
  kind: constructible
  intent: cell folium-cluster of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      cluster = plugins.MarkerCluster(name="schools")
      cluster.add_to(m)
      for _, row in escolas.iterrows():
          folium.Marker(
              [row["latitude"], row["longitude"]],
              popup=row["denominacao"],
          ).add_to(cluster)
generated_hash: 19d8cc23f140b6c2
```

**Claim.** Fifteen hundred markers are not readable, and a MarkerCluster groups them into counts that split as you zoom in.

**On slide.**
- 1,590 markers: add them to a cluster, not the map

## 6.6 — Clusters

```yaml
id: folium-cluster-shot
origin: generated
layout: claim-above-figure
time_s: 45
transition: cut
visual:
  kind: referential
  sub: screenshot
  intent: all 1,590 schools in a MarkerCluster at city zoom, as numbered cluster bubbles; headless-Chrome screenshot of a folium map built by assets/screenshot_maps.py
  asset: folium_cluster.png
  attribution: "Map © OpenStreetMap contributors · Data: DATA.RIO, CC BY 4.0"
generated_hash: 5f2fb6e563361c24
```

**Claim.** The cluster layer shows counts at city zoom and individual schools up close.

**On slide.**
- Counts at city zoom, schools up close

## 6.7 — HeatMap

```yaml
id: folium-heatmap
origin: generated
layout: claim-above-figure
time_s: 45
transition: cut
visual:
  kind: constructible
  intent: cell folium-heatmap of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      coords = escolas[["latitude", "longitude"]].values.tolist()
      plugins.HeatMap(coords, name="heat", radius=12).add_to(m)
generated_hash: 906eae275d14c927
```

**Claim.** A heatmap takes a plain list of [lat, lon] pairs and shows density instead of individual points.

**On slide.**
- A list of [lat, lon] pairs in, density out

## 6.8 — Density

```yaml
id: folium-heatmap-shot
origin: generated
layout: claim-above-figure
time_s: 45
transition: cut
visual:
  kind: referential
  sub: screenshot
  intent: the HeatMap of all schools at city zoom, no markers; headless-Chrome screenshot of a folium map built by assets/screenshot_maps.py
  asset: folium_heatmap.png
  attribution: "Map © OpenStreetMap contributors · Data: DATA.RIO, CC BY 4.0"
generated_hash: f0097e76bb7d3df1
```

**Claim.** The heat layer shows where schools concentrate without a single marker on screen.

**On slide.**
- Where schools concentrate, no markers

## 6.9 — Drawing the shapes

```yaml
id: folium-shapes
origin: generated
layout: claim-above-figure
time_s: 60
transition: cut
visual:
  kind: constructible
  intent: cell folium-shapes of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      folium.GeoJson(hull, name="convex hull").add_to(m)
      folium.GeoJson(circle, name="minimal circle").add_to(m)
      folium.Marker([centro.y, centro.x]).add_to(m)
generated_hash: 0314ca13535506f0
```

**Claim.** The hull and circle from section 5 go onto the map with GeoJson, and the centroid becomes a marker, y first.

**On slide.**
- Any shapely shape: folium.GeoJson
- A point as a marker: [y, x]

## 6.10 — The answer, on a map

```yaml
id: folium-shapes-shot
origin: generated
layout: claim-above-figure
time_s: 60
transition: cut
visual:
  kind: referential
  sub: screenshot
  intent: the 4th CRE's convex hull, minimal circle and centroid marker over the basemap; headless-Chrome screenshot of a folium map built by assets/screenshot_maps.py
  asset: folium_shapes.png
  attribution: "Map © OpenStreetMap contributors · Data: DATA.RIO, CC BY 4.0"
generated_hash: c028247e4081a6a5
```

**Claim.** The opening question's two answers now sit on a map anyone can pan, zoom and click.

**On slide.**
- Hull, circle and centroid on a live map

## 6.11 — Choropleth

```yaml
id: folium-choropleth
origin: generated
layout: claim-above-figure
time_s: 75
transition: cut
backup: true
demoted_because: If there is a enough time
visual:
  kind: constructible
  intent: cell folium-choropleth of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      folium.Choropleth(
          geo_data=bairros,
          data=bairros,
          columns=["codbairro", "por_10mil"],
          key_on="feature.properties.codbairro",
          fill_color="YlGn",
          nan_fill_color="lightgrey",
          legend_name="schools per 10,000 residents",
      ).add_to(m)
generated_hash: 2843344550cb8eb3
```

**Note.** If there is a enough time

**Claim.** A choropleth colours each bairro by a column, matched to the polygons through a key, and greys out the two bairros with no population figure.

**On slide.**
- Colour each bairro by a column
- key_on matches rows to polygons

## 6.12 — Layer control

```yaml
id: folium-layers
origin: generated
layout: claim-above-figure
time_s: 45
transition: cut
backup: true
demoted_because: If there is a enough time
visual:
  kind: constructible
  intent: cell folium-layers of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      folium.LayerControl().add_to(m)
generated_hash: 06b6478f3507244f
```

**Note.** If there is a enough time

**Claim.** A layer control lists every named layer so the viewer can switch markers, clusters, heat and shapes on and off.

**On slide.**
- Switch layers on and off: name= shows here

## 6.13 — One HTML file

```yaml
id: folium-save
origin: generated
layout: claim-above-figure
time_s: 45
transition: cut
visual:
  kind: constructible
  intent: cell folium-save of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      m.save("map.html")
generated_hash: f29ac0bfbaca793a
```

**Claim.** The finished map saves as one HTML file that opens in any browser with no Python, which is what makes it shareable.

**On slide.**
- One file, any browser, no Python

## 6.14 — Notebook, part 5

```yaml
id: act-folium-setup
origin: generated
layout: activity-setup
time_s: 120
transition: cut
content:
  task: >
    Build one map with everything: markers for a subset, every school in a
    cluster, a heat layer, and your shapes from part 4. Save it as one file.
  example: |
    m.save("map.html")
generated_hash: 3987b85acb6c56c0
```

**Claim.** The last exercise assembles the whole class into one map, with the extras as a stretch.

## 6.15 — Part 5: the map

```yaml
id: act-folium-parking
origin: generated
layout: activity-parking
time_s: 1800
transition: cut
content:
  instructions: >
    Part 5. On one folium map: markers with popups for a subset you choose,
    every school in a MarkerCluster, a HeatMap, and the hull, circle and
    centroid from part 4; then save it with m.save("map.html") and open the
    file in a browser. Stretch: a choropleth of schools per 10,000 residents
    and a LayerControl.
  constraints:
    - 30 minutes
    - pairs welcome
    - show your map
generated_hash: 6768c73d9db3da0b
```

**Claim.** Thirty minutes to build the map the class has been heading towards.

# Section 7 — From coordinates to a map

> **Bridge.** Each block added one step; laid end to end they are the whole path from a CSV of coordinates to a map someone else can open.

## 7.1 — The whole path

```yaml
id: path-recap
origin: generated
layout: claim-above-figure
time_s: 75
transition: cut
visual:
  kind: constructible
  sub: process
  intent: the five steps of the class as one pipeline, revealed left to right
  graph:
    rankdir: LR
    nodes:
      - {id: csv, label: "CSV: lat, lon"}
      - {id: gdf, label: GeoDataFrame}
      - {id: sjoin, label: sjoin}
      - {id: shapes, label: "hull, circle"}
      - {id: map, label: folium map}
    edges:
      - {from: csv, to: gdf}
      - {from: gdf, to: sjoin}
      - {from: sjoin, to: shapes}
      - {from: shapes, to: map}
generated_hash: ff77b79f29148290
```

**Claim.** The class was one pipeline: coordinates become a GeoDataFrame, location becomes a join key, points become shapes, and all of it becomes a map.

**On slide.**
- From raw coordinates to an interactive map

## 7.2 — The one idea

```yaml
id: closing-callout
origin: generated
layout: callout
time_s: 45
transition: cut
generated_hash: a638d16fe906f38e
```

**Claim.** A GeoDataFrame is a DataFrame with a geometry column; everything else today was pandas you knew and one-line library calls.

## 7.3 — Your own points

```yaml
id: closing-discussion
origin: generated
layout: discussion
time_s: 180
transition: cut
generated_hash: d29ee06fceffc3c8
```

**Claim.** Which data you already work with has coordinates in it, and what question would a map of it answer?
