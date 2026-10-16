---
slug: datavis-2
title: Honest charts
subtitle: "Data visualisation, part 2: eight habits, a small toolbox, and how charts lie"
author: Eduardo Dantas Luna
date: "2026"
target: manim
duration_min: 240
brief: ./brief.md
---

# Section 1 — A chart that fools you

> **Bridge.** Opening frame: they trust charts, so the class opens on a chart that is correct in every number and still points them to the worse treatment.

## 1.1 — Honest charts

```yaml
id: title
origin: generated
layout: title-card
time_s: 20
transition: cut
generated_hash: 1bba1dd11dd07a2c
```

## 1.2 — Which treatment works better?

```yaml
id: opening-chart
origin: generated
layout: claim-above-figure
time_s: 75
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: success rate of open surgery against PCNL over all 700 kidney-stone patients, 78% and 83%; built by assets/verified_snippets.py
  asset: opening-chart.png
  attribution: "Data: Charig et al. (1986), BMJ 292:879"
generated_hash: 05bd98b73229b2a4
```

**Note.** nothing political please

**Claim.** Over all 700 kidney-stone patients, the keyhole procedure (PCNL) succeeded more often than open surgery, 83% against 78%.

**On slide.**
- Kidney stones: 700 patients, two treatments

**Skip.** What PCNL involves beyond "keyhole surgery". The medicine is not the point.

## 1.3 — Your call

```yaml
id: opening-vote
origin: generated
layout: discussion
time_s: 120
transition: cut
generated_hash: 950cbaf81b3146a3
```

**Claim.** Which treatment would you choose for yourself, and what would make you change your mind?

## 1.4 — Split by stone size

```yaml
id: opening-split
origin: generated
layout: claim-above-figure
time_s: 90
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: the same success rates split into small and large stones, open surgery (green, first) beside PCNL (yellow, second), open surgery higher in both; built by assets/verified_snippets.py
  asset: opening-split.png
  attribution: "Data: Charig et al. (1986), BMJ 292:879"
generated_hash: 4ddc22ae4d21ed47
```

**Claim.** Split by stone size, open surgery has the higher success rate for small stones and for large stones, so the pooled chart pointed the wrong way.

**On slide.**
- Open surgery wins for small stones and for large stones

## 1.5 — Who got which treatment

```yaml
id: opening-why
origin: generated
layout: table-accented
time_s: 90
transition: cut
content:
  table:
    - [stones, open surgery, PCNL]
    - [small, "81 / 87 (93%)", "234 / 270 (87%)"]
    - [large, "192 / 263 (73%)", "55 / 80 (69%)"]
    - [all, "273 / 350 (78%)", "289 / 350 (83%)"]
  accent_rows: [2]
generated_hash: f1f5c8e0eceebd4b
```

**Claim.** PCNL was given mostly to small stones, which do better under any treatment, so pooling hands PCNL the easy cases.

**On slide.**
- PCNL got mostly small stones, the easy cases

**Skip.** Why the doctors chose that way. The data does not say, and the point holds either way.

## 1.6 — Correct and still wrong

```yaml
id: opening-turn
origin: generated
layout: callout
time_s: 45
transition: cut
generated_hash: f05af3380bf9d954
```

**Claim.** Every number on both charts is correct. A chart can be accurate and still point you the wrong way; this one is called Simpson's paradox.

## 1.7 — Today

```yaml
id: todays-path
origin: generated
layout: build-list
time_s: 60
transition: cut
generated_hash: c639d9353e9eeaea
```

**Note.** I dont want to go into a "nerrative" of the charts but I want to tell it

**Claim.** The class runs from habits to a toolbox to the tricks, with the notebook after each lecture block and two breaks.

**On slide.**
- Eight habits of an honest chart
- Notebook part 1, then a break
- A small toolbox: which chart for which question
- Notebook part 2, then a break
- How charts lie, and the question that catches each trick
- Fix this chart, in pairs
- A checklist to keep

# Section 2 — Eight habits of an honest chart

> **Bridge.** If an accurate chart can point the wrong way, the first defence is drawing charts that make the right reading the easy one, and eight habits do most of that work.

## 2.1 — Eight habits of an honest chart

```yaml
id: habits-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 2.2 — Choose the chart by the question

```yaml
id: b1-question
origin: generated
layout: two-up-compare
time_s: 90
transition: cut
content:
  label_l: "Before: a line joins the species"
  label_r: "After: one bar per species"
  panel_l:
    kind: constructible
    sub: axes
    intent: mean body mass of the three penguin species drawn as a connected line; built by assets/verified_snippets.py
    asset: b1-question-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: the same three means as bars from zero; built by assets/verified_snippets.py
    asset: b1-question-r.png
generated_hash: 8b3be8c2ce140644
```

**Claim.** A line says its points are ordered and connected, which species are not; asking which species is heaviest is a question for bars.

**Skip.** Dot plots. A bar is enough here.

## 2.3 — Position beats angle

```yaml
id: b2-position
origin: generated
layout: two-up-compare
time_s: 120
transition: cut
content:
  label_l: "Before: rank the slices"
  label_r: "After: rank the bars"
  panel_l:
    kind: constructible
    sub: axes
    intent: a seven-slice pie of diamonds by colour grade D to J, no percentages; built by assets/verified_snippets.py
    asset: b2-position-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: the same seven shares as horizontal bars in grade order; built by assets/verified_snippets.py
    asset: b2-position-r.png
