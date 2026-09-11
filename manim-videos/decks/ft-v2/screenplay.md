---
slug: ft-v2
title: Fine-tuning & Postprocessing LLMs
subtitle: Part 2 — recap, and what comes after Bradley-Terry
author: Eduardo Dantas Luna
affiliation: LARA — PUC-Rio
date: 2026
target: manim
duration_min: 40
brief: ./brief.md
---

# Section 1 — Where part 1 left off

> **Bridge.** Opening frame: part 1 built the whole RLHF loop and left it working. Everything today hangs off one piece of it — the reward model.

## 1.1 — Title

```yaml
id: title
origin: generated
layout: title-card
time_s: 30
transition: cut
```

## 1.2 — Adapters and SFT

```yaml
id: recap-adapters
origin: generated
layout: build-list
time_s: 60
transition: cut
```

**Note.** LoRA, SFT and Distillation (but it is not much important)

**Claim.** Part 1's first half was about cheap ways to change a model's weights, and only two of the three matter today.

**On slide.**
- LoRA — low-rank adapters
- Supervised fine-tuning
- Distillation — set aside for today

## 1.3 — Bradley-Terry as Elo

```yaml
id: recap-bt-lead
origin: generated
layout: build-list
time_s: 60
transition: cut
```

**Note.** The Bradley Terry model and how it is a simillar problem as a chess Elo rating system.

**Claim.** Bradley-Terry turns pairwise preferences into a single score per response, which is the same problem chess solves with Elo.

**On slide.**
- Pairwise preferences → one score per response
- Same shape as Elo: pick a winner, update the score

**Cue.** watch the formulas morph

## 1.4 — Bradley-Terry to Elo, animated

```yaml
id: bt-elo-anim
origin: human
layout: raw
time_s: 60
transition: cut
raw:
  scene: scenes.bradley_terry_elo:BradleyTerryToElo
  class: FtV2_BTAnim
```

**Note.** Use the animation from the bradley terry elo py video in this repo.

## 1.5 — RL with human feedback

```yaml
id: recap-rl-robot
origin: generated
layout: claim-above-figure
time_s: 60
transition: cut
visual:
  kind: referential
  sub: photo
  intent: a robot trained with RL from human feedback — scene-setting, not an argument
  asset: rl_robot.png
```

**Note.** RL and Human Feedback in RL problems. Where the reward is almost near a reward of a normally trained RL model.

**Claim.** A reward learned from human preferences behaves much like a hand-written RL reward.

**On slide.**
- Learned reward ≈ ordinary RL reward

## 1.6 — The OpenAI recipe

```yaml
id: recap-ppo
origin: generated
layout: build-list
time_s: 75
transition: cut
```

**Note.** We also talked about RL with LLMs and how OpenAI trained using STF and PPO.

**Claim.** The standard recipe is three stages, and the middle one is the reward model.

**On slide.**
- SFT for a reasonable starting policy
- Reward model from human preferences
- PPO against that reward

## 1.7 — The loop, end to end

```yaml
id: recap-rlhf-loop
origin: generated
layout: claim-above-figure
time_s: 60
transition: cut
visual:
  kind: referential
  sub: paper-figure
  intent: the RLHF loop end to end — prompt, samples, preference, reward model, policy update
  asset: rlhf_loop.png
```

**Claim.** All of part 1 fits in one loop, and the reward model is one box inside it.

**On slide.**
- One box in this loop is today's subject

# Section 2 — After PPO

> **Bridge.** That loop is where the field was. The next few years mostly happened inside the policy-gradient box, not the reward box — worth seeing before we go back to the reward.

## 2.1 — After PPO

```yaml
id: after-ppo-break
origin: generated
layout: section-break
time_s: 15
transition: cut
```

## 2.2 — The PPO family

```yaml
id: ppo-family
origin: generated
layout: claim-above-figure
time_s: 90
transition: cut
visual:
  kind: constructible
  sub: graph
  intent: the PPO/DPO family tree, revealed branch by branch
  graph:
    rankdir: TB
    nodes:
      - {id: ppo, label: PPO}
      - {id: dpo, label: DPO}
      - {id: grpo, label: GRPO}
      - {id: gspo, label: GSPO}
      - {id: gdpo, label: GDPO}
      - {id: qrpo, label: QRPO}
    edges:
      - {from: ppo, to: grpo}
      - {from: grpo, to: gspo}
      - {from: grpo, to: gdpo}
      - {from: grpo, to: qrpo}
      - {from: dpo, to: qrpo}
```

