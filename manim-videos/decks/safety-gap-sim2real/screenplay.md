---
slug: safety-gap-sim2real
title: Bridging the safety gap between simulation and reality
subtitle: Constrained RL on a small-scale autonomous vehicle
author: Eduardo Dantas Luna
affiliation: PUC-Rio — Master's proposal defence
date: September 2026
target: manim
duration_min: 30
brief: ./brief.md
---

# Section 1 — The car, and the instinct it produces

> **Bridge.** Opening frame: the platform goes up first, because the two things the room will hold against this work — that the car is too small for safety to matter, and that the gap is a fidelity problem — are both produced by looking at it.

## 1.1 — Title

```yaml
id: title
origin: generated
layout: title-card
time_s: 25
transition: cut
generated_hash: 94c4130f6a5f6bd8
```

## 1.2 — In the simulator

```yaml
id: sim-works
origin: generated
layout: raw
time_s: 25
transition: cut
visual:
  kind: referential
  sub: screenshot
  asset: sim_chase.png
  intent: 'up.mp4 at 30s — chase camera behind the car, 644x484, 54.5s. CAVEAT: this
    is the old SageMaker/RoboMaker (Gazebo) stack, not the current simulator shown
    at the-instrument; simulador_local.mp4 is the same footage with the console UI
    still in frame. Either re-record a chase clip from the current simulator or say
    out loud that this is an earlier version.'
raw:
  scene: scenes.clips:SimWorks
  class: Safety_SimWorks
generated_hash: 2fc0b5d8a7655df8
```

**Note.** What I really want to show is that the car works on the simulator, and then you can use the camera chase

**Claim.** In simulation the policy drives the track, and this is where every result in this talk begins.

**On slide.**
- Trained policy, simulated track

**Cue.** Illustration, not measurement — say so

**Skip.** Plays as a clip (up.mp4 24–38s); trim by editing scenes/clips.py:SimWorks. The stills stay recorded on this beat as poster frames.

## 1.3 — On the real track, by hand

```yaml
id: real-by-hand
origin: generated
layout: raw
time_s: 25
transition: cut
visual:
  kind: referential
  sub: photo
  intent: wlad_driver.mp4, trimmed by the user and played whole (10.3s, 4K). The real
    person driving. Has an audio track; the clip scene decodes video only, so it plays
    silent.
raw:
  scene: scenes.clips:RealByHand
  class: Safety_RealByHand
generated_hash: 098f168c3cabde4b
```

**Note.** the video of me driving it instead of the model

**Claim.** Driven by hand the same car holds the road, so neither the track nor the car is the problem.

**On slide.**
- Real car, driven by me

**Skip.** Plays as a clip (carrinho.mp4 12–31s); trim by editing scenes/clips.py:RealByHand. The stills stay recorded on this beat as poster frames.

## 1.4 — The catch

```yaml
id: manual-reveal
origin: generated
layout: claim-only
time_s: 20
transition: cut
generated_hash: e5c7ef4c25fbc3f0
```

**Note.** another slide that I can pass in the middle of this and the next

**Claim.** But that was actually manual driving!

## 1.5 — On the real track, by the policy

```yaml
id: real-by-policy
origin: generated
layout: raw
time_s: 30
transition: cut
visual:
  kind: referential
  sub: photo
  intent: car_running_away.mp4, trimmed and played whole (22.9s). The policy driving
    the physical car badly. Already 480x848 portrait on disk, so no rotation is applied.
raw:
  scene: scenes.clips:RealByPolicy
  class: Safety_RealByPolicy
generated_hash: 19471ae3203eb4a9
```

**Note.** the real video of the car with people chasing it

**Claim.** Driven by the policy it leaves the track, and someone has to walk over and put it back.

**On slide.**
- Real car, driven by the policy

**Skip.** Plays as a clip (VID-20251009 26–35.8s, rotated -90); trim by editing scenes/clips.py:RealByPolicy. The stills stay recorded on this beat as poster frames.

## 1.6 — The obvious objection

```yaml
id: why-bother
origin: generated
layout: claim-only
time_s: 25
transition: cut
generated_hash: 67f3473493e5c6e3
```

**Note.** Before the callout, I want a pause to ponder, about how there is the advantage of this system

**Claim.** But it's a toy car, why should we study this? It can't even hurt someone…

**Skip.** The answer. It lands on the next slide.

## 1.7 — Why study it here

```yaml
id: not-catastrophic
origin: generated
layout: callout
time_s: 40
transition: cut
generated_hash: 880942d040022812
```

**Note.** Exactly that, because mistakes are not catastrophic! Safety can be studied without a real size car crashing on the real world!