generated_hash: 414d1867faf55338
```

**Claim.** People compare positions on a common scale far more accurately than angles or areas: in the pie G, E and F look alike, and as bars G is plainly the largest.

**Skip.** The full Cleveland and McGill ranking of length, angle, area and colour. Position first is all the class needs.

## 2.4 — Every mark should carry data

```yaml
id: b3-data-ink
origin: generated
layout: two-up-compare
time_s: 90
transition: cut
content:
  label_l: "Before: grid, frame, hatching"
  label_r: "After: only marks that carry data"
  panel_l:
    kind: constructible
    sub: axes
    intent: six US states by drivers in fatal crashes, with a heavy grid, a full frame, hatched bars and a one-entry legend; built by assets/verified_snippets.py
    asset: b3-data-ink-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: the same six bars with nothing but the bars and the axes; built by assets/verified_snippets.py
    asset: b3-data-ink-r.png
generated_hash: ea1eb7d6bb65d344
```

**Claim.** Heavy grids, frames, hatching and a legend for a single series are ink the reader has to look past; take them away and the bars are the chart.

**Skip.** Tufte's data-ink ratio as a number.

## 2.5 — Colour that follows the data

```yaml
id: b4-colour
origin: generated
layout: two-up-compare
time_s: 105
transition: cut
visual:
  kind: referential
  sub: paper-figure
  intent: both panels show real colour maps (jet, viridis), off the deck palette on purpose; built by assets/verified_snippets.py
  asset: b4-colour-r.png
content:
  label_l: "Before: rainbow ('jet')"
  label_r: "After: viridis, lighter means more"
  panel_l:
    kind: referential
    sub: paper-figure
    intent: monthly air passengers 1949 to 1960 as a month-by-year heatmap in jet; built by assets/verified_snippets.py
    asset: b4-colour-l.png
  panel_r:
    kind: referential
    sub: paper-figure
    intent: the same heatmap in viridis; built by assets/verified_snippets.py
    asset: b4-colour-r.png
generated_hash: 560455345a2bfc48
```

**Claim.** A rainbow map draws bands into smooth data and fails for colour-blind viewers; a perceptually uniform map like viridis reads in order, lighter meaning more.

**Skip.** Diverging maps. They come with the correlation heatmap in the toolbox.

## 2.6 — Point at what matters

```yaml
id: b5-annotate
origin: generated
layout: two-up-compare
time_s: 90
transition: cut
content:
  label_l: "Before: the reader hunts for it"
  label_r: "After: the crash is marked"
  panel_l:
    kind: constructible
    sub: axes
    intent: the monthly Dow Jones index 1914 to 1968 as a plain line; built by assets/verified_snippets.py
    asset: b5-annotate-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: the same line with the 1929 to 1932 fall drawn in green and labelled -87%; built by assets/verified_snippets.py
    asset: b5-annotate-r.png
generated_hash: c43a1997bde55c67
```

**Claim.** An annotation tells the reader where to look and why; without it, the 1929 crash is one wiggle among many.

**Skip.** Arrows on every point. One or two annotations per chart.

## 2.7 — A title that states the takeaway

```yaml
id: b6-title
origin: generated
layout: two-up-compare
time_s: 90
transition: cut
content:
  label_l: "Before: 'Figure 1'"
  label_r: "After: the finding is the title"
  panel_l:
    kind: constructible
    sub: axes
    intent: penguin mean body mass bars titled "Figure 1"; built by assets/verified_snippets.py
    asset: b6-title-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: the same bars titled "Gentoo penguins are over a third heavier"; built by assets/verified_snippets.py
    asset: b6-title-r.png
generated_hash: 8ebbe88750aa1c90
```

**Claim.** A title that states the finding tells the reader what the chart shows before they have to work it out; "Figure 1" tells them nothing.

## 2.8 — Sort by value

```yaml
id: b7-sort
origin: generated
layout: two-up-compare
time_s: 75
transition: cut
content:
  label_l: "Before: alphabetical"
  label_r: "After: sorted by value"
  panel_l:
    kind: constructible
    sub: axes
    intent: eight US states by drivers in fatal crashes, bars in alphabetical order; built by assets/verified_snippets.py
    asset: b7-sort-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: the same eight bars sorted by value, largest on top; built by assets/verified_snippets.py
    asset: b7-sort-r.png
generated_hash: dc9cb25f6ee50a27
```

**Claim.** Sorting bars by value turns a lookup table into a ranking; alphabetical order answers a question nobody asked.

**Skip.** Categories with a natural order, such as months or grades. Keep that order.

## 2.9 — Aspect ratio sets the slope

```yaml
id: b8-aspect
origin: generated
layout: two-up-compare
time_s: 90
transition: cut
content:
  label_l: "Before: tall and narrow"
  label_r: "After: banked to about 45°"
  panel_l:
    kind: constructible
    sub: axes
    intent: yearly air passengers 1949 to 1960 in a tall, narrow plot that makes the growth look steep; built by assets/verified_snippets.py
    asset: b8-aspect-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: the same line in a plot shaped so its slopes run near 45 degrees; built by assets/verified_snippets.py
    asset: b8-aspect-r.png
