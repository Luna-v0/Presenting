---
name: presentation-brief
description: Use whenever a new talk, deck, presentation, lecture, tutorial or defense is being planned in this repo — including when the user hands over a whiteboard photo, a rough outline, a paper, or just a topic and a date. Produces a brief.md in the deck's own directory, the artifact every later stage reads. Run this before writing any screenplay or scene code; a deck without a brief has no narrative to check its beats against.
---

# Presentation brief

Produce `decks/<slug>/brief.md`. Everything downstream reads it.

The primary field is **Narrative** — setup, turn, landing, in broad steps. It is
the reason this stage exists. A narrative is checkable against beats in a way
that "a talk about NLHF" is not, and the sections of the screenplay fall out of
it rather than being negotiated separately.

Presentations are storytelling. Structure is not story: following
Context → Problem → Approach does not mean the steps flow.

## Warm start — a whiteboard photo (the default)

The photo comes first. Correcting a wrong reading is faster than answering an
open question from a blank page, and both land on the same brief.

In this order, and do not merge the steps:

1. **Transcribe.** Literally what is on the board. Boxes, arrows, text, what is
   circled, what is crossed out, how things are arranged in space. No
   interpretation at all in this step.
2. **List what is unreadable.** Ask about each one. **Never guess handwriting.**
   A misread word becomes a beat, then a slide, then something said out loud.
3. **Interpret** — separately, and labelled as interpretation. Show the
   reasoning, so a wrong reading is correctable rather than invisible.
4. **Propose a narrative** — setup, turn, landing — as *a reading of the board*.
5. **Then** ask about the gaps in the story. Not about the form.

Boxes and arrows on a whiteboard are almost always
`visual.kind: constructible`, `sub: graph`. One photo often seeds both the
structure and the first diagrams, so record what each box and edge is.

## Cold start — no photo

Interview. Do not draft. Ask about:

- Why present this, to these people, now?
- What should they be able to do or believe afterwards?
- What is the story — what changes between the first minute and the last?

Then settle the frontmatter: genre, target, technicality, duration, series.

## Run the interview even when a draft exists

The user wants it. Its job on a draft is **not** to collect facts already on the
board. It is to establish the narrative the board only implies, and to find
where the story breaks.

## Audience-first pushback is a duty

Flag content that is there because the user wants to cover it rather than
because this audience needs it. Say which it is and why. They expect this; their
own decks make the same argument.

## Rules of engagement

- At most **three questions per turn**.
- If they say "just draft it", draft it immediately and stop asking.
- Never rewrite what they said. Their phrasing carries into `Note` and `Cue`
  later, verbatim.

## The file

```markdown
---
slug: nlhf-lab-talk
title: Feedback without humans
target: manim                # manim | slides
genre: research-talk         # research-talk | showcase | tutorial | defense | lecture
technicality: 4              # 1..5 — how much math, architecture, implementation
interaction: organic         # none | organic | structured
duration_min: 25
audience: LARA lab meeting — mixed background, some RL, little NLHF
narrative_frozen: false
---

## Narrative
They arrive assuming preference data is unproblematic.
The cycle example breaks that.
They leave needing an alternative to BT — and I have one to show.

## Why I'm presenting
...

## What the audience should do
...

## Series
...

## Out of scope
...
```

`technicality` is one number. There is no separate conceptual axis.

`genre` gates what later stages may generate:

| Genre | Discussion beats | Activity blocks | Emphasis |
|---|---|---|---|
| `research-talk` | yes | no | open questions, doubts |
| `showcase` | **never** | no | intuitive ideas, the pitch |
| `tutorial` | no | **yes** | sequence, mechanics, demos |
| `defense` | no | no | method and results |
| `lecture` | yes | sometimes | conceptual depth |

`narrative_frozen: true` stops the review loop from reopening the story. Set it
when the narrative is settled and only the beats are still moving.

## Check it

```bash
cd manim-videos
uv run python -c "from presenting_lib.brief import require; require('decks/<slug>/brief.md')"
```

## Then

Hand off to the `screenplay` skill. Do not write scene code here.