**Claim.** Exactly that, because mistakes are not catastrophic! Safety can be studied without a full-size car crashing in the real world.

# Section 2 — The object being transferred

> **Bridge.** The instinct has to be answered with an object rather than an argument. This is the loop the whole talk annotates, and the step that constrains it is Altman's.

## 2.1 — The object being transferred

```yaml
id: mdp-to-cmdp
origin: generated
layout: raw
time_s: 90
transition: cut
raw:
  scene: scenes.rl_loop:MdpToCmdp
  class: Safety_MdpToCmdp
generated_hash: 7ea31491e4c97252
```

**Note.** I wanted those kinda together and I want to transition to the cost, which is a new arrow with line

**Claim.** The loop and its tuple are one picture, and becoming a CMDP is one arrow arriving — a cost coming back alongside the reward, and a budget on it.

**Skip.** Three slides for one idea. The observation/state point is said over the first step rather than boxed.

# Section 3 — Sim2real

> **Bridge.** The formalism reads the same in both places. What does not read the same is every quantity inside it, and naming those one at a time is what sim-to-real means here.

## 3.1 — Sim2real

```yaml
id: s2r-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 3.2 — Why it happens

```yaml
id: fidelity-instinct
origin: generated
layout: claim-only
time_s: 15
transition: cut
generated_hash: d3b140cb0a5d3827
```

**Note.** The two opening videos produce exactly that instinct, and it is named out loud rather than defused.

**Claim.** But why does it work in simulation and not in the real world? The main problem is…

**Skip.** Finishing the sentence. The next section finishes it.

## 3.3 — What sim-to-real looks like

```yaml
id: pov-difference
origin: generated
layout: raw
time_s: 30
transition: cut
visual:
  intent: 'two onboard streams side by side: pov.mp4 18-35s (simulated) and donut_t1.mp4
    played whole (17s, the physical car POV). Lengths now match, so neither panel
    freezes while the other runs.'
content:
  label_l: Simulated — outdoors, asphalt
  label_r: Real — indoors, cloth, foam walls
  panel_l:
    kind: referential
    sub: screenshot
    asset: onboard_sim.png
    intent: pov.mp4 at 25s — onboard view, 636x490, 49.5s. This is the old SageMaker/RoboMaker
      (Gazebo) simulator; simulador_local.mp4 shows the console UI that proves which
      stack it is. Re-record from the current simulator if you want the pair to be
      about the current one, but the beat no longer depends on the two matching.
  panel_r:
    kind: referential
    sub: photo
    asset: onboard_real.png
    intent: 'VID-20260908-WA0009.mp4 at 10s — the car''s own camera, 640x480, no audio
      stream. Usable 8–30s; wall contact from ~15s, leaves the arena at ~29s, dead
      after 32s. Alt: onboard_real_offtrack.png (28.5s, crossing out).'
raw:
  scene: scenes.clips:OnboardPair
  class: Safety_OnboardPair
generated_hash: 4c46ad4081e417ed
```

**Note.** before talking directly about the possible sim2real discrepancies (O_sim != O_real) it is actually good to have a small pause. To talk about the sim2real, and I think the best way to do this is to actually show the slide between those two about the comparison via camera view

**Claim.** Before naming the discrepancies one at a time: this is what the gap looks like. The same corner, through the same camera, in each place.

**Skip.** Plays as a clip (pov.mp4 18–34s | VID-20260908 8–24s); trim by editing scenes/clips.py:OnboardPair. The stills stay recorded on this beat as poster frames.

## 3.4 — The gap, element by element

```yaml
id: gap-pass
origin: generated
layout: raw
time_s: 75
transition: cut
raw:
  scene: scenes.rl_loop:GapPass
  class: Safety_GapPass
generated_hash: daefa46d6f83d20a
```

**Note.** you dont need to have it with a title, they can be just canvas, and I want to maintaing and just modify them while show the observations discrepancies and etc

**Claim.** One loop, held on screen, with a different element marked each click: observation, action, transition, reward — and none of them is the one that breaks the pattern.

**Skip.** Four separate slides. The steps live in scenes/rl_loop.py:GAP_STEPS; the notation is drawn on the canvas, not in a title.

# Section 4 — Similar platforms

> **Bridge.** With the constraint established as the thing that has to transfer, the closest work can be read against it. Two platforms have already done RL on cars this size.

## 4.1 — Similar platforms

```yaml
id: lit-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 4.2 — The platform

```yaml
id: platform
origin: generated
layout: claim-above-figure
time_s: 50
transition: cut
visual:
  kind: referential
  sub: photo
  asset: platform.png
  intent: 'car_running_away.mp4 at 21s, cropped: the DeepRacer with its camera module,
    straddling the boundary line'
generated_hash: 0f81caefc17dd1e5
```

