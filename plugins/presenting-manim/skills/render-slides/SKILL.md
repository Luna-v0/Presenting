---
name: render-slides
description: Build a deck as a .pptx — "make the slides", "I need a PowerPoint", a brief with target slides. Writes a plain python-pptx script for that deck. Needs no repository, no venv and no manim; the only dependency is python-pptx, so it runs anywhere including a bare chat sandbox. Read "What broke" before writing anything.
---

# Render (slides)

Read the screenplay, write a Python script, run it, check it.

```bash
python build_pptx.py
```

**Nothing here touches the repository.** No `cd`, no `uv run`, no
`presenting_lib`, no `identity/` files, no manim. The only dependency is
`python-pptx` (`pip install python-pptx`). Everything else this stage needs —
the palette, the type scale, the budgets, the conventions — is written into this
skill. That is deliberate: a pptx is the one artifact that should be buildable
from a plain Python environment, and coupling it to the repo made it the hardest
part of the pipeline to run rather than the easiest.

If a screenplay exists, read it. If not, the beats can come straight from the
conversation.

## Slides are not the manim deck

They are different media and should look different. Do **not** import the manim
layout geometry, do not convert manim units to inches, do not reproduce a beat's
manim composition slide-for-slide. Work in PowerPoint's own terms — inches,
points, text boxes, native shapes — and lay each slide out the way a good slide
would be laid out.

What carries across is the **identity and the content**. Not the rectangles.

## What broke, and the rules that follow

An earlier version generated a template with one named slide layout per catalog
entry, cloning `slideLayout` parts at the XML level because python-pptx has no
API for adding a layout. It round-tripped cleanly through python-pptx and
**would not open in PowerPoint**.

1. **Never do XML surgery.** No cloned layouts, no hand-built `<p:sldLayout>`,
   no editing theme parts. Use the stock **Blank** layout and add shapes to it.
2. **No abstraction.** A pptx is generated once and then edited by hand;
   regenerating throws those edits away. A readable script the user can open and
   change beats a renderer they would have to learn. When a deck needs something
   unusual, edit that deck's script.

Idioms, all tested:
[references/pptx-recipes.md](references/pptx-recipes.md).

## The identity

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

**Two accents, positional and not valenced.** Green is the first of two things
being related, yellow the second — two terms of a formula explained against each
other is the case they exist for. Green alone when a beat marks one thing.
**Never yellow alone.** Never a third colour; if a beat seems to need one, it is
two beats.

**Type**, in points on a 13.333 × 7.5 in slide:

| step | pt | use |
|---|---|---|
| display | 68 | title slide, section breaks |
| title | 52 | slide titles |
| claim | 40 | the one-line claim |
| body | 28 | list items, definitions |
| caption | 22 | attributions, footer |

**Fonts: Times New Roman and Courier New.** A pptx names one font and the
opening machine either has it or silently substitutes — and decks get presented
from borrowed laptops. These are on every Windows and Mac, and are metric-
compatible with the faces the manim target uses.

Character budgets, measured. Over these and it will not fit:

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

## Composing

Centred bold title with a thin green rule beneath, **sized to the title** rather
than a fixed width; section name lower left and slide number lower right, both
muted and small. Section breaks and single-statement slides get no chrome.

**Let text breathe.** Centre a short block in its space rather than pinning it to
the top — empty space under a two-line list reads as unfinished.

Use the beat's `layout` name as a description of intent, not a spec. The
workhorse is a claim across the top with a figure under it; expect most beats
there. A progressive list **expands into sibling slides**, one per item —
near-identical consecutive slides are correct.

**Draw diagrams with native pptx shapes**, not by embedding a rendered image.
They stay editable in PowerPoint afterwards, which is the whole point of
shipping a pptx. An arrow or leader must stop at the **edge** of what it points
at, never run into the middle of a label.

**`raw` beats are a manim escape hatch — skip them.** If the slides deck needs
what one shows, draw it with shapes or ask for an image.

## Content rules from the format

- **Speaker notes are directives**, built from `Claim` and `Note` — things to
  *do*: position, emphasise, contrast, frame. Never sentences to read aloud.
  **`Cue` never ships in speaker notes**; it is the user's private shorthand.
- **`Note` and `Cue` are verbatim** wherever they appear. Never reworded.
- **What renders is `On slide`, not `Claim`.** The claim states what the beat
  asserts so the arc can be checked; it never appears on screen. The exceptions
  are the single-statement layouts, whose job is to hold one sentence.
- **Attribution** goes under the figure in caption style.

## Regeneration destroys hand edits

Generation is one-shot. Re-running the script produces a **new file**; anything
edited in PowerPoint or Google Slides is lost. Say this before they start
editing, not after. If they want to keep editing in Slides, that is the end of
the pipeline for that deck — say so plainly rather than implying a round trip.

## Check it. python-pptx reading its own output is not a check.

That circularity is exactly what shipped a file PowerPoint would not open.

1. Reopen with python-pptx: slide count, and the text you expect where you
   expect it.
2. **If LibreOffice is available**, render it — a genuinely independent
   implementation. If it cannot open the file, PowerPoint almost certainly
   cannot either.

   ```bash
   soffice --headless --convert-to pdf --outdir /tmp deck.pptx
   pdftoppm -png -r 60 -f 1 -l 12 /tmp/deck.pdf /tmp/page
   ```

   Then **look at the pages.** Overflow, overlap, missing content and bad
   spacing all show up there and nothing else will tell you.
3. **Ask the user to open it once** in PowerPoint or Google Slides, and say why.
   LibreOffice agreeing is strong evidence, not the same renderer.

## Drive

**By hand — the user uploads it themselves.** Settled; do not offer to automate
it and do not ask again. Hand them the file path and stop. Never upload a deck
anywhere: it is outward-facing, and a talk in progress is not yours to publish.
