# What looking catches

Every defect below shipped past the mechanical pass. Each one was geometrically
correct, inside its slot, inside budget, above the contrast floor, and wrong.
They came out of two review rounds on one deck, which is why they are written
down: they are not exotic, they are what goes wrong.

Work through this list against the contact sheets, per tile.

## Balance

**Content jammed against one edge with dead space under it.** The most common
single defect. A short block top-aligned in a tall slot leaves half the slide
empty and reads as unfinished.

Top alignment exists for one reason: so content does not jump as it is
revealed. If everything on the beat arrives at once — a parking slide, a static
figure — there is nothing to protect and it should be balanced in the slot. If
it does arrive progressively, compute the finished block, place *that*, and
reveal items in position; then nothing moves and nothing is stranded.

Ask: cover the bottom third of the tile. Does the slide look like it ends
there? If yes, it is top-jammed.

## Things that point

**A line that ends inside what it points at.** A leader must stop at the
*boundary* of its target, never at its centre, or it draws straight through the
label it is pointing to.

Watch for clipping to the wrong thing: a text mobject is a group of per-glyph
shapes, so "the smallest shape containing this point" is a *letter*, and the
line stops on the letters instead of the box around them. Clip to shapes,
skipping text.

## Marks

**A marker nobody can identify as a marker.** A bare stripe, a rule, a tint
with no label. If a reader has to ask what it means, it is decoration with a
job it cannot do. Prefer a word in the footer, which already carries secondary
status and never collides with content.

## Transitions

**Content from the previous beat written over the new beat.** A `build`
transition must keep only what the incoming beat will not draw over — measured
geometrically, since two layouts can occupy the same region under different
slot names.

**A flicker at every beat change.** A slide's video plays on entry, so anything
cleared before that video starts is already missing from frame 0: full slide →
near-empty slide → content animating back. Clearing "at the start of the new
beat" is exactly this bug, and it is invisible in still frames because each
still is correct on its own — compare a slide's *first* frame with the previous
slide's *last* (`review_deck.py --scenes`).

The outgoing beat has to leave *inside* the new video, so frame 0 matches where
the last slide ended and the hand-off between videos is imperceptible.

**A ghost at every beat change.** Two dissolves stacked — the export's slide
transition *and* a hand-rolled crossfade — or one crossfade where the two things
overlap in space: two titles in the same band at half opacity is a ghost, not a
transition. Sequence them instead; the old title leaves with the old content and
the new one arrives with the new.

Once every slide's first frame matches the previous slide's last, the export
should have *no* transition. A dissolve then has nothing to hide and only
cross-fades two videos whose content differs, which is visible on letters and
formulas even when the backgrounds match perfectly.

**A dark flash on every slide change, backgrounds included.** Not the deck — the
page behind it. reveal.js's stock theme has a near-black background and slide
backgrounds fade, so the page shows through. Paint the page the deck's ground.

## Figures

**A figure that does not fill the space it was given.** A four-node graph
marooned in a full-frame slot is not a full-bleed figure. Spread the layout to
fill rather than magnifying it — magnifying pushes the labels off the type
scale.

**A figure that arrives all at once when it has an order.** If the structure
was declared node by node, it should arrive node by node. The reveal sequence
is usually already computed and thrown away.

**An equation that never grew.** Fitting rules that only shrink leave a short
formula stranded in the middle of a slot built to hold it. On a beat whose
whole point is the formula, that reads as a mistake.

## Tables

Build them cell by cell — the box and its text together, header first, then one
row at a time. A grid drawn up front and filled in afterwards shows lines
before there is anything to line up.

## Small text

**Word spaces that look collapsed.** Pango rounds a space to a whole pixel, so
below roughly font size 22 every word space gets the same 1px gap as the letter
spacing and `Where part 1 left off` reads as `Wherepart1 leftoff`. The letters
are fine; the words run together.

Never fix it by nudging the size up until it happens to work. Render the text at
a size that spaces correctly and **scale the mobject down** — the quantisation
happens at render time, so a scaled mobject keeps its proportions. This is how
the footer gets to be small.

## Series and colour

**Two series in the same colour.** If colour is reserved for a categorical
encoding, unaccented series are all one colour and become indistinguishable.
Separate them by line style instead.

**An accent spent by accident.** Check where accents come from, not just where
they are written. A style file that hands out accent colours by default spends
the encoding on every chart, in a place the screenplay validator cannot see.

**Yellow without a green.** The accents are positional: green is the first of
two things being related, yellow the second. A lone yellow mark means "the
second of two" with no first — the beat has lost half of what it was showing.

**A hand-written beat that does not look like the deck.** `raw` beats are not
touched by the library and usually predate the identity. `review_deck.py`
reports how far off-palette each raw scene is; anything above a few percent
will read as belonging to a different talk.

## Clearing

**A beat still visible under the next one.** If a step was expanded into
sub-steps — a diagram revealing node by node, a table building row by row — the
mobjects on stage are the *sub-groups*, not the group the layout returned.
Clearing the parent removes nothing. Track what was actually drawn.

## Reporting

Per beat id, say what you saw, not what you infer. "The leader ends inside the
`collect` box" is actionable; "the diagram looks off" is not. Then turn each
into a verdict.