generated_hash: 3c1f91b9f823592d
```

**Claim.** The same line looks steep in a tall, narrow chart and calm in a flat one; a shape where the slopes run near 45 degrees shows the change without exaggerating it.

**Skip.** Cleveland's banking calculation. figsize is the knob.

## 2.10 — The habits, in code

```yaml
id: b-fixes-code
origin: generated
layout: full-bleed-figure
time_s: 120
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: the penguin means as sorted horizontal bars, labelled and titled with the finding, and the cell that draws them
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/b-fixes-code.png
    intent: sorted, labelled penguin bars titled with the finding; built by assets/verified_snippets.py
    code: |
      penguins = sns.load_dataset("penguins")
      means = penguins.groupby("species")["body_mass_g"].mean()
      ax = means.sort_values().plot.barh()
      ax.set(xlabel="mean body mass (g)", ylabel="")
      ax.set_title("Gentoo penguins are over a third heavier")
      sns.despine()
generated_hash: a184f3550ff5b114
```

**Claim.** The habits cost a few lines: a bar instead of a line, sorted, labelled, titled with the finding, and the extra ink removed.

**Skip.** Colour and annotation in code. Part 1 of the notebook has both.

# Section 3 — Notebook, part 1

> **Bridge.** Habits stick only once they have been applied, so the first notebook part hands over charts that break them.

## 3.1 — Notebook, part 1

```yaml
id: practice1-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 3.2 — Part 1: the habits

```yaml
id: act-habits-setup
origin: generated
layout: activity-setup
time_s: 120
transition: cut
content:
  task: >
    Each chart in Part 1 breaks at least two of the habits. Say what is wrong
    with it, then redraw it: the right chart, sorted, labelled, with a title
    that states the finding.
  example: |
    ax = means.sort_values().plot.barh()
generated_hash: fd90c96b56bfa018
```

**Note.** The slide is a lecture and then we get hands on (that is more like a tutorial)

**Claim.** The first exercise applies the eight habits to charts that break them.

## 3.3 — Part 1: redraw three charts

```yaml
id: act-habits-parking
origin: generated
layout: activity-parking
time_s: 1800
transition: cut
content:
  instructions: >
    Open datavis_2.ipynb, Part 1. Three charts each break at least two
    of the eight habits. For each one, write down what is wrong, then redraw
    it: the right chart for the question, sorted, labelled axes, a title that
    states the finding and no extra ink. Stretch: annotate the one point the
    chart is about.
  constraints:
    - 30 minutes
    - pairs welcome
    - solutions hidden under each exercise
generated_hash: 8c32e5999da4ca94
```

**Claim.** Thirty minutes of redrawing, so the habits have been typed once before the toolbox adds more charts.

## 3.4 — Break

```yaml
id: break-1
origin: generated
layout: claim-only
time_s: 900
transition: cut
generated_hash: 36b914af13ca61ce
```

**Note.** Each class are 4 hours long but I need to have some gaps and exercices

**Claim.** Fifteen-minute break; the toolbox starts from the same penguins.

# Section 4 — A small toolbox

> **Bridge.** The habits assume the chart type is already right, but bars and lines answer only some questions, and no single chart answers all of them.

## 4.1 — A small toolbox

```yaml
id: toolbox-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 4.2 — No correct chart

```yaml
id: toolbox-nuance
origin: generated
layout: callout
time_s: 60
transition: cut
generated_hash: 7f85907b6e905a42
```

**Note.** there is no correct chart for every case and to have a toolbox is okay but I dont want to over do it too

**Claim.** There is no correct chart for every case. A small toolbox, picked by the question you are asking, is enough.

## 4.3 — Which question, which chart

```yaml
id: toolbox-map
origin: generated
layout: table-accented
time_s: 90
transition: cut
content:
  claim: null
  table:
    - [question, reach for]
    - ["How is it spread out?", "box, violin, strip"]
    - ["How sure is the average?", "error bars"]
    - ["How many in each group?", "count plot, grouped bar"]
    - ["What share of the whole?", "stacked bar, donut, area"]
    - ["How do numbers relate?", "bubble, pair plot, heatmap"]
    - ["Same chart, many groups?", "small multiples"]
    - ["Where does the model err?", "confusion matrix"]
generated_hash: 74b787a919fb9455
```

**Claim.** Each question has a few good charts, and the toolbox is a map from the question to them, not a rule that picks one.

**Skip.** Radar, Pareto and waterfall charts. Left out of the toolbox on purpose.

## 4.4 — Today's data

```yaml
id: toolbox-data
origin: generated
layout: claim-above-figure
time_s: 45
transition: cut
visual:
  kind: constructible
  intent: cell toolbox-data of assets/verified_snippets.py, verbatim
  builder: scenes.code_block:code
  args:
    code: |
      titanic = sns.load_dataset("titanic")
      tips = sns.load_dataset("tips")
      mpg = sns.load_dataset("mpg")
      planets = sns.load_dataset("planets")
