# Questions for the two class decks: datavis (part 2) and folium + geopandas

Answer under each `> ` line. Where my **default** is fine, just write `ok`. Skip anything you don't care about; I'll take the default.
Questions are ordered by how much each answer unblocks: section 0 first.

What I found already:
- **Previous datavis class:** `/mnt/nas/Data_Science_be_like/code/notebooks/data_vis.ipynb`, a seaborn tour on a Digimon dataset (line, bar, heatmap, scatter + hue, regplot, lmplot, swarm, KDE, jointplot, histplot). I did **not** find slides for it anywhere (see Q-D1).
- **Geo class (your note):** the geometry notebooks are too advanced and won't be used. The polygon and minimal-circle algorithms get one slide: "the library already implements these" (`.convex_hull`, `.concave_hull()`, `shapely.minimum_bounding_circle`). The class time goes to folium and geopandas.
- **Rendering:** the `presenting-manim` MCP server failed to connect in this session, so animated (manim) decks can't render until it's back. A plain slides deck (`.pptx`) doesn't need it.

---

## 0. Both classes (answer these first)

**Q0.1 Who is the audience?** Course or event, level, how many people, and do they already know pandas?
Default: the same group as the first datavis class (Data Science be like); knows basic Python + pandas, not geopandas.
> Administrative Policeman that knows python and machine learning algorithm, no need to focus on police work based but we could use the api I got about crimes 

**Q0.2 Language** for the slides, and for what you'll say?
Default: Portuguese slides and speech, with English kept for library and function names.
> It can be in english 

**Q0.3 Duration and date** of each class?
Default: ~60–90 min each.
> Each class are 4 hours long but I need to have some gaps and exercices

**Q0.4 Format** (this decides a lot):
- (a) an animated HTML deck (manim; great for algorithm animations like the minimal circle, but needs the MCP back);
- (b) a classic slide deck (`.pptx`);
- (c) slides + a companion notebook you live-code from.

Default: (c), slides plus a notebook, for both. For the geo class, a couple of animated algorithm clips if manim is available. 
> a and c. Slides on manim and a notebook.

**Q0.5 Style:** a `tutorial` (hands-on, exercises during the class) or a `lecture` (you explain, with discussion)?
Default: tutorial, with 1–2 short exercises each.
> The slide is a lecture and then we get hands on (that is more like a tutorial)

**Q0.6 Should both decks share a visual identity** with your earlier decks (`Presenting/manim-videos/identity/`)?
Default: yes.
> Not necessarially 

**Q0.7 Companion material:** should I also produce an exercise notebook + a solution notebook per class (in `Data_Science_be_like/code/notebooks/`)?
Default: yes.
> Yes. And for geopandas I think you could start by recap about pandas and use it as basis of comparison for it. 

---

## D. Datavis, part 2

**Q-D1 What exactly did the first class cover?** Just the Digimon notebook, or were there slides somewhere (Drive, PDF)? If there were slides, where are they?
> 

**Q-D2 What should students be able to DO after this class?** Pick and edit:
- (a) choose the right chart for a question; 
- (b) make a chart that's clear and honest (labels, colour, annotation, a title that states the takeaway);
- (c) spot and explain a misleading chart;
- (d) know a toolbox of "more interesting" charts and when each helps.

Default: all four, with (b) and (c) as the core.
> all, but there is a little bit of nuance to a, because there is no correct chart for every case and to have a toolbox is okay but I dont want to over do it too. 

**Q-D3 The story.** My proposed narrative, to accept or change:
- **Setup:** "You already know how to make a chart (last class)."
- **Turn:** "The same data can tell three different stories: one misleading, one technically correct but useless, one that makes the point instantly."
- **Landing:** "You leave with a checklist for honest, effective charts, and a set of chart types beyond bar and line."

The "how to lie" part is the turn: the class opens with a chart that fools them.
> I dont want to go into a "nerrative" of the charts but I want to tell it 

**Q-D4 Dataset:** reuse the Digimon data (continuity, already familiar), or something closer to their world (Brazilian public data, sports, their own course data)?
Default: Digimon for continuity, plus one real-world dataset for the "lying" examples, because misleading charts land harder on real topics.
> No ignore completely the digimon dataset choose anything else. 

**Q-D5 Tools:** seaborn/matplotlib only, or also an interactive library (plotly or Altair)?
Default: seaborn/matplotlib, plus one plotly slide to show interactivity.
> I dont really want to go into ploly or altair. 