**Note.** (Image of PPO family)

**Claim.** Everything after PPO is a variation on the same policy-gradient step, and the branching is mostly about what you compare against.

**On slide.**
- A small zoo, one idea

# Section 3 — Feedback without humans

> **Bridge.** Every one of those still needs a reward. The next question is where the reward comes from when there is no human in the loop.

## 3.1 — Feedback without humans

```yaml
id: no-humans-break
origin: generated
layout: section-break
time_s: 15
transition: cut
```

## 3.2 — RL from verifiable reward

```yaml
id: rlvr-intro
origin: generated
layout: build-list
time_s: 90
transition: cut
```

**Note.** GRPO is a variation of PPO, I can explain it at the end of the presentation. But the important nuance is that rather then using human feedback it goes back to using simple reward functions based on rules to train the model.

**Claim.** RLVR drops the learned reward model entirely and goes back to a rule you can check.

**On slide.**
- No reward-model training step
- No preference dataset
- Just a rule that says right or wrong

**Skip.** The GRPO derivation. Offered at the end if someone asks.

## 3.3 — The math reward

```yaml
id: rlvr-math
origin: generated
layout: callout
time_s: 45
transition: cut
```

**Note.** In the original paper for GRPO they used it to train a model to be better at solving math problems. They did a lot in the paper, but we will focus on the math reward function.

**Claim.** Compare the model's answer to the known result: match is reward, mismatch is nothing.

## 3.4 — RL from AI feedback

```yaml
id: rlaif
origin: generated
layout: build-list
time_s: 75
transition: cut
```

**Note.** A trend that started is to use LLMs to train the Reward Model instead of Humans. It is highly associated with Anthropic and their Constitutional AI. It is definetly more scalablen than humans and it is highly used.

**Claim.** The other way to remove the human is to keep the reward model and let a stronger model do the labelling.

**On slide.**
- An LLM grades instead of a person
- Constitutional AI is the canonical case
- Scales past what human labelling can

# Section 4 — What Bradley-Terry actually assumes

> **Bridge.** Both of those routes avoid the reward model rather than fixing it. To fix it you have to say what it assumes — which is the thing nobody states out loud.

## 4.1 — What Bradley-Terry actually assumes

```yaml
id: bt-assumes-break
origin: generated
layout: section-break
time_s: 15
transition: cut
```

## 4.2 — What it does not need

```yaml
id: bt-drops
origin: generated
layout: build-list
time_s: 75
transition: cut
```

**Note.** 1. People can be reasoning agents and still give contradicting preferences.
2. The reward model that is learning it is biases to the distribution of the initial model by design.

This makes it a lot more scalable than the older methods.

**Claim.** Bradley-Terry is popular because of what it lets you skip, not because of what it assumes.

**On slide.**
- Annotators may contradict each other
- Bias toward the base model's distribution is by design

## 4.3 — It is not transitive

```yaml
id: bt-not-transitive
origin: generated
layout: equation-annotated
time_s: 120
transition: cut
content:
  equation: P(R \succ P),\; P(P \succ S),\; P(S \succ R) \;\;\text{can all be} > \tfrac{1}{2}
  annotations:
    - all three preferences can hold at once
    - a single score per item cannot express that
```

**Note.** P(A≻B),P(B≻C),P(C≻A).

But for a ELO ranking system this is impossible since:

r(A)>r(B)>r(C)>r(A) --> Contradiction

**Claim.** Human preferences can form a cycle, and a model that assigns one number per response cannot represent one.

**Cue.** rock paper scissors / who's voted in a runoff

**Skip.** The Luce axioms. Not needed for the argument.

## 4.4 — Biased to the dataset

```yaml
id: bt-biased
origin: generated
layout: build-list
time_s: 75
transition: cut
```

**Note.** Because if amount of A > C then Bradley-Terry will give a higher reward for A than C.

**Claim.** How often something appears in the preference data leaks straight into its reward.

**On slide.**
- Frequency in the data becomes reward
- Coverage shapes the whole reward landscape
- Re-weighting and active sampling help

# Section 5 — An alternative

> **Bridge.** So the fix has to drop the single score, not the human. That is exactly what Nash Learning from Human Feedback does.