**Note.** I also want to talk about domain randomization on the original deepracer paper because they also use something similar

**Claim.** DeepRacer trains entirely in simulation with no tuning on the car, and already narrows the gap through joint perception and dynamics — so randomization is not new to this platform.

**On slide.**
- 1/18 scale, monocular camera, sim-only
- Randomization already here. Balaji 2020

**Skip.** Their specific knobs. The Zotero note carries only the abstract, so the detail needs checking against the PDF before it goes on a slide.

## 4.3 — What it looks like

```yaml
id: dr-example
origin: human
layout: claim-above-figure
time_s: 30
transition: cut
visual:
  kind: referential
  sub: screenshot
  asset: renderer_nyx_dr.png
  intent: four onboard views of the same track under randomized appearance. Pairs
    with renderer_nyx.png in Methodology, which is the same renderer un-randomized
```

**Note.** I want the nyx generalization to go right after the slide about the original deepracer paper from balaji

**Claim.** The same track and the same geometry, with appearance randomized. The policy has to work across all of them.

**On slide.**
- the same track, four times over

## 4.4 — Wheeled Lab

```yaml
id: wheeled-lab
origin: generated
layout: claim-above-figure
time_s: 35
transition: cut
visual:
  kind: referential
  sub: screenshot
  asset: wheeled_lab.png
  intent: 'wheeledbot.mp4 at 13s: the policy with a moving barricade beside the Isaac
    Lab training trajectories'
generated_hash: 55359c1ed1bcf8e7
```

**Note.** no constraint formalism, no cost channel — it is a fidelity-and-randomization framework, which is the received view the turn argues against

**Claim.** An open-source Isaac Lab stack for low-cost RC cars, demonstrated with three zero-shot policies — drifting, elevation traversal, visual navigation. Han et al. 2025. The contribution is the stack; there is no cost channel.

**On slide.**
- Isaac Lab stack for RC cars · Han et al. 2025

## 4.5 — Controlled drifting

```yaml
id: drift-wheeled
origin: human
layout: raw
time_s: 35
transition: cut
raw:
  scene: scenes.clips:DriftWheeled
  class: Safety_DriftWheeled
```

**Note.** I added a drift_wheeled video that should be the second slide of wheeled lab (only should have two slides)

**Claim.** Wheeled Lab drifting on purpose, trained in simulation.

# Section 5 — Domain randomization

> **Bridge.** Both of them close the gap the same way, and so does the strongest sim-to-real result in the field — by randomizing what the simulator cannot get right.

## 5.1 — Domain randomization

```yaml
id: dr-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 5.2 — Project Ace

```yaml
id: ace-video
origin: human
layout: raw
time_s: 40
transition: cut
raw:
  scene: scenes.clips:AceVideo
  class: Safety_AceVideo
```

**Note.** I also added a video for the rubik cube and the project ace and the wheeled robot

**Claim.** Project Ace, in motion.

## 5.3 — Project Ace

```yaml
id: project-ace
origin: human
layout: claim-above-figure
time_s: 40
transition: cut
visual:
  kind: referential
  sub: paper-figure
  asset: ace_1.png
  intent: 'the Project Ace perception setup: cameras, gaze control, the arm'
```

**Note.** the idea of the architecture is that they have neural networks that generates a distill information for the policy, but they instead of doing a feature vector they have a stack of inputs into the policy, they also have some kind of noise to the training on simulation that resambles domain randomization

**Claim.** Project Ace is Sony AI's table tennis robot. Its policy reads a noisy state while its critic reads the true one, and that noise is what stands in for randomization. The stacking and the asymmetry are what this work inherits.

**On slide.**
- Noisy state to the policy, true state to the critic
- Sony AI, Nature 2026

**Skip.** The table tennis. What transfers is the architecture, not the sport.

## 5.4 — Asymmetric actor critic

```yaml
id: ace-architecture
origin: human
layout: claim-above-figure
time_s: 35
transition: cut
visual:
  kind: referential
  sub: paper-figure
  asset: ace_2.png
  intent: the Project Ace asymmetric actor critic diagram
```

**Note.** I also added 2 photos from ace and from cube that you can put after the videos

**Claim.** The critic is given the true state and the policy only a noisy one. That is the same asymmetry a privileged cost critic uses.

**On slide.**
- the policy sees noise, the critic sees truth

## 5.5 — Solving a Rubik's cube

```yaml
id: cube-video
origin: human
layout: raw
time_s: 30
transition: cut
raw:
  scene: scenes.clips:CubeVideo
  class: Safety_CubeVideo
