# The screenplay format

Markdown with just enough structure to parse. H1 is a section, H2 is a beat, a
fenced `yaml` block after the beat heading carries its fields, and bold-labelled
paragraphs carry the prose.

````markdown
---
slug: nlhf-lab-talk
title: Feedback without humans
subtitle: An alternative to Bradley-Terry
author: ...
affiliation: ...
date: "2026"
target: manim
duration_min: 25
brief: ./brief.md
---

# Section 2 — The assumption nobody states

> **Bridge.** Part 1 ended with the loop working. The obvious next question is
> what the reward model is actually assuming — which is where it breaks.

## 2.1 — Preferences form a cycle

```yaml
id: preference-cycle
origin: generated
layout: claim-above-figure
time_s: 90
transition: cut
visual:
  kind: constructible
  sub: graph
  intent: three items in a preference cycle, A>B>C>A, cycle edge accented
```

**Note.** whiteboard: the triangle with the arrow going back — this is the whole point

**Claim.** Bradley-Terry assumes preferences are transitive, and human preferences are not.

**On slide.**
- A ≻ B ≻ C ≻ A

**Cue.** the pizza thing / ask who's voted in a runoff

**Skip.** The Luce axioms. Not needed for the argument.
````

## Beat fields

| Field | Values |
|---|---|
| `id` | stable slug, unique per deck. Identity, not position. |
| `origin` | `generated` \| `human` |
| `layout` | a catalog name, or `raw` |
| `time_s` | int, estimated seconds |
| `transition` | `cut` (clear the previous beat) \| `build` (keep it) |
| `scene_type` | `2d` \| `3d` — `3d` forces a scene split |
| `visual.kind` | `constructible` \| `referential` \| `chart` \| `none` |
| `visual.sub` | `graph` `axes` `geometry` `equation` `process` `timeline` / `photo` `paper-figure` `screenshot` |
| `visual.intent` | free text: what it must accomplish, not which file |
| `visual.asset` | path, once one exists |
| `visual.graph` | inline node/edge spec — see below |
| `visual.data` | inline chart spec — see below |
| `backup` | bool |
| `demoted_because` | why it was demoted, in the user's framing |
| `verdict` | `keep` \| `demote` \| `narrative-wrong` — transient, written by review |
| `content` | explicit slot values; wins over every default mapping |
| `raw` | `scene: module:Class` or `code: |` — only with `layout: raw` |

## What lands in which slot

`content:` always wins. Otherwise:

| Layout | Default mapping |
|---|---|
| `title-card` | the deck's frontmatter |
| `section-break` | the enclosing section's name |
| `claim-only` | `claim` ← `Claim` (a full sentence, deliberately) |
| `callout` | `statement` ← `Claim` |
| `discussion` | `prompt` ← `Claim` |
| `build-list` | `items` ← the `On slide` bullets |
| `term-reveal` | `term` ← first bullet, `definition` ← `Claim` |
| `activity-setup` / `activity-parking` | `task` / `instructions` ← `On slide` |
| everything else | `claim` ← `On slide` (fragments), `visual` ← `visual:` |

## Line breaks in YAML content

`fit_text` honours explicit newlines as hard breaks — a screenplay that wrote a
line break meant it. So the scalar style matters:

```yaml
content:
  instructions: >          # folded: newlines become spaces. Use this for prose.
    One long sentence that the library is free to wrap wherever it fits.

  example: |               # literal: newlines are kept. Use this for code.
    pref = load("toy.jsonl")
    fit(pref, model="bt")
```

Using `|` for prose is the common mistake: it produces ragged, hand-broken lines
that ignore the slot width.

## The layout catalog

| Name | Chrome | Slots |
|---|---|---|
| `title-card` | bare | title, subtitle, author, date, affiliation |
| `section-break` | bare | section |
| `claim-only` | bare | claim |
| `full-bleed-figure` | none | visual |
| `claim-above-figure` | full | claim, visual, caption — **the workhorse** |
| `figure-with-callouts` | full | visual, callout×3 |
| `two-up-compare` | full | label_l, panel_l, label_r, panel_r |
| `build-list` | full | claim, items |
| `term-reveal` | full | term, definition, visual? |
| `equation-annotated` | full | equation, annotation×2 |
| `table-accented` | full | claim, table |
| `callout` | bare | statement |
| `discussion` | bare | prompt |
| `activity-setup` | full | task, example? |
| `activity-parking` | full | instructions, constraints |
| `backup` | full | delegates to another layout, plus a stripe |
| `raw` | declared | — |

Chrome tiers: `full` = centered title, green rule, footer with section name and
progress dots. `bare` = content only. `none` = nothing at all.

## Diagrams

Graphviz positions; the library draws. Node declaration order is the reveal
order.

```yaml
visual:
  kind: constructible
  sub: graph
  intent: the PPO/DPO family tree, revealed branch by branch
  graph:
    rankdir: TB              # TB | LR | BT | RL
    nodes:
      - {id: ppo, label: PPO}
      - {id: grpo, label: GRPO}
    edges:
      - {from: ppo, to: grpo}
```

Scope honestly: this handles graphs. Not a hand-composed spatial figure, not a
paraboloid. Those are `raw` beats or draw.io.

## Charts

```yaml
visual:
  kind: chart
  intent: proxy reward against gold reward as optimisation continues
  source: Gao et al. 2023, figure 3
  data:
    kind: line               # line | bar | scatter
    x: [0, 1, 2, 3]
    series:
      proxy: [0, 1, 2, 3]
      gold: [0, 1, 1.2, 0.9]
    accent: gold             # the one series the beat is about
    xlabel: KL budget
    ylabel: reward
```

A chart earns its place if the beat spends time on it. Otherwise it is backup.

## The escape hatch

```yaml
id: bt-elo-anim
layout: raw
time_s: 60
raw:
  scene: scenes.bradley_terry_elo:BradleyTerryToElo
  class: FtV2_BTAnim
```

or `raw.code:` with a scene class written inline. Raw beats still carry timing,
sections and review; they only skip slot validation. A library that cannot be
stepped around gets abandoned — hard topics will need things the catalog does
not cover.
