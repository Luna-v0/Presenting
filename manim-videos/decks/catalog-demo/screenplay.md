---
slug: catalog-demo
title: The layout catalog
subtitle: One beat per layout, rendered
author: Presenting
affiliation: manim-videos/presenting_lib
date: "2026"
target: manim
duration_min: 30
brief: ./brief.md
---

# Section 1 — Opening the deck

> **Bridge.** Opening frame: three layouts carry the start of every talk — the title, the section break, and a single sentence with nothing else on screen.

## 1.1 — Title

```yaml
id: title
layout: title-card
time_s: 20
```

## 1.2 — One sentence, nothing else

```yaml
id: the-claim-only
layout: claim-only
time_s: 30
```

**Claim.** A slide holding one sentence and nothing else is the strongest thing in the catalog, and the least used.

## 1.3 — The workhorse

```yaml
id: the-workhorse
layout: claim-above-figure
time_s: 45
transition: cut
visual:
  kind: constructible
  sub: graph
  intent: brief to screenplay to render, with review feeding back
  graph:
    rankdir: LR
    nodes:
      - {id: brief, label: brief}
      - {id: screenplay, label: screenplay}
      - {id: render, label: render}
      - {id: review, label: review}
    edges:
      - {from: brief, to: screenplay}
      - {from: screenplay, to: render}
      - {from: render, to: review}
      - {from: review, to: screenplay}
```

**Claim.** Most beats are a claim across the top and a figure under it, and expecting anything else is how a catalog grows layouts nobody uses.

**On slide.**
- Claim on top, figure under it

## 1.4 — Building on the last beat

```yaml
id: the-build-transition
layout: build-list
time_s: 45
transition: build
```

**Claim.** A build transition keeps the previous beat on screen instead of clearing it.

**On slide.**
- transition: cut — clear and start fresh
- transition: build — keep what is there

# Section 2 — Showing a figure

> **Bridge.** Once a figure is the point rather than the accompaniment, the claim has to get out of its way — and there are three degrees of getting out of the way.

## 2.1 — Showing a figure

```yaml
id: figures-break
layout: section-break
time_s: 10
```

## 2.2 — Callouts around a figure

```yaml
id: the-callouts
layout: figure-with-callouts
time_s: 60
visual:
  kind: constructible
  sub: process
  intent: the three stages, middle one under discussion
  graph:
    rankdir: TB
    nodes:
      - {id: collect, label: collect}
      - {id: fit, label: fit}
      - {id: optimise, label: optimise}
    edges:
      - {from: collect, to: fit}
      - {from: fit, to: optimise}
edges: []
content:
  callouts:
    - ["annotators disagree here", [0.5, 0.86]]
    - ["one number per response", [0.5, 0.5]]
    - "and the policy chases it"
```

**Claim.** Three callouts with leaders, and no leader at all when a callout has nowhere to point.

## 2.3 — Two panels side by side

```yaml
id: the-two-up
layout: two-up-compare
time_s: 50
content:
  label_l: Before
  label_r: After
  panel_l:
    kind: referential
    sub: photo
    intent: the deck as it looked before the identity
  panel_r:
    kind: constructible
    sub: geometry
    intent: the same deck on sand, with chrome
```

**Claim.** Comparison is its own layout, because doing it with two beats loses the comparison.

## 2.4 — The whole frame

```yaml
id: the-full-bleed
layout: full-bleed-figure
time_s: 40
visual:
  kind: constructible
  sub: graph
  intent: one figure with nothing else on screen at all
  graph:
    rankdir: LR
    nodes:
      - {id: no_title, label: no title}
      - {id: no_footer, label: no footer}
      - {id: no_dots, label: no dots}
      - {id: just_this, label: just the figure}
    edges:
      - {from: no_title, to: just_this}
      - {from: no_footer, to: just_this}
      - {from: no_dots, to: just_this}
```

**Claim.** Chrome tier none: no title, no footer, no dots, and the compiler animates the chrome out to get there.

# Section 3 — Text that has to be exact

> **Bridge.** Figures carry the argument, but some beats turn on a definition, a formula or a number — and those are the beats where the text itself has to be exact.

## 3.1 — Text that has to be exact

```yaml
id: exact-break
layout: section-break
time_s: 10
```

## 3.2 — Naming a thing

```yaml
id: the-term
layout: term-reveal
time_s: 45
visual:
  kind: chart
  intent: what the term does to the numbers
  data:
    kind: line
    x: [0, 1, 2, 3, 4, 5]
    series:
      proxy: [0, 1.0, 1.9, 2.7, 3.4, 4.0]
      gold: [0, 0.9, 1.5, 1.6, 1.3, 0.8]
    accent: gold
    xlabel: optimisation
    ylabel: reward
```

**Claim.** The term arrives alone, and the definition follows on the next click, because a definition already on screen spends the moment of naming.

**On slide.**
- Overoptimisation

## 3.3 — A formula with its parts marked