```

**Note.** I also added a video for the rubik cube and the project ace and the wheeled robot

**Claim.** Solving a Rubik's cube, in motion.

## 5.6 — Automatic domain randomization

```yaml
id: openai-cube
origin: human
layout: claim-above-figure
time_s: 30
transition: cut
visual:
  kind: referential
  sub: paper-figure
  asset: cube_1.png
  intent: 'the ADR pipeline: randomized environments, the policy, the vision network'
```

**Note.** The Project Ace and OpenAIs Cube hand will be two of them instead the one about fully domain randomization

**Claim.** OpenAI solved a Rubik's cube on a real hand from simulation alone by generating randomized environments of ever-increasing difficulty — and their memory-augmented policy is the same idea as stacking history.

**On slide.**
- ADR: randomize harder until it transfers
- OpenAI 2019

## 5.7 — Transfer to the real world

```yaml
id: cube-transfer
origin: human
layout: claim-above-figure
time_s: 35
transition: cut
visual:
  kind: referential
  sub: paper-figure
  asset: cube_2.png
  intent: the cube paper's transfer-to-real diagram
```

**Note.** I also added 2 photos from ace and from cube that you can put after the videos

**Claim.** Their real-world stack is the pipeline this work uses: camera images into a network, a state vector out, the policy on top of it.

**On slide.**
- three cameras, a state network, then the policy

# Section 6 — Three questions about the constraint

> **Bridge.** Nobody in that literature carries a cost channel. So the open questions are about the constraint: whether it can be satisfied, whether it survives the trip, and what makes it survive.

## 6.1 — Three questions about the constraint

```yaml
id: rq-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 6.2 — RQ1

```yaml
id: rq1-question
origin: generated
layout: callout
time_s: 20
transition: cut
generated_hash: 6fe7b93baf98dab7
```

**Note.** I think actually the rq1 be a "can" is not falsifiable, I think we can go direclty to the second part of the question

**Claim.** Does a CMDP-trained policy achieve constraint satisfaction in simulation comparable to or better than a reward-shaped baseline?

**Skip.** Whether Time Trial can be written as a CMDP. It is a modelling choice, not a question, and section 2 already shows it done.

## 6.3 — RQ1 — how it gets answered

```yaml
id: rq1
origin: generated
layout: build-list
time_s: 35
transition: cut
generated_hash: 99656de539ee961f
```

**Claim.** The first question is whether the reformulation is possible at all, and whether it beats shaping on the thing it is supposed to control.

**On slide.**
- CMDP vs reward-shaped baseline
- 5 seeds · 40 train / 20 held out

## 6.4 — RQ2

```yaml
id: rq2-question
origin: generated
layout: callout
time_s: 20
transition: cut
generated_hash: 3de1d92b7a1660ee
```

**Note.** I think we can make it a little bit simpler to understand all, we can just say, does the constraint satisfaction transfer to the real world for the rq2

**Claim.** Does constraint satisfaction transfer to the real world?

**Skip.** How it is measured. The next slide carries the estimand and the budget; the question itself should be sayable in one breath.

## 6.5 — RQ2 — how it gets answered

```yaml
id: rq2
origin: generated
layout: build-list
time_s: 30
transition: cut
generated_hash: 718a5a94963a880a
```

**Claim.** The second question is answered by one number, measured the same way on both sides of the gap.

**On slide.**
- Hardware rate vs simulated rate
- Off-track entries per lap
- Same definition both sides

## 6.6 — RQ3

```yaml
id: rq3-question
origin: generated
layout: callout
time_s: 20
transition: cut
generated_hash: 4df83321ef63e202
```

**Note.** I want to give the real research questions I wrote down

**Claim.** What effect does the sim-to-real technique have on the transfer of constraint satisfaction?

## 6.7 — RQ3 — how it gets answered

```yaml
id: rq3
origin: generated
layout: build-list
time_s: 35
transition: cut
generated_hash: 140e6388a647e83f
```

**Note.** RQ3 — What effect does the sim-to-real technique have on the transfer of constraint satisfaction? Refined to: which domain randomization axes matter most.

**Claim.** The third question is a screening experiment ranking the four layers by main effect, and it is the one whose answer is genuinely open.

**On slide.**
- Which randomization layer matters
- One factor at a time, by layer
- 5 configs × 5 seeds = 25 runs
- Two or three go to the car

# Section 7 — Methodology

> **Bridge.** Three questions of that shape need something to ask them with. First the simulator, which is the instrument rather than a contribution; then what the observation channel actually is in each place, and what the policy reads.

## 7.1 — Methodology

