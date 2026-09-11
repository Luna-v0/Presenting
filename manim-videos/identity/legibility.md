# Where `min_legible_body` came from

`type.min_legible_body: 22` (manim font_size units).

The value does not depend on render quality. `font_size` is in scene units, so
text at 22 occupies the same fraction of the frame whether the deck is rendered
at 480p or 2K — the floor is about how big the text is *on the wall*, not how
many pixels describe it. Rendering at `-qp` makes it sharper, not larger. The
ladder below was captured at 1080p purely because that was convenient.

Derived, not guessed. `uv run python scripts/measure_slots.py --calibrate`
renders a ladder of the same sentence at descending sizes, each labelled with
its size, at true scale — the scene refuses to rescale, because a ladder that
quietly shrinks to fit is a ladder that lies about the thing it is being used
to decide. The frame is `identity/out/legibility-ladder.png`.

Read at arm's length on a laptop, which approximates the back of a room:

| size | verdict |
| --- | --- |
| 26–34 | comfortable, no effort |
| 24 | comfortable |
| **22** | **readable without effort — the floor** |
| 20 | readable, but you notice yourself reading |
| 18 | strained |
| 16 | gone |

So 22, at `Liberation Serif`. Two consequences:

* `body` and `caption` bottom out at 22. `caption` nominally renders at 24, so
  it has almost no room to shrink — that is correct, not a bug: a caption that
  needs to shrink is a caption that is too long.
* `claim`, `title` and `display` bottom out one step *above* 22 — at the size
  of the step below them. A title that has to be smaller than a claim is not a
  smaller title, it is a title that does not fit, and it should raise.

Re-derive this whenever `type.family_body` changes. The families change the
character of the deck more than any hex value does, and a different face at the
same nominal size is a different floor: this ladder is in `Liberation Serif`
because that is what Pango actually resolves to here — the beamer theme asks
for `TeX Gyre Termes`, which is not installed on this machine (plan §11.5).