**Q-D6 Which "more interesting" charts?** Keep or remove (my picks marked ★):
- ★ small multiples
- ★ violin/raincloud
- ★ ECDF
- ★ slope chart
- ★ dumbbell
- ★ ridgeline
- ★ hexbin/2D density (for overplotting)
- bump chart
- waffle
- treemap
- sankey
- parallel coordinates
- calendar heatmap
- lollipop
- annotated time series
> I dont know them by name, not all at least, you will need to provide me a grid of samples for each chart. 

**Q-D7 Which principles?** Default: chart choice by question, Cleveland's perceptual ranking (position > length > angle > area > colour), data-ink and declutter, colour (sequential/diverging/qualitative, colour-blind safe), annotation, takeaway titles, sorting, aspect ratio. Too many? Add or cut:
> I think I will need to show 

**Q-D8 "How to lie with statistics": which tricks?** Keep or remove (★ = my picks):
- ★ truncated y-axis
- ★ dual axes
- ★ area/pictogram scaling
- ★ cherry-picked time window
- ★ cumulative vs per-period
- ★ 3D pie
- ★ mean vs median (skew)
- ★ Simpson's paradox
- ★ correlation ≠ causation (spurious correlations)
- survivorship bias
- base-rate neglect
- misleading colour scales
- log scale without saying so
- binning tricks in histograms
> I will also need a description of those 

**Q-D9 Real examples of bad charts?** Recreating real news/politics charts lands well but needs care (I'd redraw them from the data, not copy images). Do you want real-world examples, Brazilian ones in particular, or only synthetic?
Default: 2–3 real ones, redrawn, with sources cited.
> Yeah, nothing political please 

**Q-D10 Exercise:** "fix this chart" (they get a bad chart + data and redesign it), done in pairs?
Default: yes, ~10 min.
> Yeah

---

## G. Folium + GeoPandas

**Q-G1 What should students be able to DO afterwards?** Pick and edit:
- (a) load spatial data (GeoJSON/shapefile) into GeoPandas;
- (b) understand CRS/projections well enough to measure distances and areas correctly;
- (c) do spatial operations (spatial join, buffer, point-in-polygon);
- (d) make an interactive map with Folium (markers, clusters, choropleth, heatmap);
- (e) wrap a set of points in a shape by calling the library (convex hull, minimal circle), with no algorithm details.

Default: all five, with (c) and (d) as the core and (e) as a short payoff near the end.
> I dont even understand the b. I think it is more about a,d and e. 

**Q-G2 The story.** Proposed:
- **Setup:** "Here are N points on a map (e.g. schools, bus stops, deliveries)."
- **Turn:** "What 'area' do they cover? The answer depends on the shape you choose (hull, circle, buffer union) and on the projection, and the naive way gives wrong distances."
- **Landing:** "You can go from raw coordinates to correct measurements and a shareable interactive map."

Accept or change:
> Ok

**Q-G3 Dataset/use case.** Rio de Janeiro / Brazil (IBGE boundaries + some point set, e.g. schools, bus stops, PUC-Rio surroundings)? Or something you already use at work?
Default: Rio (IBGE municipal and neighbourhood boundaries + a public point dataset).
> Anything Rio related is good. 

**Q-G4 (settled by your note):** the algorithms are not explained, only called from the library: one picture of the points, the hull and the circle, and one line of code each. Nothing to answer unless you want a 10-second intuition ("rubber band" for the hull).
> 

**Q-G5 Which shapes and operations?** Keep or remove:
- ★ convex hull (library call)
- ★ minimal enclosing circle (library call)
- concave hull (library call)
- ★ buffer + union ("the area within 500 m of any point")
- ★ spatial join / point-in-polygon ("which neighbourhood is each point in")
- ★ dissolve / groupby on geometry
- ★ area and distance in metres (reproject first; show the wrong answer in degrees)
- ★ centroid
- clip / overlay (intersection of two layers)
- Voronoi (nearest-facility areas, library call)
- reading from shapefile / GeoJSON / GeoPackage, and the geobr package for Brazilian boundaries
> just the simple ones we talked about 

**Q-G6 Folium features:** markers + popups, MarkerCluster, choropleth, HeatMap, drawing the computed shapes, layer control, exporting to HTML?
Default: all of them, ending with one shareable HTML map.
> If there is a enough time

**Q-G7 Anything else from your work** ("I will probably have to talk about…")? If there's a concrete task you need to teach for (a client question, a dataset), describe it; the class can be built around it.
> 

---

## Anything else?
> 