```yaml
id: method-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 7.2 — A new simulator

```yaml
id: the-instrument
origin: human
layout: callout
time_s: 35
transition: cut
generated_hash: e06d4c47e6c88226
```

**Note.** I prefer you say just a new simulator as a separate slide with a callout, You can say that it was inspired by Wheeled labs

**Claim.** A new simulator, where the data never leaves the GPU. Inspired by Wheeled Lab.

**Skip.** the old-versus-new table. The two numbers are the point.

## 7.3 — What that buys

```yaml
id: throughput
origin: human
layout: claim-only
time_s: 30
transition: cut
```

**Note.** I also have the number for the old stack its 167 steps per second

**Claim.** 167 steps per second became 27,548, on the same GPU.

## 7.4 — Nyx

```yaml
id: renderer-nyx
origin: human
layout: claim-above-figure
time_s: 25
transition: cut
visual:
  kind: referential
  sub: screenshot
  asset: renderer_nyx.png
  intent: eight onboard views of the same track, rendered by Nyx
```

**Note.** I want them showed one after another with the title as their name

**Claim.** The same scene as Nyx renders it.

**On slide.**
- 1,505 steps/s

## 7.5 — Madrona

```yaml
id: renderer-madrona
origin: human
layout: claim-above-figure
time_s: 25
transition: cut
visual:
  kind: referential
  sub: screenshot
  asset: renderer_madrona.png
  intent: eight onboard views of the same track, rendered by Madrona
```

**Note.** I want them showed one after another with the title as their name

**Claim.** The same scene as Madrona renders it.

**On slide.**
- 27,548 steps/s

## 7.6 — Rasterizer

```yaml
id: renderer-rasterizer
origin: human
layout: claim-above-figure
time_s: 25
transition: cut
visual:
  kind: referential
  sub: screenshot
  asset: renderer_rasterizer.png
  intent: eight onboard views of the same track, rendered by Rasterizer
```

**Note.** I want them showed one after another with the title as their name

**Claim.** The same scene as Rasterizer renders it.

**On slide.**
- TODO: steps/s

**Skip.** its throughput. I do not have that number; the other two are from the brief.

## 7.7 — Observation

```yaml
id: observation-paths
origin: generated
layout: raw
time_s: 45
transition: cut
raw:
  scene: scenes.rl_loop:Observation
  class: Safety_Observation
generated_hash: 19ef5ceb733e25f1
```

**Note.** this is the second part of the methodology, the first part should be about the simulator

**Claim.** The observation channel is not the same object in the two places: in simulation it comes straight from the environment and can be randomized, and on the car it arrives through the encoder — where there is also no reward in the world to read.

**Skip.** The action side. That is the vector stack, and it gets its own treatment after this.

## 7.8 — In simulation

```yaml
id: sim-observation
origin: generated
layout: raw
time_s: 40
transition: cut
visual:
  intent: the same pipeline as the next slide, but the environment hands the vector
    over directly, with the randomization between it and the actor
raw:
  scene: scenes.encoder_pipeline:SimPipeline
  class: Safety_SimPipeline
```

**Note.** the same pipeline, but instead of getting the image the env already gives the vector directly, with a randomization box in the middle to the actor, and for the cost critic and the value critic it gives the vector without the randomization

**Claim.** In simulation the environment hands the vector over directly. The randomization sits between that vector and the actor, and the two critics read the same vector with the randomization skipped.

**Skip.** The camera. There is no camera in this path, which is exactly the difference from the next slide.

## 7.8 — What the policy actually reads

```yaml
id: encoder-example
origin: generated
layout: raw
time_s: 55
transition: cut
visual:
  intent: three frames from donut_t1.mp4 at 2.5s, 7.5s and 12.5s, morphing into the
    vector. Real onboard frames, not placeholders.
raw:
  scene: scenes.encoder_pipeline:EncoderPipeline
  class: Safety_EncoderPipeline
generated_hash: 4651743ce53f2ce9
```

**Note.** I want a animation showing the enviroment generating some images, passing through the encoder and the encoder spitting out a vector with speed, distance from ceneter and some other stats, and show that that vector is then sent to the policy and that is what deals with DR from real world

**Claim.** Frames out of the environment, through the encoder, out as a short vector of numbers, into the policy — and the encoder is the part that has to survive the real world.

**Skip.** The real field list. speed and centre offset are yours; the rest is a placeholder until it is checked against the environment code.

# Section 8 — How each gap is closed

> **Bridge.** The same figure one last time, with what is actually done about each quantity that differs.

## 8.1 — How each gap is closed

```yaml
id: solve-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 8.2 — Every difference lands on a layer

