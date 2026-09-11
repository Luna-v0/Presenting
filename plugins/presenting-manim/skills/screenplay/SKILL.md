---
name: screenplay
description: Use to turn a brief into a deck's screenplay.md, or to revise one section of an existing screenplay after a review. Triggers on "write the screenplay", "turn the brief into beats", "section 3 didn't land", "redo the middle", or any request to add, cut, reorder or rewrite beats. This is the only place beats are written — never hand-edit generated scene code instead.
---

# Screenplay

`brief.md` → `decks/<slug>/screenplay.md`. Two modes: full generation, and
**section-scoped revision** (see below). The screenplay is the artifact the user
keeps: it has to read as a document in six months and parse for the compiler.

## Before writing anything

```bash
cd manim-videos
uv run python -c "
from presenting_lib.brief import require
from presenting_lib.slots import budget_for
b = require('decks/<slug>/brief.md')
print(b.genre, b.target, b.interaction, b.duration_min, b.rules)
print('claim budget:', budget_for(b.target, 'claim-above-figure', 'claim'))
"
```

Read `identity/budgets.json` for your target. **Over budget is a defect**, not a
style note — the compiler raises `SlotOverflow` and the deck will not build.

## Sections come from the Narrative

Derive them from the brief's `Narrative`, not from a table of contents. Every
section carries a **Bridge**: one sentence stating the logical connection from
the previous section. Not a scripted phrase — the joint itself. Section one's
bridge states the opening frame instead.

**If you cannot write the bridge, the order is wrong.** Say so and propose a
reorder. Do not invent a connective to paper over it. This is the single most
useful check in the format: structure is not story, and a deck can follow
Context → Problem → Approach without the steps actually flowing.

## The four prose fields

| Field | What it is | Rule |
|---|---|---|
| `Note` | the user's planning intent | **Verbatim.** Never rewritten, tidied, translated or merged. |
| `Claim` | one sentence: what the beat asserts | **Never spoken, never shown.** This is what you reason with. |
| `On slide` | fragments, derived by compressing `Claim` | What actually renders. Must fit the budget. |
| `Cue` | the user's delivery shorthand | **Verbatim, any language.** Never expand into prose. |
| `Skip` | deliberately not said | Stops the beat re-growing later. |

Full sentences on screen belong only in `claim-only` and `callout`. Everywhere
else, `On slide` is fragments.

There is no `Say` field. The user's notes are keywords; there is nothing to
compress into a spoken sentence. The guard against slides-as-documentation is
`Claim` → `On slide` plus the measured budget.

**All on-slide text is English.** No per-deck override. The user may speak
Portuguese over English slides; that only affects `Cue`, which may be in any
language.

## Figures over text, always

A beat with a full text slot and an empty visual slot is a defect. For anything
conceptual, **a constructed diagram beats a sourced photo** — reach for
`constructible` first. Photos are for scene-setting and for showing a real thing.

Never generate photographic or referential imagery. The user sources PNGs by
hand and considers being asked a feature; record the ask in `visual.intent` and
let `shot-list` turn it into a request.

## Gates

- **Discussion beats**: only when the brief allows them. Never in a `showcase` —
  a showcase with a discussion prompt is a failed showcase. Never when
  `interaction: none`. Place them where they earn it: after a framework is
  introduced and before it is applied; at a genuine open question; where the
  user wants to be argued with. Never because time has passed.
- **Activity blocks**: `genre: tutorial` only, and always as a pair —
  `activity-setup` then `activity-parking`. See
  [references/activities.md](references/activities.md).
- **Accents**: the encoding is **positional, not valenced**. Green is the first
  of two things being related; yellow is the second. Green does not mean good
  and yellow does not mean warning.

  Use them when a beat relates two things to each other — two terms of a formula
  being explained against each other is the case they exist for. A beat marking
  only *one* thing uses green. **Never use yellow alone**: it means "the second
  of two" and without a first the beat has lost half its point.

  Never introduce a third colour. If a beat seems to need one, it is two beats.
  The meanings live in `identity/tokens.yaml`; clear one and `validate` starts
  refusing generated beats that use an accent again.

## Time

Every beat carries `time_s`. Budget to **85% of the slot** — nobody finishes
early. Overrun resolves by **demotion, not deletion**: set `backup: true` and
record `demoted_because` in the user's own framing.

## Flag these, every time

- a beat with full text and `visual.kind: none`
- two beats making the same point
- a beat assuming something no earlier beat established
- a section whose beats do not deliver what its bridge promised

The full list is in [references/review-checklist.md](references/review-checklist.md)
so it can be run standalone against an existing screenplay.

## Section-scoped revision

"Section 3 didn't land" regenerates that section's beats against the narrative
and touches nothing else. Sections are the natural unit because they are already
the narrative's joints.

```bash
cd manim-videos
uv run python -c "
from presenting_lib import screenplay as sp, revise
deck = sp.load('decks/<slug>/screenplay.md')
print([b.id + ' ' + b.origin for b in revise.section_scope(deck, '<section>').beats])
"
```

- `origin: generated` — rewrite freely.
- `origin: human` — **propose, never apply.** Show the proposal and let the user
  decide. Without this the second pass eats the fixes from the first.
- Set `origin: human` whenever the user dictates content for a beat.
- Keep beat `id`s stable. They are identity: assets and review verdicts key off
  them, and a renumber breaks every path.

## Writing a beat by hand

When the catalog does not cover what the beat needs, `layout: raw` hands it
straight to manim — either reusing a scene that already exists, or with the
scene written inline in the screenplay. Raw beats keep their timing, section,
id, and place in review; they only skip the layout. See
[references/hand-written-beats.md](references/hand-written-beats.md).

Offer this rather than bending a layout that is only almost right, and do not
treat it as a last resort — a library that cannot be stepped around gets
abandoned.

## Format

See [references/format.md](references/format.md) for the full beat schema and a
worked example. Check your work:

```bash
cd manim-videos
uv run python -c "
from presenting_lib import screenplay as sp, compile as C
d = sp.load('decks/<slug>/screenplay.md')
[print(f) for f in C.validate(d)]
"
```

Zero errors before handing off to `shot-list`.
