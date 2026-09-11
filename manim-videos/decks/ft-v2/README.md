# ft-v2 — the migration reference

`screenplays/ft_v2.md` + `scenes/ft_v2.py` was the known-good hand-written deck.
This directory is the same talk ported to the v3 format and compiled through
`presenting_lib`, which is how the library was proven before anything else was
built on it.

```bash
cd manim-videos
uv run python -c "
from presenting_lib.compile import compile_deck
print(compile_deck('decks/ft-v2/screenplay.md', 'decks/ft-v2/out/ft_v2_scenes.py')[0])"
```

The generated module's header carries the render / present / convert commands.

## What the port established

- **Zero manual positioning** in the generated file: no `.next_to`, no
  `.shift`, no literal `font_size=`, no `.to_edge`. Everything through slots.
  Asserted by `tests/test_acceptance.py::test_01_...`.
- **Raw beats work as an escape hatch.** `bt-elo-anim` and `nlhf-anim` alias
  `scenes/bradley_terry_elo.py::BradleyTerryToElo` and `scenes/nlhf.py::NLHF`
  untouched, and still take part in timing, sections and review.
- **Graphviz-for-positioning works.** The hand-placed PPO family tree in the old
  file is now a node/edge spec; `dot -Tplain` positions it and the library draws
  it in the palette.
- **The bridge rule is workable.** Writing seven bridges by hand for a deck that
  never had them was the first real test of it, and it changed the section
  boundaries: the flat "Previously we talked about" run became one section with
  an opening frame, and "Why I mention Bradley-Terry" became "What Bradley-Terry
  actually assumes", which is what its beats actually deliver.

## Bugs the port found

All four were real, and none would have surfaced from reading the code:

1. The green rule was drawn at a fixed `y`, so a two-line title had a line
   through it.
2. `transition: cut` faded out the persistent footer and never restored it, so
   the chrome vanished after the first cut.
3. Manim renders an animation's frames over `[0, run_time)`, so every slide's
   video ended mid-draw — visible when presenting, not just in review. The
   compiler now holds each slide for `SETTLE_S` before the break.
4. The compiler emitted a trailing empty slide per scene.

## Differences from the original, on purpose

- **`bt-not-transitive` is rendered without accents.** It is the two-accent case
  — one term green, one yellow — and that is exactly what it wants. It stays
  neutral until `accents.*.meaning` is decided in `identity/tokens.yaml`,
  because an accent that means something different in every deck is worse than
  no accent.
- The old deck's `rlvr_tbd` placeholder slide ("more here later") is not ported.
  It was a hole in the screenplay, not a beat.
- Blocks (`ExampleBlock`, `RemarkBlock`, `AlertBlock`) became `build-list` and
  `callout` beats. The catalog has no block layout; a block was a way of
  grouping text, and the layouts group it by position instead.

## Comparing it against the original

Both versions are still renderable, so the comparison is available side by side:

```bash
cd manim-videos
# the port
uv run python scripts/extract_frames.py FtV2_01_WherePart1LeftOff ... --out media/review
# the original
uv run python scripts/extract_frames.py FtV2_01_Recap FtV2_02_RecapAfter \
    FtV2_03_Continuing FtV2_04_FeedbackNoHumans FtV2_05_WhyBT FtV2_06_NLHFIntro \
    FtV2_NLHFResults FtV2_07_NoMoreBT FtV2_08_Outro --out media/review-old
```

**Whether the port is "visually equivalent or better" is a judgement call, and
it is yours.** They do not share an identity: the original is white ground,
black serif, no chrome, with manim-beamer's camera zooming to fit each slide's
content — so a one-line title fills the frame. The port is on sand, with a
centered title, a green rule, a persistent footer, and a fixed camera, because
slot geometry needs one.

Two differences worth knowing before you look:

- The original's frames are **not** all comparable. `SlideShow` fades every
  mobject out at the end of a slide, so a good number of its extracted frames
  are blank or mid-fade. The port holds each slide on its settled state.
- The camera-fit behaviour is the thing the port deliberately gives up. It is
  what made text size unpredictable from slide to slide, and it is
  incompatible with "is this text inside the safe area" being a question the
  library can answer.

## The brief is reconstructed

`brief.md` was written *from* the deck, not from an interview. Its `Narrative`
is a reading of what the talk does, not a statement of intent. Correct it before
treating it as the record.