```yaml
id: dr-layers
origin: generated
layout: table-accented
time_s: 15
transition: cut
content:
  table:
  - - layer
    - element
    - perturbs
  - - image
    - observation
    - appearance
  - - physics
    - P
    - mass, friction, damping
  - - geometry
    - observation and P
    - track shape, boundary
  - - actuation
    - A
    - commanded vs realised
  accent_rows:
  - 4
generated_hash: cd9db7d4515860aa
```

**Note.** Geometry spanning two elements is a fact about the platform, not a flaw in the taxonomy, and connects to the turn: geometry is the one thing the simulator is measured about.

**Claim.** The differences decompose into four layers, and geometry spans two elements because it is both what the camera sees and where the boundary is.

**On slide.**
- Every difference lands on one of these
- Prediction: the image layer ranks last

**Skip.** The 31 knobs. Layer level is the resolution this proposal works at.

## 8.3 — Action

```yaml
id: solve-action
origin: generated
layout: claim-above-figure
time_s: 20
transition: cut
visual:
  kind: constructible
  sub: geometry
  intent: the loop with an action stack on the action path, feeding back into the
    agent
  builder: scenes.rl_loop:loop
  args:
    insert:
    - A
    - action stack
    feedback: true
generated_hash: 4b8af2e8ff4c10cd
```

**Note.** On the bench-calibrated the actuation, I prefer to actually use the idea of feature stack instead (as a easy one)

**Claim.** The action gap is absorbed by feeding the recent actions back into the agent, so it can infer the lag between command and execution.

**On slide.**
- Action stack: the agent reads its own recent actions

**Skip.** Bench calibration of the actuation map. Stacking is the cheaper route.

## 8.4 — Transition

```yaml
id: solve-transition
origin: generated
layout: claim-above-figure
time_s: 25
transition: cut
visual:
  kind: constructible
  sub: geometry
  intent: stacked history inserted on the observation channel — the A_{t-1} arrow
  builder: scenes.rl_loop:loop
  args:
    insert:
    - O
    - history
generated_hash: 50eaeb7cb945b5a1
```

**Note.** stacked observation and action history (whiteboard photo 2, the `A_{T-1}` arrow), physics-layer DR, latency if added. This is implicit system identification from history, not an actuation fix — it belongs on P, not A.

**Claim.** A policy that sees its own recent observations and actions can infer which dynamics it is in, which is why history sits on P and not on A.

**On slide.**
- Stacked observation and action history
- From Project Ace, and it sits on P, not A

## 8.5 — Reward

```yaml
id: solve-reward
origin: generated
layout: claim-only
time_s: 15
transition: cut
generated_hash: 05cd2f9192bfd36a
```

**Note.** r — shares the measurement problem with c.

**Claim.** Reward has no gap to close. It has the cost's measurement problem.

# Section 9 — Results

> **Bridge.** The protocol is not hypothetical: parts of it have already run. What follows is what those runs say, and what they do not say yet.

## 9.1 — Results

```yaml
id: results-break
origin: generated
layout: section-break
time_s: 10
transition: cut
generated_hash: 08b8902c09894d24
```

## 9.2 — What already generalises

```yaml
id: generalisation
origin: human
layout: raw
time_s: 40
transition: cut
raw:
  scene: scenes.clips:GeneralizationVideo
  class: Safety_GeneralizationVideo
generated_hash: 81a7ec6014778072
```

**Note.** Here it should go the video called generalization in the deepracer folder

**Claim.** A feature-vector policy completing held-out tracks with no visual randomization, many of them at once.

## 9.3 — Inference on the car

```yaml
id: onnx-inference
origin: human
layout: raw
time_s: 45
transition: cut
raw:
  scene: scenes.clips:OnnxInference
  class: Safety_OnnxInference
```

**Note.** I created a inference node on the physical car and I will give you a video of it running with it, it works well, its as onnx_inference in the folder

**Claim.** An ONNX inference node running on the physical car, and it works.

## 9.5 — What comes next

```yaml
id: next-steps
origin: human
layout: build-list
time_s: 45
transition: cut
```

**Note.** I also think I need a list of todos at the end, like make more robust experiments using HPO, implement Safe RL algorithms and evaluate on the real world

**Claim.** Three things left, in order.

**On slide.**
- More robust experiments, using HPO
- Implement the safe RL algorithms
- Evaluate on the real world

# Section 10 — Backup

> **Bridge.** Everything past this point was cut for time and kept for questions; the order is the order it is most likely to be asked for.

## 10.1 — What that number is not

```yaml
id: rq2-limit
origin: human
layout: callout
time_s: 20
transition: cut
content:
  backup_of: callout
backup: true
demoted_because: Remove this other slide too
generated_hash: d53f2d86a539e4e9
```

**Note.** Limitation recorded: this is not the constrained objective, which weights duration and discounting.

