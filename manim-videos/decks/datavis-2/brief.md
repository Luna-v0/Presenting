---
slug: datavis-2
title: Honest charts
target: manim
genre: lecture
technicality: 2
interaction: structured
duration_min: 240
audience: Administrative police officers who know Python and machine-learning algorithms; they had one short seaborn class before
narrative_frozen: false
---

## Narrative
They arrive able to make a chart with seaborn (the first class), and they trust charts.
The turn: a chart can be technically correct and still fool you. The same data drawn two ways tells two different stories, and there is no single correct chart for every question.
They leave able to spot a misleading chart, draw a clear and honest one, and reach for a few chart types beyond bar and line when a question needs them.

## Why I'm presenting
The second datavis class for this group. The first was a very small seaborn class; this one increments it: the best ways to make charts, some more interesting charts, and "how to lie with statistics" with misleading charts.

## What the audience should do
- choose a chart for a question, with the nuance in the presenter's words: "there is a little bit of nuance to a, because there is no correct chart for every case and to have a toolbox is okay but I dont want to over do it too"
- make a chart that's clear and honest (labels, colour, annotation, a title that states the takeaway)
- spot and explain a misleading chart
- know a small toolbox of more interesting charts and when each helps

## Series
Part 2 of the datavis classes. Part 1 was the notebook data_vis.ipynb in ds_be_like (seaborn: line, bar, heatmap, scatter with hue, regplot, lmplot, swarm, KDE, jointplot, histplot); don't re-teach those. The same group also gets the folium + geopandas class (deck geo-folium).
Format: a 4-hour class. Lecture blocks on these slides alternate with hands-on work in a companion notebook (exercise + solution), with breaks. One "fix this chart" exercise in pairs (~10 min).
Pending: which toolbox charts and which misleading-chart tricks go in; the presenter picks from decks/datavis-2/gallery/.

## Out of scope
- the Digimon dataset from part 1 ("ignore completely the digimon dataset choose anything else")
- plotly, Altair, or any interactive charting library ("I dont really want to go into ploly or altair")
- political examples ("nothing political please"); real examples are redrawn from data, with sources cited
- data storytelling as a topic of its own ("I dont want to go into a "nerrative" of the charts but I want to tell it")
- police-work framing; crime data may appear as a dataset, but the class isn't about police work