generated_hash: 121df25af7d0e27a
```

**Claim.** Every chart in the toolbox uses the penguins or one of four more small datasets that ship with seaborn, one line each.

**On slide.**
- Passengers, restaurant bills, cars, exoplanets
- All built into seaborn, like the penguins

**Skip.** What every column means. Each chart says what it plots.

## 4.5 — Box, violin, strip

```yaml
id: d-spread
origin: generated
layout: full-bleed-figure
time_s: 90
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: penguin flipper length by island as a box, a violin and a strip side by side, and the cell that draws them
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/d-spread.png
    intent: box, violin and strip of flipper length by island; built by assets/verified_snippets.py
    code: |
      kw = dict(data=penguins, x="flipper_length_mm", y="island")
      fig, axes = plt.subplots(1, 3, sharey=True)
      sns.boxplot(**kw, ax=axes[0])
      sns.violinplot(**kw, ax=axes[1])
      sns.stripplot(**kw, ax=axes[2])
generated_hash: ebff90751f7c846c
```

**Claim.** The same flipper lengths three ways: the box summarises, the violin shows the two humps on Biscoe that the box hides, and the strip shows every penguin.

**Skip.** How the violin is smoothed (kernel density). The shape is the point.

## 4.6 — Violin with the points

```yaml
id: d-raincloud
origin: generated
layout: full-bleed-figure
time_s: 75
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: the violins of flipper length by island with every penguin drawn on top, and the two lines that draw them
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/d-raincloud.png
    intent: violin with the raw points layered on top; built by assets/verified_snippets.py
    code: |
      sns.violinplot(**kw, inner=None, color="0.85")
      sns.stripplot(**kw, color="black", size=3)
generated_hash: 3179638c6b39be87
```

**Note.** I prefer to show just the violin.

**Claim.** Layering the points over the violin shows the shape and every penguin at once, so a smooth curve cannot hide how few points sit behind it.

## 4.7 — Error bars

```yaml
id: d-errorbars
origin: generated
layout: full-bleed-figure
time_s: 75
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: mean tip per day with 95% confidence intervals, all four overlapping, and the call that draws it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/d-errorbars.png
    intent: mean tip by day with 95% CIs; built by assets/verified_snippets.py
    code: |
      sns.pointplot(tips, x="day", y="tip",
                    errorbar=("ci", 95), linestyle="none")
generated_hash: 11f60d626effac3d
```

**Claim.** An error bar shows how sure the mean is, not how spread out the data is: the four days' intervals overlap, so the differences in mean tip may be noise.

**Skip.** Bootstrap against t-intervals. seaborn bootstraps; the reading is the same.

## 4.8 — Count plot

```yaml
id: d-countplot
origin: generated
layout: full-bleed-figure
time_s: 60
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: Titanic passengers per class, split into died and survived, and the call that draws it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/d-countplot.png
    intent: passenger counts per class, by survival; built by assets/verified_snippets.py
    code: |
      sns.countplot(titanic, x="class", hue="alive")
generated_hash: f2f2a3732a8a6ef9
```

**Claim.** countplot counts the rows for you: passengers per class, split by whether they survived.

## 4.9 — Grouped bar

```yaml
id: d-groupedbar
origin: generated
layout: full-bleed-figure
time_s: 60
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: penguin mean body mass by species, males beside females, and the call that draws it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/d-groupedbar.png
    intent: mean body mass by species and sex; built by assets/verified_snippets.py
    code: |
      sns.barplot(penguins, x="species", y="body_mass_g",
                  hue="sex")
generated_hash: 4a8722396f37c617
```

**Claim.** A grouped bar compares two categories at once: species along the axis, and males against females inside each species.

## 4.10 — Stacked and 100% stacked

```yaml
id: d-stacked
origin: generated
layout: full-bleed-figure
time_s: 90
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: Titanic class by survival as stacked counts and as 100% shares, and the cell that draws both
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/d-stacked.png
    intent: stacked counts and stacked shares per class; built by assets/verified_snippets.py
    code: |
      counts = pd.crosstab(titanic["class"], titanic["alive"])
      counts.plot.bar(stacked=True)
      shares = counts.div(counts.sum(axis=1), axis=0)
      shares.plot.bar(stacked=True)
generated_hash: 0af2670a278a99ea
```

**Claim.** Stacked bars show each class's total and its make-up; rescaled to 100% they show the share that survived, which is the question here.

**Skip.** Comparing the middle segments of a stacked bar. Only the bottom segment shares a baseline.

## 4.11 — Donut

```yaml
id: d-pie
origin: generated
layout: full-bleed-figure
time_s: 60
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: the three Titanic classes as a donut, 55%, 24% and 21%, and the cell that draws it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/d-pie.png
    intent: share of passengers per class as a donut; built by assets/verified_snippets.py
    code: |
      classes = titanic["class"].value_counts()
      plt.pie(classes, labels=classes.index, autopct="%.0f%%",
              wedgeprops={"width": 0.4}, pctdistance=0.8)
generated_hash: d2f2a97f179709dd
```

**Claim.** A pie or a donut is fine for two or three parts of one whole, like the three classes; with more parts, bars, as the habits showed.

## 4.12 — Stacked area

```yaml
id: d-area
origin: generated
layout: full-bleed-figure
time_s: 75
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: exoplanets found per year by radial velocity and by transit as a stacked area, and the cell that draws it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/d-area.png
    intent: planets found per year, two methods stacked; built by assets/verified_snippets.py
    code: |
      per_year = pd.crosstab(planets["year"], planets["method"])
      per_year[["Radial Velocity", "Transit"]].plot.area()
