# Writing a beat by hand

The catalog will run out. When it does, `layout: raw` hands the beat straight to
manim and the library gets out of the way entirely — no slots, no fitting, no
validation. Raw beats still carry `time_s`, still belong to a section, still get
a beat id, and still take part in review and the revision loop. They only skip
the layout.

A library you cannot step around gets abandoned, so reach for this whenever the
beat needs something the catalog does not do. It is not a failure mode.

## Two forms

### Reuse a scene that already exists

The common case: you have a scene file and want it in the deck.

```yaml
id: bt-elo-anim
layout: raw
time_s: 60
raw:
  scene: scenes.bradley_terry_elo:BradleyTerryToElo
  class: FtV2_BTAnim
```

`scene` is `module:Class`, importable from `manim-videos/`. `class` is the name
the deck will render it under — it becomes a subclass, so the original file is
never touched. Your scene must inherit from `manim_slides.Slide` (or
`ThreeDSlide`); its internal `next_slide()` calls become click-through points
inside the deck, exactly as they would standalone.

`ft-v2` does this twice, for `bradley_terry_elo.py` and `nlhf.py`.

### Write the scene in the screenplay

For something short that does not deserve its own file:

```yaml
id: the-raw-beat
layout: raw
time_s: 40
raw:
  class: CatalogDemo_Raw
  code: |
    class CatalogDemo_Raw(DeckScene):
        deck_path = str(DECK_PATH)
        beat_ids = ()

        def construct(self):
            from manim import Circle, Create, ManimColor, Text
            from presenting_lib.tokens import PALETTE, TYPE

            self.camera.background_color = ManimColor(PALETTE.ground)
            self.camera.init_background()
            ...
```

The code is emitted into the generated module verbatim. `DeckScene`,
`DeckScene3D` and `DECK_PATH` are already in scope there.

## Staying on-identity

Nothing forces a raw beat to look like the rest of the deck, so do it yourself:

```python
from presenting_lib.tokens import PALETTE, TYPE, GEOMETRY
from presenting_lib.slots import Slot
from presenting_lib.chrome import CONTENT_FULL
```

- Set the ground: `self.camera.background_color = ManimColor(PALETTE.ground)`
  then `self.camera.init_background()`. A plain hex string renders but crashes
  manim-slides on save.
- Take colours from `PALETTE`, sizes from `TYPE.size("body")` and families from
  `TYPE.family("body")`. Do not type hex or font numbers.
- You can still use `Slot(...).fit_text(...)` for individual pieces without
  adopting a whole layout — it is the fitting, not the catalog.
- End on the state you want held: manim renders an animation over
  `[0, run_time)`, so add a short `self.wait(0.4)` before each `next_slide()` or
  the slide ends mid-draw.
- Keep the first frame equal to where the previous slide ended if you can. A
  slide's video plays on entry, so clearing before it starts makes the deck
  flicker on that beat.

## Chrome on a raw beat

A raw beat skips the catalog, so it also skips the chrome the catalog would have
drawn. For the title and the green rule that is usually what you want — a
hand-composed figure or a video wants the whole frame. The footer is different:
a bare canvas still sits somewhere in the deck, and the room still wants to know
where.

So the compiler tells every raw scene where it is:

```python
class Safety_GapPass(GapPass):
    section_name = 'The object being transferred'
    slide_number = 11
    deck_sections = ('The car, and the instinct it produces', ...)
```

Draw the footer from those three and it is the same footer every other slide
carries — same type, same muted colour, same progress dot on the same section:

```python
from presenting_lib.chrome import DeckMeta, footer

class Canvas(Slide):
    section_name = ""
    slide_number = 1
    deck_sections: tuple = ()

    def construct(self):
        self.camera.background_color = ManimColor(PALETTE.ground)
        self.camera.init_background()
        if self.deck_sections:                 # absent when run standalone
            self.add(footer(DeckMeta(sections=list(self.deck_sections)),
                            self.section_name, self.slide_number))
```

Guard on `deck_sections`. It is empty when the scene is rendered on its own —
`manim-slides render scenes/foo.py Canvas` — which is how you iterate on a raw
beat, and a footer claiming slide 1 of an unknown deck is worse than none.

**Leave room for it.** The footer sits at the bottom of the frame and nothing
stops a figure from being drawn straight through it. Whatever slot the beat
composes into should stop above it; `presenting_lib.chrome.CONTENT_FULL` is the
band a full-chrome layout uses, and a canvas that only wants the footer can
take most of the frame but not all of it.

## What review can and cannot tell you

`review_deck.py` reports raw beats and then leaves them alone — it has no slots
to check them against. Geometry, contrast and legibility on a raw beat are
yours. The contact sheet still includes its frames, so look at them.

That now covers the footer too. A raw beat that draws one has chrome geometry
nothing validates, so a figure overlapping the section name or the progress dots
will render perfectly happily. The contact sheet is the only thing that catches
it.

## When not to use it

If the beat is a claim with a figure, or a list, or a comparison, use the
layout. Raw is for what the catalog genuinely does not cover: a hand-composed
spatial figure, a bespoke animation, a simulation. Reaching for it because a
layout is *almost* right produces a deck where half the slides drift from the
other half — which is the thing the library exists to prevent.
