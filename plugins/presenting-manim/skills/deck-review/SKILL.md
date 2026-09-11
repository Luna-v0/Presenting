---
name: deck-review
description: Use after rendering a deck — "review the deck", "does this look right", "I watched it and section 3 is off", "check the slides". Runs the mechanical pass over frames and captures the user's verdicts against beat ids so the next revision can act on them. Use it every time before a talk is considered done; the failures it catches are the ones no amount of reading the screenplay will find.
---

# Deck review

Two jobs. The second matters more.

## 1. Mechanical pass

```bash
cd manim-videos
uv run manim-slides render decks/<slug>/out/<slug>_scenes.py <Scene> ... -qp
uv run python scripts/extract_frames.py <Scene> ... --out media/review
uv run python scripts/review_deck.py decks/<slug>/screenplay.md \
    --frames media/review --scenes <Scene> ...
uv run python scripts/contact_sheet.py --frames media/review --deck decks/<slug>/screenplay.md
```

It checks, in order of cost:

- **Screenplay** — budgets, missing bridges, empty visual slots, time overrun,
  genre gates, accents used before their meanings exist.
- **Model** — builds every beat and checks geometry exactly: inside the safe
  area, inside its own slot, no collision between slots, no visual slot still
  holding a placeholder.
- **Pixels** — over the extracted frames.
- **Slide hand-offs** — with `--scenes`, compares each slide's first frame
  against the previous slide's last. A slide's video plays on entry, so
  anything cleared *before* it starts is already gone in frame 0: the viewer
  sees the full slide, then a near-empty one, then the content animating back.
  That is what a per-beat flicker is, and it is invisible in still frames
  because every still looks correct on its own.

The pixel pass exists for one failure class the other two structurally cannot
see: **a slide that is correct in code and unreadable on screen.** During the
identity work a colour was silently overridden downstream and every label
rendered light-on-light. The geometry was perfect. A human eye was the only
thing that caught it. The check now measures contrast inside the exact
rectangles the library placed text in, and fails anything under 3:1.

It also flags pixels that are off-palette — a third colour behaving like an
accent — on any frame that is not holding a photo or a chart.

### Then look at every sheet. This is not optional.

`contact_sheet.py` tiles the frames six to a page with the beat id and its
`Claim` under each one. **Read every sheet image before saying anything about
the deck.** A clean mechanical run means nothing is *measurably* broken; it
says nothing about whether the deck reads well, and the two come apart
constantly.

Work the list in
[references/looking-at-slides.md](references/looking-at-slides.md) against every
tile. It is not generic advice — every item on it is a defect that shipped past
the mechanical pass on a real deck, so run it as a checklist rather than
skimming it.

The two that come up most:

- **Content jammed against one edge with dead space under it.** Cover the
  bottom third of the tile; if the slide looks like it ends there, it is
  top-jammed.
- **A line that ends inside what it points at**, instead of stopping at its
  boundary.

And the one nothing else can check: **does the frame say what its `Claim`
says?** The claim is never on screen, so this pass is the only one that can
compare them.

Report what you saw per beat id — what is on the tile, not what you infer from
it — and turn each into a verdict.

`activity-parking` beats get read differently: check them for legibility *over
duration*, from the back of a room, not at a glance. That slide has to hold
still for ten minutes.

### Not checked, and why

- **Accent consistency.** While `accents.green.meaning` and
  `accents.yellow.meaning` are unassigned in `identity/tokens.yaml` there is
  nothing to check "used for its assigned meaning" against. The script says so
  rather than pretending. Ask the user to decide (plan §11.1).
- **Raw beats.** The library does not lay them out, so their geometry and
  contrast are the author's to check by eye. The script says which frames those
  are.

## 2. Judgement capture — the important half

The user watches the HTML export and reacts. **Your job is to record what they
say against beat ids, not to diagnose.** They know what is wrong when they see
it; you know which beat they mean.

Write one verdict per beat they mention:

| Verdict | Meaning | What happens |
|---|---|---|
| `keep` | it works | nothing |
| `demote` | good, but it doesn't fit the story | `backup: true`, moved after the outro, `demoted_because` recorded |
| `narrative-wrong` | the beat is right and the *story* is wrong | reopens the brief |

```yaml
id: bt-biased
verdict: demote
demoted_because: really cool but it broke the run into the alternative
```

Then apply them:

```bash
cd manim-videos
uv run python -c "
from presenting_lib import screenplay as sp, revise, compile as C
d = sp.load('decks/<slug>/screenplay.md')
r = revise.apply_verdicts(d, C.load_brief(d))
[print(c) for c in r.changes]
sp.save(d)
"
```

### Demotion, not deletion, is the default

The most common reaction is *"this part is really cool but it didn't fit the
narrative."* That is a conflict, not a defect. Deleting means killing something
the user likes, which they will resist, and the usual result is bending the
story to keep the beat. A demoted beat is still there, still theirs, and
available next talk when the narrative has room.

Always record `demoted_because` **in the user's own framing**. That sentence is
what makes the beat findable later.

### Name the failure mode out loud

Bending the narrative to accommodate a beat you are fond of. Sometimes that is
right — a cool part can be a signal that the story is smaller than the material.
Usually it is not. Ask which is happening, and default to demoting.

### The freeze

`narrative-wrong` is the only verdict that reopens the brief, and
`narrative_frozen: true` blocks it outright. When frozen, `apply_verdicts`
refuses and says so; unfreezing has to be a deliberate act by the user, not a
drift. A loop that always invites another pass is one you never ship from.

## Then

Hand the surviving work to `screenplay` in section-scoped revision mode. It will
preserve every `origin: human` beat. See
[references/what-to-look-for.md](references/what-to-look-for.md) for the reading
pass.