generated_hash: 19db5f07eb070c0c
```

**Claim.** A stacked area shows a total over time and what it is made of: radial velocity found most planets until transit surveys overtook it around 2010.

**Skip.** The drop in 2014. The dataset ends in 2014, so the last year is incomplete.

## 4.13 — Bubble chart

```yaml
id: d-bubble
origin: generated
layout: full-bleed-figure
time_s: 60
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: cars' horsepower against miles per gallon, sized by weight and coloured by origin, and the call that draws it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/d-bubble.png
    intent: horsepower against mpg, size weight, hue origin; built by assets/verified_snippets.py
    code: |
      sns.scatterplot(mpg, x="horsepower", y="mpg",
                      size="weight", hue="origin")
generated_hash: 292169a91653052f
```

**Claim.** A bubble chart adds a third number as size: heavier cars have more horsepower and fewer miles per gallon, though sizes are hard to compare exactly.

## 4.14 — Pair plot

```yaml
id: d-pairplot
origin: generated
layout: full-bleed-figure
time_s: 75
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: every pair of mpg, weight and horsepower, coloured by origin, and the call that draws it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/d-pairplot.png
    intent: pair plot of three car columns by origin; built by assets/verified_snippets.py
    code: |
      sns.pairplot(mpg, hue="origin",
                   vars=["mpg", "weight", "horsepower"])
generated_hash: 0b4cac2427cb9398
```

**Claim.** A pair plot draws every pair of columns at once, which makes it the first look at a new table rather than a chart to present.

## 4.15 — Correlation heatmap

```yaml
id: d-corr
origin: generated
layout: full-bleed-figure
time_s: 75
transition: cut
visual:
  kind: referential
  sub: paper-figure
  intent: correlations of four car columns on a diverging map centred on zero, and the cell that draws it; the vlag colour map is off the deck palette on purpose
  asset: d-corr.png
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/d-corr.png
    intent: correlation heatmap, diverging, annotated; built by assets/verified_snippets.py
    kind: referential
    sub: paper-figure
    code: |
      cols = ["mpg", "weight", "horsepower", "acceleration"]
      corr = mpg[cols].corr()
      sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag",
                  vmin=-1, vmax=1)
generated_hash: 85ddef46c682aecb
```

**Claim.** A correlation heatmap needs a diverging map centred on zero, because a correlation has a sign: weight and mpg move against each other at -0.83.

## 4.16 — Small multiples

```yaml
id: d-facets
origin: generated
layout: full-bleed-figure
time_s: 75
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: weight against mpg in one panel per origin on shared axes, and the call that draws it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/d-facets.png
    intent: one scatter per origin, shared axes; built by assets/verified_snippets.py
    code: |
      sns.relplot(mpg, x="weight", y="mpg", col="origin")
generated_hash: 400d2302bec4c8f4
```

**Claim.** Small multiples repeat one chart per group on shared axes, which reads more easily than every group overlaid in colour.

## 4.17 — Confusion matrix

```yaml
id: d-confusion
origin: generated
layout: full-bleed-figure
time_s: 90
transition: cut
visual:
  kind: referential
  sub: paper-figure
  intent: a row-normalised confusion matrix of a penguin-species classifier, Chinstrap mostly called Adelie, and the cell that draws it; the Greens colour map is off the deck palette
  asset: d-confusion.png
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/d-confusion.png
    intent: normalised confusion matrix, three species; built by assets/verified_snippets.py
    kind: referential
    sub: paper-figure
    code: |
      cm = confusion_matrix(y_test, y_pred, normalize="true")
      ax = sns.heatmap(cm, annot=True, fmt=".2f", cmap="Greens",
                       xticklabels=labels, yticklabels=labels)
      ax.set(xlabel="predicted", ylabel="true")
generated_hash: aeecad3e3d70e53e
```

**Claim.** A confusion matrix shows which classes a model mixes up: this one is 83% accurate overall and still calls 70% of Chinstraps Adelie.

**Skip.** The model itself. A logistic regression on two measurements, chosen because it makes mistakes.

## 4.18 — Bars, lines, scatters first

```yaml
id: toolbox-enough
origin: generated
layout: callout
time_s: 45
transition: cut
generated_hash: 1961557e21fcd6ea
```

**Claim.** Most charts you draw will still be a bar, a line or a scatter; reach into the toolbox when the question asks for it.

# Section 5 — Notebook, part 2

> **Bridge.** A toolbox is learned by reaching into it, so part 2 hands over questions and leaves the choice of chart to them.

## 5.1 — Notebook, part 2

```yaml
id: practice2-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 5.2 — Part 2: pick the chart

```yaml
id: act-toolbox-setup
origin: generated
layout: activity-setup
time_s: 120
transition: cut
content:
  task: >
    Part 2 asks five questions about the titanic, tips, diamonds and mpg data.
    For each one, pick a chart from the toolbox, draw it, and give it a title
    that answers the question.
  example: |
    counts.plot.bar(stacked=True)
generated_hash: 68138479a352288a
```

**Claim.** The second exercise hands over questions, not chart types, so choosing the chart is part of the work.

## 5.3 — Part 2: five questions

