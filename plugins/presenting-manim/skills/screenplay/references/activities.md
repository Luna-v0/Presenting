# Activity blocks

`genre: tutorial` only. Always a pair, never a single beat.

## `activity-setup`

The task, with a worked example if one helps. This is the beat you talk over.

```yaml
id: fit-a-preference-model
layout: activity-setup
time_s: 180
content:
  task: Fit both models on the toy set and find one triple where they disagree.
  example: |
    pref = load("toy.jsonl")
    fit(pref, model="bt")
```

## `activity-parking`

The slide that stays on screen while people work. Instructions on the left,
constraints in a box on the right.

```yaml
id: fit-a-preference-model-parking
layout: activity-parking
time_s: 900
content:
  instructions: Open notebook 3. Load the toy preference set, fit both models,
    and find one triple where they disagree.
  constraints:
    - 20 minutes
    - pairs
    - ask before installing anything
```

This is the one slide in a manim deck that must **hold still and stay legible
for ten minutes** rather than animate. The compiler renders it static by
construction. At review, check it for legibility over duration — read it from
the back of the room, not at a glance.

## Timing

`time_s` covers setup, the work itself, and the debrief. Note what the
presenter does while people work — walking around, or sitting down — in `Note`.