**Claim.** Entries per lap is not the constrained objective. It is the part of it that can be measured on hardware.

## 10.2 — Discussion

```yaml
id: discussion-slide
origin: human
layout: claim-only
time_s: 45
transition: cut
content:
  backup_of: claim-only
backup: true
demoted_because: I want to finish the slides just before this one
generated_hash: cfcdfeb303e32745
```

**Note.** I also want to remove the schedule (and just put a slide to discuss)

**Claim.** Where would you push on this?

**Skip.** The month-by-month schedule. It is in the document; a slide of it invites the wrong argument.

## 10.3 — Back to the car

```yaml
id: close
origin: human
layout: full-bleed-figure
time_s: 35
transition: cut
visual:
  kind: referential
  sub: photo
  intent: the same opening shot of the real DeepRacer Evo on the real track — the
    bookend
content:
  backup_of: full-bleed-figure
backup: true
demoted_because: I want to finish the slides just before this one
generated_hash: e627a2bdc05db0ac
```

**Claim.** The talk closes on the car it opened with, now as the place a constraint gets measured rather than as a demonstration.

## 10.4 — The threat to the ranking

```yaml
id: takeoff-lottery
origin: human
layout: claim-above-figure
time_s: 30
transition: cut
visual:
  kind: constructible
  sub: axes
  intent: final return under identical config and seed, showing the two outcomes as
    separated clusters, with the spread between them drawn as the noise floor the
    ranking has to clear
content:
  backup_of: claim-above-figure
backup: true
demoted_because: Again I want to delete this slide
generated_hash: af4c61bf931faf48
```

**Note.** Either outcome is usable: small variance validates the 5-seed protocol; large variance gives a measured noise floor, and the ranking is reported as resolving only effects above it.

**Claim.** Seed-level variance is measured before the ablation is designed, and reporting the floor it sets is a credibility gain rather than a weakness.

**On slide.**
- Same config and seed: park, or fly
- Ranking resolves above the floor

## 10.5 — What this experiment cannot answer

```yaml
id: rq3-limits
origin: human
layout: build-list
time_s: 25
transition: cut
content:
  backup_of: build-list
backup: true
demoted_because: I think I want to delete this slide
generated_hash: c869500658093c9b
```

**Note.** And not even I could understand this

**Claim.** The screen is deliberately coarse: it ranks layers, it cannot rank knobs, and it cannot see two layers interacting.

**On slide.**
- OFAT cannot see interactions between layers
- A high image-layer rank does not say which knob
- Knob-by-knob resolution is dissertation work

## 10.6 — The goal

```yaml
id: the-goal
origin: generated
layout: claim-only
time_s: 15
transition: cut
content:
  backup_of: claim-only
backup: true
demoted_because: You basically repeat those in two slides
generated_hash: e9e1a9bd6095eeb5
```

**Note.** Goal: to investigate whether a policy trained in simulation under explicit safety constraints continues to satisfy those constraints when deployed on physical hardware.

**Claim.** Does a policy trained in simulation under explicit safety constraints continue to satisfy those constraints when deployed on physical hardware?

## 10.7 — Domain randomization

```yaml
id: what-is-dr
origin: generated
layout: term-reveal
time_s: 40
transition: cut
content:
  backup_of: term-reveal
backup: true
demoted_because: I will explain what is domain randomization in the platform
generated_hash: 7d0aa0dafc9c3830
```

**Note.** I need to explain what is the domain randomization exaclty after

**Claim.** Instead of guessing one value for what the simulator cannot measure, train across a range of values, so the policy cannot come to depend on any single guess being right.

**On slide.**
- Domain randomization

## 10.8 — The turn

```yaml
id: the-turn
origin: generated
layout: callout
time_s: 85
transition: cut
content:
  backup_of: callout
backup: true
demoted_because: Also skip "the simulator is worng about whether..."
generated_hash: d41cc4acbcfb77c6
```

**Claim.** The simulator is wrong about whether the car crosses the boundary and right about where the boundary is. What transfers is the constraint.

**Cue.** whether you cross depends on the dynamics conceded to be wrong — which is what the budget d and the conservatism of the Lagrangian absorb

## 10.9 — The boundary is geometry

```yaml
id: the-predicate
origin: generated
layout: claim-above-figure
time_s: 55
transition: cut
visual:
  kind: constructible
  sub: geometry
  intent: a track polygon with its boundary, the car's four wheel positions on it,
    one wheel across the line — the off-track condition drawn as the geometric predicate
    it is
content:
  backup_of: claim-above-figure
backup: true
demoted_because: You can also skip "the boundry is geometry"
generated_hash: 294bd7fc4a48c2c4
```