```yaml
id: act-toolbox-parking
origin: generated
layout: activity-parking
time_s: 2400
transition: cut
content:
  instructions: >
    Part 2. Five questions, one chart each: fares by class; the mean bill,
    smokers against non-smokers; men, women and children per class; diamond
    measurements that move together; fuel economy by year, one panel per
    origin. Title each chart with its answer. More than one chart can be
    right: be ready to say why you chose yours.
  constraints:
    - 40 minutes
    - pairs welcome
    - solutions hidden under each exercise
generated_hash: 34f8f4ddb375affc
```

**Claim.** Forty minutes where the choice of chart is theirs, and the debrief compares the choices.

## 5.4 — Break

```yaml
id: break-2
origin: generated
layout: claim-only
time_s: 900
transition: cut
generated_hash: db1141f88a5a4345
```

**Claim.** Fifteen-minute break, then how charts lie.

# Section 6 — How charts lie

> **Bridge.** With the habits and the toolbox they can draw an honest chart; the same choices made the other way give charts that are correct in every number and still mislead, like the kidney-stone chart from the opening.

## 6.1 — How charts lie

```yaml
id: lie-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 6.2 — Six more

```yaml
id: lie-intro
origin: generated
layout: claim-only
time_s: 30
transition: cut
generated_hash: 32df7851c2e4e436
```

**Claim.** Six more charts that are correct in every number and still mislead, each with the question that catches it.

## 6.3 — Truncated axis

```yaml
id: c1-truncated
origin: generated
layout: two-up-compare
time_s: 120
transition: cut
content:
  label_l: "Misleading: axis starts at $2.60"
  label_r: "Honest: bars start at zero"
  panel_l:
    kind: constructible
    sub: axes
    intent: mean tip per day as bars on an axis that starts at $2.60; built by assets/verified_snippets.py
    asset: c1-truncated-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: the same four bars from zero; built by assets/verified_snippets.py
    asset: c1-truncated-r.png
generated_hash: 65de9b274c8e22b3
```

**Claim.** Starting a bar chart's axis at $2.60 makes Sunday's tips look five times Friday's when they are 19% higher; ask where the axis starts.

**Skip.** Line charts. A line's axis need not start at zero; a bar's length has to.

## 6.4 — Two y-axes

```yaml
id: c2-dual-axes
origin: generated
layout: two-up-compare
time_s: 120
transition: cut
content:
  label_l: "Misleading: two scales cross"
  label_r: "Honest: one scale, 1970 = 100"
  panel_l:
    kind: constructible
    sub: axes
    intent: mean mpg (green, left axis) and mean weight (yellow, right axis) of cars 1970 to 1982, scaled so the lines cross; built by assets/verified_snippets.py
    asset: c2-dual-axes-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: the same two series indexed to 1970 = 100 on one axis; built by assets/verified_snippets.py
    asset: c2-dual-axes-r.png
generated_hash: 503bf5c9994afe8f
```

**Claim.** Two y-axes can be scaled to make any two lines meet, cross or move together, so the crossing means nothing; put both on one scale, such as an index.

## 6.5 — Cherry-picked window

```yaml
id: c4-window
origin: generated
layout: two-up-compare
time_s: 120
transition: cut
content:
  label_l: "Misleading: Jul to Nov 1960"
  label_r: "Honest: all twelve years"
  panel_l:
    kind: constructible
    sub: axes
    intent: monthly air passengers July to November 1960 only, falling 37%; built by assets/verified_snippets.py
    asset: c4-window-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: the whole 1949 to 1960 series with that window shaded green; built by assets/verified_snippets.py
    asset: c4-window-r.png
generated_hash: 6193733d3397e655
```

**Claim.** Passengers fell 37% from July to November 1960, as they did every autumn on a rising trend; ask why the chart starts and ends where it does.

## 6.6 — Mean or median

```yaml
id: c7-mean-median
origin: generated
layout: two-up-compare
time_s: 120
transition: cut
content:
  label_l: "Misleading: the mean, $3,933"
  label_r: "Honest: the median, $2,401"
  panel_l:
    kind: constructible
    sub: axes
    intent: histogram of diamond prices with the mean, $3,933, marked; built by assets/verified_snippets.py
    asset: c7-mean-median-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: the same histogram with the median, $2,401, marked in green; built by assets/verified_snippets.py
    asset: c7-mean-median-r.png
generated_hash: 8050de06ee82daad
```

**Claim.** A few expensive diamonds pull the mean to $3,933 while the typical diamond costs $2,401; check the shape of the data and report the median.

## 6.7 — Correlation is not cause

```yaml
id: c9-spurious
origin: generated
layout: two-up-compare
time_s: 120
transition: cut
content:
  label_l: "Misleading: r = 0.98"
  label_r: "Honest: year-on-year, r = 0.27"
  panel_l:
    kind: constructible
    sub: axes
    intent: yearly air passengers against the Dow Jones, 1949 to 1960, with a fitted line and r = 0.98; built by assets/verified_snippets.py
    asset: c9-spurious-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: their year-on-year changes against each other, r = 0.27; built by assets/verified_snippets.py
    asset: c9-spurious-r.png
