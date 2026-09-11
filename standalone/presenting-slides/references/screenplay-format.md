# The screenplay

Markdown. Readable as a document in six months, and structured enough to build
from. Sections are `#`, beats are `##`, and a small YAML block carries the
beat's fields.

````markdown
---
title: Feedback without humans
subtitle: An alternative to Bradley-Terry
author: ...
duration_min: 25
genre: research-talk
---

# Section 2 — The assumption nobody states

> **Bridge.** Part 1 ended with the loop working. The obvious next question is
> what the reward model is actually assuming — which is where it breaks.

## 2.1 — Preferences form a cycle

```yaml
layout: claim-above-figure
time_s: 90
visual:
  kind: constructible
  intent: three items in a preference cycle, A>B>C>A, cycle edge accented
```

**Note.** whiteboard: the triangle with the arrow going back — this is the whole point

**Claim.** Bradley-Terry assumes preferences are transitive, and human preferences are not.

**On slide.**
- A ≻ B ≻ C ≻ A

**Cue.** the pizza thing / ask who's voted in a runoff

**Skip.** The Luce axioms. Not needed for the argument.
````

## Fields

| field | meaning |
|---|---|
| `layout` | which shape of slide — see below |
| `time_s` | estimated seconds |
| `backup` | true when demoted; keep `demoted_because` alongside |
| `visual.kind` | `constructible` (draw it) · `referential` (a real image) · `chart` · `none` |
| `visual.intent` | what it must accomplish, not which file |

`Skip` records what you deliberately will *not* say, which stops a beat
re-growing later.

## Layouts

Descriptions of intent, not a spec — lay each one out the way a good slide would
be laid out.

| name | what it is |
|---|---|
| `title-card` | title, subtitle, author, affiliation, date. No chrome. |
| `section-break` | the section name, large and centred, nothing else. |
| `claim-only` | one sentence, centred, room around it. |
| `callout` | one sentence inside a rule — a thesis or a warning. |
| `claim-above-figure` | claim across the top, figure under it. **The workhorse — expect most beats here.** |
| `build-list` | a list revealed one item at a time → sibling slides. |
| `two-up-compare` | two labelled halves. Comparison is its own layout; doing it with two beats loses the comparison. |
| `term-reveal` | the term alone, then its definition on the next slide. |
| `equation-annotated` | a formula with up to two annotation boxes in the accent tints. |
| `table-accented` | a table with one row or column marked. |
| `figure-with-callouts` | a figure with up to three boxes beside it, leaders stopping at the box edge. |
| `discussion` | one prompt, nothing else. **Never in a showcase.** |
| `activity-setup` / `activity-parking` | tutorials only: the task, then the instructions that stay up while people work. |
| `backup` | anything, marked "Backup" in the footer. |

## Where the text comes from

**What renders is `On slide`, not `Claim`.** The claim is one sentence stating
what the beat asserts; it exists so the arc can be checked and the slide text
derived from it, and it never appears on screen.

The exceptions are `claim-only` and `callout`, whose whole job is to hold one
sentence.

`Note` and `Cue` never appear on a slide at all. `Note` may go into speaker
notes verbatim; `Cue` never does.

## Checking a screenplay

- Does every section have a bridge that is a real logical connection?
- Do the beats deliver what the bridge promised?
- Is any beat assuming something no earlier beat established?
- Do two beats make the same point?
- Any beat with full text and no visual?
- Is `On slide` fragments rather than sentences?
- Is every `Note` and `Cue` byte-identical to what they wrote?
- Does the total sit inside 85% of the slot? If not, which beats get demoted?