```yaml
id: the-equation
layout: equation-annotated
time_s: 60
content:
  equation: P(a \succ b) = \frac{e^{r(a)}}{e^{r(a)} + e^{r(b)}}
  annotations:
    - [one scalar per response, green]
    - [which forces a total order, yellow]
```

**Claim.** Green marks the first of two things being related and yellow the second — a formula whose parts are being explained against each other is what the pair exists for.

**Cue.** point at the numerator, then the ordering

## 3.4 — A table with one row marked

```yaml
id: the-table
layout: table-accented
time_s: 45
content:
  table:
    - [method, win rate, cost]
    - [Bradley-Terry, "0.51", low]
    - [preference model, "0.63", high]
  accent_rows: [3]
```

**Claim.** An unmarked table is a wall of numbers and the room has to be told where to look.

**On slide.**
- One row marked, the rest quiet

## 3.5 — The thesis, held

```yaml
id: the-callout
layout: callout
time_s: 30
```

**Claim.** A callout holds one sentence inside a rule, and it is the other place a full sentence belongs on screen.

# Section 4 — Beats that are not slides

> **Bridge.** Some beats are not there to be looked at. They are there to make something happen in the room, and they are shaped by that instead of by the content.

## 4.1 — Beats that are not slides

```yaml
id: room-break
layout: section-break
time_s: 10
```

## 4.2 — Asking the room

```yaml
id: the-discussion
layout: discussion
time_s: 90
```

**Claim.** Where would you expect this to break in your own work?

**Cue.** wait. actually wait.

## 4.3 — Setting up the work

```yaml
id: the-activity-setup
layout: activity-setup
time_s: 60
content:
  task: Pick one beat from your last talk and name the layout it should have used.
  example: |
    claim + figure    -> claim-above-figure
    one sentence      -> claim-only
    before vs after   -> two-up-compare
```

**Claim.** Tutorials get a setup beat and a parking beat, always as a pair.

## 4.4 — While people work

```yaml
id: the-activity-parking
layout: activity-parking
time_s: 300
content:
  instructions: >
    Open your last deck, find a slide you were not happy with, name the layout
    it should have used, and say what it would have cost you to write the claim
    in one sentence first.
  constraints:
    - 5 minutes
    - pairs
    - one slide each, not the whole deck
```

**Claim.** This is the one slide that must hold still and stay legible for ten minutes rather than animate.

# Section 5 — Where the catalog stops

> **Bridge.** Every catalog runs out. What matters is what happens at the edge — whether there is a way through it, and whether the deck can still hold what it could not fit.

## 5.1 — Where the catalog stops

```yaml
id: edges-break
layout: section-break
time_s: 10
```

## 5.2 — Something we have not built yet

```yaml
id: the-placeholder
layout: claim-above-figure
time_s: 40
visual:
  kind: referential
  sub: photo
  intent: a whiteboard covered in boxes and arrows, mid-argument
  asset: whiteboard.png
```

**Claim.** A deck with no assets at all still renders, because you have to watch a rough deck back before you know which assets are worth sourcing.

**On slide.**
- Missing assets are labelled, not fatal

## 5.3 — Out of the plane

```yaml
id: the-3d-split
layout: claim-above-figure
time_s: 40
scene_type: 3d
visual:
  kind: constructible
  sub: geometry
  intent: a surface that needs a camera with a third axis
```

**Claim.** A 3d beat forces its own scene, because the 2d runner cannot host one.

**On slide.**
- scene_type: 3d splits the scene

## 5.4 — Straight through the library

```yaml
id: the-raw-beat
layout: raw
time_s: 40
raw:
  class: CatalogDemo_Raw
  code: |
    class CatalogDemo_Raw(DeckScene):
        """raw beat: scene code the library never touches."""

        deck_path = str(DECK_PATH)
        beat_ids = ()

        def construct(self):
            from manim import Circle, Create, ManimColor, Text, VGroup

            from presenting_lib.tokens import PALETTE, TYPE

            self.camera.background_color = ManimColor(PALETTE.ground)
            self.camera.init_background()

            ring = Circle(radius=1.6, color=PALETTE.green.mid, stroke_width=6)
            label = Text("raw", font=TYPE.family_body, font_size=48,
                         color=PALETTE.ink)
            self.play(Create(ring))
            self.play(Create(label))
            self.wait(0.4)
            self.next_slide()
            self.play(VGroup(ring, label).animate.scale(0.6))
            self.wait(0.5)
```

**Note.** Hand-written on purpose. The library must not intercept it.

## 5.5 — Kept, not killed

```yaml
id: the-backup
layout: claim-above-figure
time_s: 40
backup: true
demoted_because: good on its own but it broke the run into the last section
visual:
  kind: constructible
  sub: graph
  intent: the demoted beat, still here
  graph:
    rankdir: LR
    nodes:
      - {id: kept, label: still yours}
    edges: []
```

**Claim.** A demoted beat keeps its reason, moves after the outro, and says "Backup" in the footer.

**On slide.**
- Demotion, not deletion