generated_hash: 141a12cddabd33a6
```

**Claim.** Air passengers and the Dow Jones correlate at 0.98 because both grew through the 1950s; their year-on-year changes barely correlate, so time is the shared cause, not flying.

## 6.8 — Survivorship bias

```yaml
id: c10-survivors
origin: generated
layout: two-up-compare
time_s: 120
transition: cut
content:
  label_l: "Misleading: armour where hit"
  label_r: "Honest: armour where not hit"
  panel_l:
    kind: constructible
    sub: geometry
    intent: a bomber seen from above with the holes found on planes that came back; illustrative, after Wald (1943); built by assets/verified_snippets.py
    asset: c10-survivors-l.png
  panel_r:
    kind: constructible
    sub: geometry
    intent: the same bomber with the engines and cockpit, where no holes were seen, circled in green; built by assets/verified_snippets.py
    asset: c10-survivors-r.png
generated_hash: fca67b90bfe97681
```

**Claim.** The planes that came back show where a plane can be hit and survive; the hits that matter were on the planes that did not return, so ask what is missing from the sample.

**Skip.** The full Wald story and how it has been retold. The drawing is illustrative, not data.

## 6.9 — Base-rate neglect

```yaml
id: c11-base-rate
origin: generated
layout: two-up-compare
time_s: 120
transition: cut
backup: true
demoted_because: 'C backup pick, from the user''s "and what else gets too much"'
visual:
  kind: constructible
  sub: axes
  intent: both panels, the 90% the headline suggests, and the 9 sick among 108 positives; built by assets/verified_snippets.py
  asset: c11-base-rate-r.png
content:
  backup_of: two-up-compare
  label_l: "Misleading: '90% accurate'"
  label_r: "Honest: 9 of 108 positives are sick"
  panel_l:
    kind: constructible
    sub: axes
    intent: one bar at 90%, the chance a positive is sick as the headline suggests it; built by assets/verified_snippets.py
    asset: c11-base-rate-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: the 108 positives out of 1,000 people, 9 sick (green) and 99 not; built by assets/verified_snippets.py
    asset: c11-base-rate-r.png
generated_hash: 09fe9ec2bb25c0b0
```

**Claim.** When 1 person in 100 has the condition, a test that is 90% accurate still gives 99 false positives for 9 true ones; ask for the base rate.

**Skip.** Bayes' rule. The counts carry it.

## 6.10 — Misleading colour scale

```yaml
id: c12-colour-scale
origin: generated
layout: two-up-compare
time_s: 90
transition: cut
backup: true
demoted_because: 'C backup pick, from the user''s "and what else gets too much"'
visual:
  kind: referential
  sub: paper-figure
  intent: both panels show real colour maps (jet, viridis), off the deck palette on purpose; built by assets/verified_snippets.py
  asset: c12-colour-scale-r.png
content:
  backup_of: two-up-compare
  label_l: "Misleading: rainbow bands"
  label_r: "Honest: the same field, viridis"
  panel_l:
    kind: referential
    sub: paper-figure
    intent: a smooth synthetic field drawn in jet, showing bands and a hot spot that are not in the data; built by assets/verified_snippets.py
    asset: c12-colour-scale-l.png
  panel_r:
    kind: referential
    sub: paper-figure
    intent: the same field in viridis; built by assets/verified_snippets.py
    asset: c12-colour-scale-r.png
generated_hash: 9960868f3901952c
```

**Claim.** A rainbow map draws sharp bands and a hot spot into a field that changes smoothly everywhere; the same data in viridis shows no edges.

**Skip.** Repeating the colour habit. Same root cause, shown on data that has no edges at all.

## 6.11 — Log scale, unlabelled

```yaml
id: c13-log-scale
origin: generated
layout: two-up-compare
time_s: 90
transition: cut
backup: true
demoted_because: 'C backup pick, from the user''s "and what else gets too much"'
visual:
  kind: constructible
  sub: axes
  intent: both panels, the same yearly series on an unlabelled log axis and on a linear one; built by assets/verified_snippets.py
  asset: c13-log-scale-r.png
content:
  backup_of: two-up-compare
  label_l: "Misleading: log axis, plain ticks"
  label_r: "Honest: linear axis, said so"
  panel_l:
    kind: constructible
    sub: axes
    intent: yearly air passengers on a log axis whose ticks read like a linear one; built by assets/verified_snippets.py
    asset: c13-log-scale-l.png
  panel_r:
    kind: constructible
    sub: axes
    intent: the same series on a linear axis labelled as linear; built by assets/verified_snippets.py
    asset: c13-log-scale-r.png
generated_hash: 1465d1cf3f4915a4
```

**Claim.** A log axis with plain-looking ticks turns accelerating growth into a calm straight line; ask whether the gaps between the ticks are equal.

# Section 7 — Fix this chart

> **Bridge.** Spotting a trick is half the skill and fixing it is the other half, so the last exercise is one chart that makes several of the day's mistakes at once.

## 7.1 — Fix this chart

```yaml
id: fix-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 7.2 — What is wrong here?

