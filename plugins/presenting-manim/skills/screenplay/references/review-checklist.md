# Screenplay checklist

Runnable against any existing screenplay, without regenerating it.

```bash
cd manim-videos
uv run python -c "
from presenting_lib import screenplay as sp, compile as C
d = sp.load('decks/<slug>/screenplay.md')
[print(f) for f in C.validate(d)]
"
```

That covers the mechanical half. The rest is reading.

## Story

- [ ] Does every section have a **Bridge**, and is each one a real logical
      connection rather than a transition phrase? If a bridge cannot be
      written, the order is wrong — reorder, do not invent a connective.
- [ ] Do the beats in a section actually deliver what its bridge promised?
- [ ] Does the deck's arc match the brief's `Narrative` — setup, turn, landing?
- [ ] Is any beat assuming something no earlier beat established?
- [ ] Do two beats make the same point? Merge, or demote one.
- [ ] Is anything present because the user wants to cover it rather than
      because this audience needs it? Say so.

## Slides

- [ ] Any beat with a full text slot and `visual.kind: none`? That is a defect.
- [ ] Is anything conceptual sourced as a photo when a diagram would be better?
- [ ] Is `On slide` fragments, not sentences? (Except `claim-only`, `callout`.)
- [ ] Is every text slot inside its budget for **this target**?
- [ ] Is all on-slide text English?

## The user's words

- [ ] Is every `Note` byte-identical to what they wrote?
- [ ] Is every `Cue` still keywords, in whatever language they used?
- [ ] Has any `Claim` leaked onto a slide verbatim outside `claim-only` /
      `callout`?

## Time

- [ ] Does the total sit inside 85% of the slot?
- [ ] If not, which beats are the demotion candidates? **Demote, never delete.**

## Gates

- [ ] Discussion beats: allowed by genre *and* by `interaction`?
- [ ] Activity blocks: `genre: tutorial`, and always setup + parking as a pair?
- [ ] Accents: none assigned while the meanings are unassigned in
      `identity/tokens.yaml`.

## The loop

- [ ] Is every `id` stable and unique?
- [ ] Is `origin: human` set on everything the user wrote or edited?
- [ ] Does every `backup: true` beat carry a `demoted_because`?
