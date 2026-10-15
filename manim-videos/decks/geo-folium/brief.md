---
slug: geo-folium
title: Points on a map
target: manim
genre: lecture
technicality: 2
interaction: structured
duration_min: 240
audience: Administrative police officers who know Python, pandas and machine-learning algorithms; new to geopandas and folium
narrative_frozen: false
---

## Narrative
They arrive knowing pandas. A GeoDataFrame is a DataFrame with one extra column, so everything starts from what they know.
Here are N points on a map of Rio: what area do they cover? The answer depends on the shape you choose, a hull or a circle, and the library already implements each one in one line.
They leave able to go from raw coordinates to a shareable interactive map.

## Why I'm presenting
A class on folium and geopandas for the same group as the datavis classes. The presenter's focus: "I want to focus more on folium and geopandas for those classes". Taking a set of points and drawing a minimal circle or a polygon around them is shown only as library calls: "just saying that a lib has functions that implements the poly algo and the min circle is good enough".

## What the audience should do
- load spatial data (GeoJSON / shapefile, or lat/lon columns) into GeoPandas
- make an interactive map with Folium (markers, clusters, choropleth, heatmap)
- wrap a set of points in a shape by calling the library (convex hull, minimal circle), with no algorithm details

## Series
Follows the datavis classes (deck datavis-2), same audience. Opens with a pandas recap used as the basis of comparison for GeoPandas ("start by recap about pandas and use it as basis of comparison for it").
Data: "Anything Rio related is good." The presenter has access to a crimes API that may provide the point data; the class is not about police work.
Format: a 4-hour class. Lecture blocks on these slides alternate with hands-on work in a companion notebook (exercise + solution), with breaks.
Operations: "just the simple ones we talked about": points from lat/lon, reading boundaries, plotting, point-in-polygon (spatial join, the geo version of merge), convex hull, minimal circle, centroid. Folium extras (choropleth, layer control, HTML export) only "If there is a enough time".

## Out of scope
- how the algorithms work (Welzl, Graham scan, Delaunay); the geometry notebooks CirculoMinimo, Delaunay, polygon_analysis and TrianPoly are too advanced for this audience
- CRS and projection theory; at most one beat: lat/lon are degrees, not metres
- concave hull, Voronoi, overlay, dissolve
- political examples
