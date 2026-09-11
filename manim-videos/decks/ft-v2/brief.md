---
slug: ft-v2
title: Fine-tuning & Postprocessing LLMs — Part 2
target: manim
genre: research-talk
technicality: 4
interaction: organic
duration_min: 40
audience: LARA lab meeting — mixed background, some RL, little NLHF
narrative_frozen: false
---

## Narrative
They arrive with part 1's picture: SFT, a Bradley-Terry reward model, PPO.
That picture has an assumption nobody stated — that preferences are transitive —
and rock-paper-scissors breaks it.
They leave knowing there is an alternative that does not need the assumption,
and that Bradley-Terry is still the right tool when the world is well behaved.

## Why I'm presenting
Second half of a two-part lab session. I want the room to see why the reward
model, not the RL algorithm, is where the interesting failure lives.

## What the audience should do
Be able to say what Bradley-Terry assumes, why that assumption fails, and name
one alternative.

## Series
Follows "Fine-tuning LLMs part 1" (LoRA, SFT, RLHF, Bradley-Terry, PPO).
Beat 1 is a recap, not a cold open.

## Out of scope
Hyperparameters, training infrastructure, a GRPO derivation (offered at the end
if anyone asks).

---

**This brief was reconstructed from the existing `screenplays/ft_v2.md` and
`scenes/ft_v2.py` as the migration reference (plan §7).** It was not produced by
an interview, so `Narrative` is a reading of the deck rather than something the
human stated. Correct it before treating it as the record of intent.
