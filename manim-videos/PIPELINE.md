# The Presenting pipeline

The repo already automated screenplay → manim scene code. That is the cheap
step. This is the expensive one: deciding what the story is, keeping text
legible, sourcing visuals, staying inside the slot, looking like one person made
it — and going back and fixing it after seeing it run.

```
whiteboard photo ──┐
                   ├──> brief ──> screenplay ──> shot list ──> render ──┬── manim  (manim-slides + library)
topic (interview) ─┘      ▲            ▲                                └── slides (pptx → Drive)
                          │            │                                        │
                          └── deck-review ◀────────────────────────────────────┘
```

**The loop is the point.** Judgement about whether a talk works comes from
watching it back, not from reading a plan. A one-directional pipeline puts the
artifact that produces the insight at the very end with no way to carry it back.

## Where things live

| Path | What |
|---|---|
| `identity/tokens.yaml` | the single source of colour, type and geometry |
| `identity/export_*.py` | tokens → beamer `.sty`, draw.io styles, `.mplstyle`, reveal.js template |
| `identity/budgets.json` | measured character budget per target, layout and slot |
| `identity/legibility.md` | where `min_legible_body` came from |
| `presenting_lib/` | tokens, slots, chrome, the layout catalog, diagrams, tables, charts, the compiler — the **manim** target |
| `decks/<slug>/` | `brief.md`, `screenplay.md`, `SHOTS.md`, `assets/`, `out/` |
| `scripts/measure_slots.py` | re-measure budgets; `--calibrate` renders the legibility ladder |
| `scripts/extract_frames.py` | one settled frame per slide, for review |
| `scripts/review_deck.py` | the mechanical review pass |
| `scripts/contact_sheet.py` | frames tiled six to a page, labelled — for looking |
| `scenes/` | hand-written scenes, unchanged and still rendering |
| `plugins/presenting-manim/skills/` | the six pipeline skills |

## A deck, end to end

```bash
cd manim-videos

# 1. brief — the `presentation-brief` skill writes decks/<slug>/brief.md

# 2. screenplay — the `screenplay` skill writes decks/<slug>/screenplay.md
uv run python -c "
from presenting_lib import screenplay as sp, compile as C
d = sp.load('decks/<slug>/screenplay.md'); [print(f) for f in C.validate(d)]"

# 3. shot list — asks the human for what only they can supply
uv run python -c "
from presenting_lib import screenplay as sp, shots
shots.write(sp.load('decks/<slug>/screenplay.md'))"

# 4. compile and render
uv run python -c "
from presenting_lib.compile import compile_deck
print(compile_deck('decks/<slug>/screenplay.md', 'decks/<slug>/out/<slug>_scenes.py')[0])"
uv run manim-slides render decks/<slug>/out/<slug>_scenes.py <Scene> ... -qp

# 5. watch it back — this is where judgement enters
uv run manim-slides convert --one-file --offline \
    --use-template identity/out/revealjs.html \
    -ctransition="'fade'" -cbackground_transition="'fade'" \\
    -ctransition_speed="'fast'" <Scene> ... <slug>.html

# 6. review
uv run python scripts/extract_frames.py <Scene> ... --out media/review
uv run python scripts/review_deck.py decks/<slug>/screenplay.md --frames media/review

# 7. revise: write verdicts onto beats, then
uv run python -c "
from presenting_lib import screenplay as sp, revise, compile as C
d = sp.load('decks/<slug>/screenplay.md')
[print(c) for c in revise.apply_verdicts(d, C.load_brief(d)).changes]
sp.save(d)"
```

## The five failures this design exists to prevent

Each has a hard failure attached, because silence is what let them through.

| Failure | The guard |
|---|---|
| Text renders off-frame and manim exits zero | `Slot.fit_text` shrinks only to the legibility floor, then raises `SlotOverflow` naming the slot, the length and the budget |
| A tint gets paired with the wrong text colour | Colour is exposed as `Surface` and `Ramp`, never loose hex. Handing green tint to a text call with `ink` raises |
| An agent improves the human's words | `Note` and `Cue` round-trip byte for byte, and there is a test for it |
| A slide is correct in code and unreadable on screen | `review_deck.py` measures contrast inside the exact rectangles the library placed text in |
| A revision pass eats the human's edits | `origin: human` beats are proposed against, never rewritten |

A sixth has no automated guard and never will: **a slide that measures clean and
still reads badly.** Overlapping content after a `build`, a leader running
through the box it points at, a marker nobody recognises. `contact_sheet.py`
exists to make looking cheap enough that it actually happens — six frames a
page, each labelled with its beat id and `Claim`. Looking is the check, and
`plugins/presenting-manim/skills/deck-review/references/looking-at-slides.md`
lists what it catches — every entry there is a defect that shipped past the
mechanical pass on a real deck.

## The two targets are not the same thing

