---
name: presenting-slides
description: Build a presentation as a .pptx — from a whiteboard photo, a topic, or an existing outline. Use when someone wants slides, a deck, a talk, a PowerPoint, or a Google Slides file. Runs anywhere Python and python-pptx are available; needs no repository and no local tooling. Covers the whole path: working out the story, writing the beats, then generating the file.
---

# Presenting — slides

Three stages, and the first two are just conversation and markdown:

1. **Brief** — what story is this talk telling?
2. **Screenplay** — the beats, with the claim and the visual for each.
3. **Build** — a Python script using `python-pptx`, run in the code sandbox,
   producing a file to download.

Only stage 3 needs anything installed, and only `python-pptx`. If the user just
wants slides from content they have already, skip to stage 3 — but read the
brief section first, because "what is the story" is worth two minutes even then.

## 1. The brief

Presentations are storytelling. Structure is not story: following
Context → Problem → Approach does not mean the steps flow.

The one thing worth getting: **the narrative** — setup, turn, landing, in broad
steps. It is checkable against the beats in a way that "a talk about X" is not,
and the sections fall out of it.

**If they give you a whiteboard photo, in this order:**

1. **Transcribe.** Literally what is on the board — boxes, arrows, text, what is
   circled, what is crossed out, how it is arranged. No interpretation.
2. **List what is unreadable, and ask.** Never guess handwriting: a misread word
   becomes a beat, then a slide, then something said out loud.
3. **Interpret** — separately, labelled as interpretation, with the reasoning
   shown so a wrong reading is correctable.
4. **Propose a narrative** as a reading of the board.
5. **Then** ask about gaps in the story, not the form.

Otherwise interview: why present, to whom, what should they be able to do
afterwards, what changes between the first minute and the last. **At most three
questions per turn**, and if they say "just draft it", draft it.

Also settle: duration, and genre — `research-talk`, `showcase`, `tutorial`,
`defense`, `lecture`. Genre gates content: a **showcase never gets a discussion
prompt**, activities are for tutorials.

**Push back on audience grounds.** Flag anything that is there because they want
to cover it rather than because this audience needs it.

## 2. The screenplay

Beats, in sections. Every section carries a **bridge**: one sentence stating the
logical connection from the previous section. Not a transition phrase — the
joint itself. **If you cannot write the bridge, the order is wrong**; say so and
propose a reorder rather than inventing a connective.

Each beat has:

- **Claim** — one sentence, what the beat asserts. **Never goes on the slide**
  and is never spoken. It exists so the arc can be checked and the slide text
  derived from it.
- **On slide** — fragments compressed from the claim. Full sentences only on a
  single-statement slide.
- **Note / Cue** — the user's own words. **Verbatim, always.** Never reworded,
  tidied, translated or merged. `Cue` is delivery shorthand and stays private.
- **Visual** — what it must accomplish, not which file.

**Figures over text, always.** A beat with a full text slot and no visual is a
defect. For anything conceptual a constructed diagram beats a stock photo — and
in pptx you can draw one with native shapes, which stays editable afterwards.

**Decks are never documentation.** Not even tutorials. A companion handout is a
separate thing the user writes.

Budget beats to **85% of the slot** — nobody finishes early. When it overruns,
**demote, do not delete**: mark the beat as backup, move it after the outro, and
record *why* in the user's own words. That sentence is what makes it findable
next talk. Cutting something they like is the thing they will resist, and
bending the story to keep it is the failure mode — name it out loud.

Format details: [references/screenplay-format.md](references/screenplay-format.md).

## 3. Build the file

Write a plain Python script and run it. **No framework, no template, no shared
renderer** — a pptx is generated once and then edited by hand, so a readable
script beats an abstraction.

```python
# pip install python-pptx  (in the code sandbox)
from pptx import Presentation
from pptx.util import Inches, Pt
```

**Never do XML surgery.** No cloned slide layouts, no hand-built `<p:sldLayout>`,
no editing theme parts. Use the stock **Blank** layout and add shapes to it. An
earlier attempt cloned layouts at the XML level, round-tripped cleanly through
python-pptx, and would not open in PowerPoint.

Idioms and a worked example:
[references/pptx-recipes.md](references/pptx-recipes.md).

### The identity

| | |
|---|---|
| ground (slide background) | `#E4DCC6` |
| ink (all body text) | `#232A24` |
| muted (captions, footer) | `#5F5A4B` |
| structure fill / stroke | `#CFC6AE` / `#8C8470` |
| green tint / mid / dark | `#CCE0C6` / `#3D6349` / `#1E3527` |
| yellow tint / mid / dark | `#F6E5A5` / `#A87F20` / `#55400E` |

**Pairing is not optional.** An accent fill carries its own `dark` text; ground
and structure carry `ink`. **No light text on a dark fill anywhere.**

**Two accents, and they are positional, not valenced.** Green is the first of two
things being related, yellow the second — two terms of a formula explained
against each other is the case they exist for. Green alone when a beat marks one
thing. **Never yellow alone.** Never a third colour; if a beat seems to need one,
it is two beats.

**Type**, in points on a 13.333 × 7.5 in slide:

| step | pt | use |
|---|---|---|
| display | 68 | title slide, section breaks |
| title | 52 | slide titles |
| claim | 40 | the one-line claim |
| body | 28 | list items, definitions |
| caption | 22 | attributions, footer |

**Fonts: Times New Roman and Courier New.** A pptx names one font and the opening
machine either has it or silently substitutes — and decks get presented from
borrowed laptops. These are on every Windows and Mac.

### Composing

Centred bold title, a thin green rule beneath sized to the title rather than
fixed width; section name lower left and slide number lower right, both muted and
small. Section breaks and single-statement slides get no chrome.

**Let text breathe.** Centre a short block in its space rather than pinning it to
the top — empty space under a two-line list reads as unfinished.

A progressive list **expands into sibling slides**, one per item revealed.
Near-identical consecutive slides are correct here.

**Speaker notes are directives**, built from the claim and the note — things to
*do*: position, emphasise, contrast, frame. Never sentences to read aloud, and
**never the cue**.

Character budgets, measured — over these and it will not fit:

| layout | budget |
|---|---|
| `title-card` | title 64, subtitle 128, author 154, affiliation 77, date 77 |
| `section-break` | section 64 |
| `claim-above-figure` | claim 145, caption 93 |
| `build-list` | claim 145, items 1037 total |
| `claim-only` | 616 |
| `callout` | 472 |
| `two-up-compare` | label 36 each |
| `term-reveal` | term 49, definition 976 (541 beside a figure) |
| `equation-annotated` | annotation 311 each |
| `figure-with-callouts` | callout 122 each |
| `discussion` | prompt 496 |

## Check it, then hand it over

python-pptx reading its own output proves only that python-pptx can read what
python-pptx wrote. That circularity is exactly what shipped a file PowerPoint
would not open.

1. Reopen with python-pptx: slide count, and the text you expect where you
   expect it.
2. If LibreOffice is available, convert to PDF and **look at the pages** —
   overflow, overlap and missing content all show there:
   `soffice --headless --convert-to pdf --outdir /tmp deck.pptx`
3. **Ask the user to open it once** in PowerPoint or Google Slides, and say why.
   Nothing else available is the same renderer.

Regeneration produces a **new file**; anything they edit in PowerPoint is lost.
Say so before they start editing, not after.

Never upload the deck anywhere. Hand them the file.