**Note.** Cost: one wheel off track. Stricter than DeepRacer's `all_wheels_on_track`.

**Claim.** The off-track condition is a geometric predicate over wheel positions and a track polygon, and track geometry is measured rather than modelled.

**On slide.**
- Off track: one wheel outside the polygon

## 10.10 — What is being run

```yaml
id: algorithm
origin: generated
layout: build-list
time_s: 55
transition: cut
content:
  backup_of: build-list
backup: true
demoted_because: I think its too much to add, I cannot cover everything
generated_hash: b7e58baef2815bd7
```

**Note.** I want to also remove the part about PPO-Lagrangian I think its too much to add, I cannot cover everything

**Claim.** The algorithm is standard and the environment contract is not, and the price of that choice is stated rather than hidden.

**On slide.**
- PPO-Lagrangian, by hand on rsl-rl
- One dual variable
- Reproduced on Safety-Gymnasium
- Limitation: comparability lost

**Skip.** How PPO-Lagrangian works. The committee is voting on the questions, not on the dual update.

## 10.11 — Render it away, or randomize over it

```yaml
id: renderer-cost
origin: generated
layout: table-accented
time_s: 20
transition: cut
content:
  table:
  - - renderer
    - steps/s
  - - Nyx
    - 1,505
  - - Madrona
    - 27,548
  accent_rows:
  - 3
  backup_of: table-accented
backup: true
demoted_because: the thing about nyx and madrona should be in the first slide of the
  methodology
generated_hash: 0432e7e790b40fa6
```

**Claim.** Closing the appearance gap by rendering harder costs eighteen times the throughput and randomizing over it costs nothing, which is why the mitigation is randomization and not fidelity.

**On slide.**
- 18× to render it away. Free to randomize over it

**Cue.** alike to a human eye is not alike to a CNN; the OFAT rank is the actual test

**Skip.** The full throughput table and the compute arithmetic. Backup.

## 10.12 — In expectation, not worst case

```yaml
id: expectation-form
origin: generated
layout: callout
time_s: 35
transition: cut
content:
  backup_of: callout
backup: true
demoted_because: Also dont like this one
generated_hash: 9fdb2df0912144ce
```

**Note.** To be stated explicitly on the CMDP slide — a committee strong on core RL will ask which is being solved.

**Claim.** The constraint holds in expectation over the randomized parameters, not in the worst case.

## 10.13 — Cost

```yaml
id: solve-cost
origin: generated
layout: claim-above-figure
time_s: 20
transition: cut
visual:
  kind: constructible
  sub: geometry
  intent: a privileged cost critic on the cost channel
  builder: scenes.rl_loop:loop
  args:
    cost: true
    insert:
    - c
    - cost critic
content:
  backup_of: claim-above-figure
backup: true
demoted_because: This part about cost I think its better just saying
generated_hash: 7f11d461b0d5d9ec
```

**Note.** This part about cost I think its better just saying

**Claim.** The cost is measurable on both sides of the gap — from privileged state in simulation, and by annotating video from the car.

**On slide.**
- Cost critic in simulation
- Event rate from video on hardware

**Skip.** Annotation protocol detail. Backup.

## 10.14 — Throughput and renderers

```yaml
id: b-throughput
origin: generated
layout: table-accented
time_s: 60
transition: cut
content:
  backup_of: table-accented
  table:
  - - renderer
    - steps/s
  - - Nyx
    - 1,505
  - - Madrona
    - 27,548
  accent_rows:
  - 3
backup: true
demoted_because: the argument needs the 18x, not the table
generated_hash: d789d3836e0ca9a4
```

**Claim.** The full throughput comparison, plus the arithmetic that turns steps per second into the compute budget for twenty-five runs.

**On slide.**
- Throughput, and what it buys in runs

## 10.15 — Hardware annotation protocol

```yaml
id: b-annotation
origin: generated
layout: build-list
time_s: 60
transition: cut
content:
  backup_of: build-list
backup: true
demoted_because: protocol detail, only needed if the estimand is challenged
generated_hash: f1c42450f6ec6001
```

**Claim.** How a violation gets from onboard video to a number, and what makes that number comparable to the simulated one.

**On slide.**
- One wheel out, annotated from video
- Rising edges, not frames
- Same definition computes the sim rate

## 10.16 — If RQ1 fails

```yaml
id: b-rq1-fallback
origin: generated
layout: claim-only
time_s: 60
transition: cut
content:
  backup_of: claim-only
backup: true
demoted_because: a fallback the committee should know exists but should not spend
  time on
generated_hash: e50404b7c4f6c675
```

**Claim.** If the CMDP does not beat shaping in simulation, the thesis becomes a characterisation of violation across the boundary, on the same instrument and protocol.