The manim target is library-driven: rendered over and over, geometry identical
across dozens of beats, covered by tests. `presenting_lib` exists for it.

The slides target has **no renderer and no template**. The `render-slides` skill
writes a plain python-pptx script per deck, and that script lays the slides out
the way slides should be laid out rather than reproducing the manim
composition — they are different media and are meant to look different. What
carries across is the identity and the content, not the rectangles.

An earlier version did share geometry, through a generated template with one
named slide layout per catalog entry. It cloned `slideLayout` parts at the XML
level, round-tripped cleanly through python-pptx, and would not open in
PowerPoint. Both halves of that were mistakes: the XML surgery, and the coupling.

## How a beat change works

Worth knowing, because getting it wrong is invisible in still frames.

A manim-slides slide is a video that plays when you arrive at it. So anything
the compiler clears *before* that video starts is already missing from frame 0,
and the viewer sees the full previous slide, then a near-empty one, then the
content animating back in — a flicker on every beat change, on every slide,
while each individual frame looks perfect.

So the outgoing beat stays on screen into the incoming slide's video and leaves
*inside* it. Frame 0 then matches where the previous slide ended, the hand-off
between video elements is imperceptible, and the only transition is the one
that is actually animated. `review_deck.py --scenes` measures this: it compares
each slide's first frame against the previous slide's last.

Scene boundaries are the same problem one level up: separate manim scenes
cannot share mobject state, so a scene would start blank. Each one is therefore
*primed* — the previous beat is rebuilt and added with no animation before the
scene begins, so its first frame matches too.

With every hand-off continuous, the export needs no slide transition at all,
and deliberately has none. A dissolve on top would cross-fade two videos whose
content differs, which ghosts the letters. The only visible cut left is after a
`raw` beat, whose final state is code the library never saw.

## Identity

Settled by rendering and iterating. Do not re-derive.

- Sand ground `#E4DCC6`, ink `#232A24`, muted `#5F5A4B`.
- Structure boxes are sand-family on purpose: because they are quiet, an
  accented box reads as marked without the slide getting busy. If they vanish on
  a projector, push the **stroke** toward ink — never brighten the fill.
- Exactly **two accents**, green and yellow, each a three-value ramp. An accent
  fill carries its own `dark`. There is no light text on a dark fill anywhere.
- Both accents may appear on one beat when they mark genuinely different things
  — highlighting two terms of one formula is the primary case.

## Decisions

Five of the plan's six open questions are settled; the sixth has simply never
come up. Kept here because each one still explains why the code looks the way
it does.

1. ~~What green and yellow mean~~ — **settled, and the encoding is positional
   rather than valenced.** Green is the first of two things being related and
   the only accent to use when a beat marks one thing; yellow is the second,
   never used alone. Two terms of a formula being explained against each other
   is the case they exist for. The gate is not deleted: clear a meaning in
   `identity/tokens.yaml` and `compile.validate` starts refusing generated
   beats that use an accent again.
2. ~~Where decks live~~ — **settled: `manim-videos/decks/`.** A deck needs the
   layout library, the identity tokens, the measured budgets, the scripts and
   the venv, and all of those live here; moving decks up a level would put a
   directory boundary between a deck and everything that renders it, break
   `import presenting_lib` from the generated scene modules, and buy nothing.
   The thing that actually reads oddly is the *name* `manim-videos`, which is
   historical — it is the pipeline root now, and renaming it would invalidate
   every path in the READMEs, the plugin's MCP server config and every deck's
   generated commands, for cosmetics.
3. ~~Drive upload~~ — **settled: by hand.** `render-slides` prints the path and
   uploads nothing.
4. **Section name in the footer** — still not explicitly decided. It has been
   kept alongside the dots through every review round without anyone objecting
   to it, which is weak evidence rather than a decision. Say the word and it
   comes out.
5. ~~Type families~~ — **settled: Liberation, and for a portability reason
   rather than a visual one.** A talk often gets presented from a machine that
   is not yours, and a font that is not on it silently becomes something else.
   Liberation Serif is metric-compatible with Times New Roman and Liberation
   Mono with Courier New, so the pptx target names the Microsoft face and
   degrades to identical widths on any borrowed Windows or Mac. The manim
   target embeds rendered video, so its fonts are baked in either way.
   `min_legible_body: 22` was measured in Liberation Serif and stands.
6. ~~How `origin` gets flipped~~ — **settled: it is no longer a flag anyone has
   to remember.** A generated beat is stamped with a hash of its content; a beat
   whose content no longer matches its stamp was edited by a person, and a
   revision pass proposes against it instead of rewriting it. Setting
   `origin: human` by hand still works and still wins, but forgetting to no
   longer costs you the edit.

## Tests

```bash
cd manim-videos
uv run pytest tests/ -q
```

`tests/test_acceptance.py` is numbered to match the plan's acceptance table.