## 5.1 — An alternative

```yaml
id: alternative-break
origin: generated
layout: section-break
time_s: 15
transition: cut
```

## 5.2 — Nash Learning from Human Feedback

```yaml
id: nlhf-idea
origin: generated
layout: build-list
time_s: 105
transition: cut
```

**Note.** The general idea is really simple, instead of BT, lets train a binary classifier to predict the preference. (given two answers, which one is better?)

Then we treat this as a two player game between the human and the model.

**Claim.** Train a classifier that answers "which of these two wins", then solve the game it defines instead of fitting a score.

**On slide.**
- Binary classifier, not a scalar reward
- Two-player game
- Solve for the equilibrium

## 5.3 — NLHF policy gradient, animated

```yaml
id: nlhf-anim
origin: human
layout: raw
time_s: 90
transition: cut
raw:
  scene: scenes.nlhf:NLHF
  class: FtV2_NLHFAnim
```

**Note.** Use the animation from the nlhf.py

## 5.4 — What it buys you

```yaml
id: nlhf-results
origin: generated
layout: claim-above-figure
time_s: 60
transition: cut
visual:
  kind: referential
  sub: paper-figure
  intent: NLHF results against a Bradley-Terry baseline — the empirical case for dropping BT
  asset: results_nlhf.png
```

**Claim.** The equilibrium policy beats the Bradley-Terry baseline where preferences are not transitive.

**On slide.**
- Better where BT's assumption fails

# Section 6 — When Bradley-Terry is still right

> **Bridge.** Which is not the same as saying Bradley-Terry was a mistake. It is worth being clear about where it is still the right tool.

## 6.1 — When Bradley-Terry is still right

```yaml
id: still-right-break
origin: generated
layout: section-break
time_s: 15
transition: cut
```

## 6.2 — Not really

```yaml
id: bt-still-works
origin: generated
layout: callout
time_s: 60
transition: cut
```

**Note.** For well behaved problems, (like the ones solvable by RLVR) BT works perfectly.

**Claim.** For well-behaved problems — the ones RLVR can also solve — Bradley-Terry works perfectly and costs less.

# Section 7 — If you want to play with it

> **Bridge.** That is the argument. The rest is what to install if you want to try any of it this week.

## 7.1 — If you want to play with it

```yaml
id: outro-break
origin: generated
layout: section-break
time_s: 15
transition: cut
```

## 7.2 — Libraries

```yaml
id: libraries
origin: generated
layout: build-list
time_s: 75
transition: cut
```

**Note.** TRL – RL for LLM algorithms
PEFT – LoRA and other Adapters
UNSLOTH – Easy Training Loop for a whole FT pipeline for LLMs
ART – Adaptable training loop for RL pipelines for LLMs

**Claim.** Four libraries cover everything in this talk.

**On slide.**
- TRL — RL algorithms for LLMs
- PEFT — LoRA and other adapters
- Unsloth — a whole fine-tuning pipeline
- ART — training loops for RL pipelines

## 7.3 — Harness

```yaml
id: harness
origin: generated
layout: callout
time_s: 45
transition: cut
```

**Note.** Hermes agents – Claude-code-like CLI that uses online RL to learn based on your feedback (uses the cloud and no local computation!)

**Claim.** Hermes agents is a Claude-Code-like CLI that learns from your feedback with online RL, in the cloud.

## 7.4 — Thesis ideas

```yaml
id: thesis-ideas
origin: generated
layout: build-list
time_s: 120
transition: cut
```

**Note.** 1. Fine tune Deep Racer (using this new gym interface) (but no real world test)
2. Test other PG algorithms without no Bradley Terry
3. Fine tune a robotics problem to solve a task using some ideas of LLM fine tuning
    a. Use a preference Model instead of Bradley Terry
    b. Use a non-deterministic model and do GRPO
4. Fine tune SLMs for a RLVR task (coding, websearch, reasoning, etc)
5. Evaluate LoRA with other domains.
6. Human Feedback to create a time-to-talk model (based on the BT model).

**Claim.** Six of these are the size of a thesis and none of them are taken.

**On slide.**
- DeepRacer through the new Gym interface
- PG algorithms without Bradley-Terry
- Robotics with a preference model
- SLMs on an RLVR task
- LoRA in other domains
- A time-to-talk model from human feedback

**Cue.** ask who wants which