```yaml
id: fix-bad
origin: generated
layout: full-bleed-figure
time_s: 60
transition: cut
visual:
  kind: referential
  sub: paper-figure
  intent: mean NYC taxi fare by pickup borough on an axis cut at 10, in rainbow colours, alphabetical, titled "Figure 1", with no y label, and the cell that draws it; the rainbow is off the deck palette on purpose
  asset: fix-bad.png
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/fix-bad.png
    intent: the bad taxi-fare chart; drawn by the fix-bad cell of assets/verified_snippets.py
    kind: referential
    sub: paper-figure
    code: |
      taxis = sns.load_dataset("taxis")
      fares = taxis.groupby("pickup_borough")["fare"].mean()
      ax = fares.plot.bar(color=["red", "gold", "green", "blue"])
      ax.set_ylim(10, 26)
      ax.set_title("Figure 1")
generated_hash: fee11c526742ceb0
```

**Claim.** This chart of New York taxi fares breaks at least five of today's rules at once.

**Skip.** The answers. They come after the exercise.

## 7.3 — Part 3: fix this chart

```yaml
id: act-fix-setup
origin: generated
layout: activity-setup
time_s: 120
transition: cut
content:
  task: >
    In pairs: list everything wrong with this chart, then redraw it honestly
    from the same data, so it answers "where do taxi rides cost the most?"
  example: |
    taxis = sns.load_dataset("taxis")
generated_hash: 6dec0f3febc6ba8f
```

**Claim.** The exercise is diagnosis first and a redraw second, in pairs.

## 7.4 — Part 3: ten minutes

```yaml
id: act-fix-parking
origin: generated
layout: activity-parking
time_s: 600
transition: cut
content:
  instructions: >
    Part 3 of the notebook draws this chart from sns.load_dataset("taxis").
    Write down every problem you can find, then redraw it so it answers
    "where do taxi rides cost the most?" honestly. One chart per pair; we
    look at three of them.
  constraints:
    - 10 minutes
    - in pairs
    - one chart per pair
generated_hash: 4a2901afbd928318
```

**Claim.** Ten minutes in pairs, ending with a chart each pair can defend.

## 7.5 — What did you change?

```yaml
id: fix-debrief
origin: generated
layout: discussion
time_s: 180
transition: cut
generated_hash: ee63a2b3b9e5ac89
```

**Claim.** What did you change, which problem was the hardest to see, and did any pair end up answering a different question?

## 7.6 — One honest version

```yaml
id: fix-one-answer
origin: generated
layout: full-bleed-figure
time_s: 120
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: median taxi fare per pickup borough as sorted horizontal bars from zero, titled with the finding, and the cell that draws it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/fix-one-answer.png
    intent: median fare by borough, sorted, titled; built by assets/verified_snippets.py
    code: |
      order = ["Queens", "Bronx", "Brooklyn", "Manhattan"]
      ax = sns.barplot(taxis, x="fare", y="pickup_borough",
                       estimator="median", order=order,
                       errorbar=None)
      ax.set(xlabel="median fare (USD)", ylabel="")
      ax.set_title("A Queens pickup costs 2.5x a Manhattan one")
generated_hash: f5aa3859e79da12b
```

**Claim.** One honest version: medians, sorted, from zero, in one colour, with the finding as the title; a box plot of every fare would be another.

## 7.7 — Same data, another question

```yaml
id: fix-per-mile
origin: generated
layout: full-bleed-figure
time_s: 90
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: median fare per mile per pickup borough in the same order, now rising instead of falling, and the cell that draws it
  builder: scenes.code_block:figure_with_code
  args:
    image: decks/datavis-2/assets/built/fix-per-mile.png
    intent: median fare per mile by borough, same order; built by assets/verified_snippets.py
    code: |
      rides = taxis[taxis["distance"] > 0].copy()
      rides["per_mile"] = rides["fare"] / rides["distance"]
      ax = sns.barplot(rides, x="per_mile", y="pickup_borough",
                       estimator="median", order=order,
                       errorbar=None)
      ax.set(xlabel="median fare per mile (USD)", ylabel="")
      ax.set_title("Per mile, Queens rides are the cheapest")
generated_hash: 3ce826e019cf9abd
```

**Claim.** Asked per mile instead of per ride, the order flips and Queens is the cheapest, because its rides are long; which chart is honest depends on the question.

**Skip.** Airport flat fares and tolls. Distance alone flips the order.

# Section 8 — A checklist to keep

> **Bridge.** Every fix in the exercise answered one of a few questions, and those questions are a checklist to run on any chart, theirs or anyone else's.

## 8.1 — Before you trust a chart

```yaml
id: checklist
origin: generated
layout: build-list
time_s: 150
transition: cut
generated_hash: 65d4a116de082346
```

**Claim.** Seven questions catch every trick from today and carry the habits that prevent them.

**On slide.**
- Does the chart fit the question?
- Where does the axis start? Is there a second one?
- Why this time window?
- Mean or median: what shape is the data?
- Is a group hiding inside the total?
- Correlated, or caused? What is missing from the sample?
- Sorted, labelled, titled with the finding?

## 8.2 — An honest one

```yaml
id: close-callout
origin: generated
layout: callout
time_s: 45
transition: cut
generated_hash: 768389500a9625ac
```

**Claim.** There is no correct chart for every case, but for each question there is an honest one, and these seven questions find it.

## 8.3 — Your own charts

```yaml
id: close-discussion
origin: generated
layout: discussion
time_s: 180
transition: cut
generated_hash: b4a3f46fc8a828ae
```

**Claim.** Which chart from your own work would fail this checklist, and which question would catch it?
