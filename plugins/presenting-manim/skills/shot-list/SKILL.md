---
name: shot-list
description: Use after a screenplay exists to produce the deck's SHOTS.md — the list of images the user has to go and find, and the diagrams we will build for them. Triggers on "what images do I need", "shot list", "find the figures", or any point where a deck is about to be rendered with empty visual slots. Also use when the target changes, since the ask is different for manim and slides.
---

# Shot list

Read the screenplay, write `decks/<slug>/SHOTS.md`, and make sure the deck
builds green immediately.

```bash
cd manim-videos
uv run python -c "
from presenting_lib import screenplay as sp, shots
d = sp.load('decks/<slug>/screenplay.md')
print(shots.write(d))
for s in shots.shots_for(d):
    print(('BUILD' if s.built_by_us else 'ASK  '), s.beat_id, '-', s.needs)
"
```

## A deck with zero assets must render end to end

Every unsourced visual falls back to a labelled placeholder — a box saying what
it is waiting for. That is what turns "go find PNGs" into a stage instead of a
blocker, and it matters more here than it looks: the user needs to watch a rough
deck back **before** committing to any assets, because watching it is how they
find out which assets are worth sourcing.

Never leave a deck that will not build.

## The list is a function of the target

| Visual | manim | slides |
|---|---|---|
| `constructible` | nothing to ask — the library draws it | a manim still into `assets/built/` |
| `chart` with `data:` | nothing to ask | nothing to ask |
| `chart` without data | ask for the numbers | ask for the numbers |
| `referential` | ask | ask |

Expect roughly three asks for a manim deck and three times that for a Slides
one, from the identical screenplay.

For `constructible` visuals on the **slides** target, render them in manim as
high-resolution stills into `assets/built/<beat-id>.png`. This is the one place
the two targets touch, and it is what makes a Slides deck look like the user's
own rather than like clip art.

## Write asks the user can act on

Each entry is keyed by beat `id`, never by position, so reordering the deck
never invalidates an ask or breaks a path.

```markdown
### preference-cycle — referential / paper-figure

**Needs:** reward-hacking figure from Gao et al. 2023, fig. 3
**Why:** the claim is that overoptimization is empirical — an asserted graph won't carry it
**Search:** "gao scaling laws reward model overoptimization figure 3"
**Wrong if:** it's the KL plot rather than proxy-vs-gold
**Save to:** assets/raw/preference-cycle.png
**Attribution:** Gao, Schulman, Hilton 2023 — needs a credit line
```

**Wrong if** is the field that saves a round trip. Write it whenever there is a
plausible near-miss.

Never generate photographic or referential imagery. The user sources PNGs by
hand and considers being asked a feature.

## Offer recreations — never do them silently

When a paper figure is supplied and the target is manim, offer to rebuild it
natively. It inherits the palette, it is not blurry, and the reveal order
becomes the user's.

Offer it, do not just do it: it costs render iteration, it is the step most
likely to introduce a subtle error, and redrawing somebody's published result
has a fidelity question attached. Frame it concretely — *"roughly ten minutes of
render iteration, and it animates in three steps"* — so the user can price it.

## Attribution

Where a shot records one, it renders in the `caption` slot in caption style. Set
`visual.attribution` on the beat so `render-manim` and `render-slides` both pick
it up.

## Then

`render-manim` (or `render-slides`). Placeholders are fine at that point — the
first watch-through is what decides which of these asks actually matter.
