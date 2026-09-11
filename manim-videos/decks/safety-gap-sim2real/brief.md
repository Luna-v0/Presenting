---
slug: safety-gap-sim2real
title: Bridging the gap of safety between simulation and reality for small-scale autonomous vehicles
target: manim
genre: research-talk
technicality: 4
interaction: none
duration_min: 30
audience: Master's proposal defence, PUC-Rio. Two committee members from machine learning; strong on core RL theory, light on safe RL. Delivered in English.
narrative_frozen: false
---

## Narrative

They arrive believing the sim-to-real gap is a fidelity problem — you close it by
modelling better, or by randomizing over what you failed to model. The two opening
videos produce exactly that instinct, and it is named out loud rather than defused.

The turn is an argument, not a result. The simulator is *measured* about track
geometry and *modelled* about friction, actuation latency and slip. The gap lives
entirely in the second list. But the off-track condition is a geometric predicate
over wheel positions and a track polygon — it lives in the first. The simulator is
therefore wrong about *whether* the car crosses the boundary and right about *where
the boundary is*. So the thing that transfers is not the dynamics but the constraint,
and it should be encoded as one instead of buried in a shaped reward maximised under
a wrong model.

They leave believing the CMDP is the right formalism for this platform, which makes
RQ1–RQ3 the obvious questions rather than three questions announced. The simulator
is the instrument that makes constraint violation measurable at the scale a CMDP
study needs.

Two supporting arguments that must be made explicitly rather than assumed.

**Why the small car.** Violations are cheap, which invites the question of why
safety machinery is needed at all. The answer given up front: the platform is
valuable *because* violations are cheap — it is one of the few settings where
constraint violation can be measured on real hardware, repeatedly, with
statistical power. The constraint is not there because a crash matters; the
constraint is the object of study, and this is a place it can be studied.

**Why the matching observations do not undercut the thesis.** The onboard sim and
real recordings look alike, so the observation axis shows fidelity succeeding.
That is used as evidence against the fidelity instinct, not for it: rendering was
good enough here and the car still fails, so the difficulty lives elsewhere. This
converges with the feature-vector policy generalising across tracks without any
visual randomization.

## Why I'm presenting

Proposal defence. The committee is voting on whether the research questions,
evaluation protocol and four-month schedule are sound. The systems work already
done is evidence the proposed experiments can actually be run, not a result in
its own right — in the user's words, "this new simulator is solely a tool to make
everything faster."

## What the audience should do

Accept the CMDP framing as appropriate for this platform; approve RQ1–RQ3 and the
evaluation protocol; argue about RQ3, which is where the answer is genuinely open
and where a preliminary result already complicates the question.

## Narrative spine — beat budget

Structure is MDP -> CMDP -> sim2real -> solution, from the user's whiteboards.
The canonical loop figure (AGENT / ENV, S_t, R_t, A_T) is drawn once and returned
to throughout; the gap pass annotates it in red, one element at a time, in the
user's own notation `X_sim != X_real`.

| Beat | Min | Notes |
|---|---|---|
| Two videos; small-car argument; name the fidelity instinct | 3 | Illustration, not measurement — say so |
| Related work, grouped in three | 3 | Platform / neighbours / formalism |
| MDP tuple and loop figure; then CMDP: add c, d, feasible set | 4 | Cost motivated before the pass, not after |
| **Gap pass** — observation, A, P, r, then c breaks the pattern | 6 | The turn is the last slide of this beat |
| **Solve pass** — one mitigation per element | 5 | Robust CNN; stacking; calibration; cost critic |
| RQ1–RQ3, evaluation protocol | 6 | Longest single block — the thing being voted on |
| Preliminary state, instrument | 2 | Han and Czechmanowski return here |
| Risks, scope, schedule; close on the real car | 1 | Bookend the opening |

### The gap pass

Uniform rhythm, then a break. Order matters and is load-bearing.

- **Observation** — onboard sim and real recordings side by side. They look *alike*.
  Framing: this is the axis where the fidelity approach worked, and the car still
  fails. Kills the fidelity instinct with evidence in thirty seconds rather than
  by argument. The renderer benchmark lives here: closing this gap by rendering
  harder costs 18x (Nyx 1,505 vs Madrona 27,548 steps/s, same GPU).
  Stated prediction: the image layer should rank near-zero in the OFAT screen.
  Objection to pre-empt: alike to a human eye is not alike to a CNN; the OFAT
  rank is the actual test.
- **A** — commanded vs realised control. A real gap, bench-measurable.
- **P** — friction, slip, latency. Where the difficulty actually lives.
- **r** — not a true gap; reward is chosen, not a property of the world. What
  differs is that it is computable in simulation only.
- **c** — **the pattern breaks.** The boundary is a geometric predicate over wheel
  positions and a track polygon; geometry is *measured*, not modelled. The
  simulator is wrong about whether the car crosses and right about where the
  boundary is. Counterargument pre-empted in-beat: whether you cross depends on
  the dynamics conceded to be wrong — which is what the budget d and the
  conservatism of the Lagrangian absorb.

### The solve pass

One mitigation per element, same figure, same order.

- Observation — robust CNN encoder in front of the agent (whiteboard photo 4), image-layer DR.
- A — bench calibration of the actuation map g.
- P — stacked observation and action history (whiteboard photo 2, the `A_{T-1}`
  arrow), physics-layer DR, latency if added. This is implicit system
  identification from history, not an actuation fix — it belongs on P, not A.
- r — shares the measurement problem with c.
- c — privileged cost critic; event-rate measurement on hardware.

## Committed research questions (unchanged since 26 May)

Goal: to investigate whether a policy trained in simulation under explicit safety
constraints continues to satisfy those constraints when deployed on physical hardware.

- **RQ1** — Can Time Trial and Object Avoidance be reformulated as CMDPs, and does a
  CMDP-trained policy achieve constraint satisfaction in simulation comparable to or
  better than a reward-shaped baseline?
- **RQ2** — Does that constraint satisfaction transfer to a physical DeepRacer Evo,
  measured by on-hardware violation rate relative to simulation?
- **RQ3** — What effect does the sim-to-real technique have on the transfer of
  constraint satisfaction? Refined to: which domain randomization axes matter most.

RQ4 (algorithm comparison) dropped and stays dropped.

## Settled decisions

- PPO-Lagrangian, implemented by hand on top of rsl-rl. Reproduction check against
  one Safety-Gymnasium task to establish implementation correctness.
- Contract is rsl-rl VecEnv, **not** Gymnasium or Safety-Gymnasium. Claimed as a
  batched CMDP environment contract with cost as a first-class channel. Lost
  comparability with existing safe-RL implementations stated as a limitation.
- Single dual variable per constrained problem, not per environment.
- RQ2 estimand: off-track entries per lap (rising edges of the cost indicator),
  computed identically in simulation and from video. Limitation recorded: this is
  not the constrained objective, which weights duration and discounting.
- Cost: one wheel off track. Stricter than DeepRacer's `all_wheels_on_track`.
- Budget d: to be set empirically from the September unconstrained-PPO hardware
  violation rate, not picked a priori.
- 5 seeds. 2/3 – 1/3 track split (~40 train / ~20 held out); check for near-duplicate
  track families before splitting.
- Domain randomization organised as four layers, catalogued in
  `deepracer-studies/experiments/ablation_individual.ipynb` (31 knobs; the original
  `visual` layer is merged into `image`):

  | Layer | Tuple element | Perturbs |
  |---|---|---|
  | image | observation | scene appearance and the rendered observation |
  | physics | P | mass, friction, damping |
  | geometry | observation and P | track shape — what the camera sees and where the boundary is |
  | actuation | A | commanded versus realised control |

  Geometry spanning two elements is a fact about the platform, not a flaw in the
  taxonomy, and connects to the turn: geometry is the one thing the simulator is
  measured about.

- Ablation: one-factor-at-a-time screening at the **layer** level, each layer alone
  against baseline, ranked by main effect. Five configurations x 5 seeds = 25 runs.
  Starts on a single track. Two limitations stated explicitly: interaction effects
  are not observable under OFAT, and the image layer merges pre-render appearance
  with post-render pixel operations, so a high rank there does not localise further.
  Knob-level resolution is dissertation work, not proposal work.

- Latency randomization (observation delay, action delay, control-frequency jitter)
  is absent from the catalogue. Either added to the actuation layer before the
  ablation runs, or named as a limitation. Unresolved.

- Constraint under randomization: expectation form
  E_xi[J_c(pi, xi)] <= d, not worst-case sup_xi J_c(pi, xi) <= d. To be stated
  explicitly on the CMDP slide — a committee strong on core RL will ask which is
  being solved.
- Hardware annotation by eye from video. Full ablation runs in simulation; two or
  three configurations go to the car.
- Related work: dedicated section, grouped in three. Han and Czechmanowski reappear
  later where they do argumentative work.
- No code on screen.
- Terminology: the tuple element is called **observation** throughout, in the user's
  own framing — the car acts on a 160x120 camera image and a feature vector, never
  on the state, so this is also the accurate word for the system. The canonical loop
  figure keeps whichever label the slides use, consistently. One exception is stated
  once in the CMDP beat: the cost c is a function of state, not observation, which is
  why the privileged cost critic exists and why hardware measurement needs video.

## Related work on slides

Platform: Balaji et al. 2020, DeepRacer, arXiv:1911.01562.
Neighbours: Han et al. 2025, Wheeled Lab, CoRL, arXiv:2502.07380; Czechmanowski et
al. 2025, IROS, arXiv:2504.02420.
Formalism and algorithms: Altman 1999, CMDPs; Achiam et al. 2017, CPO; Stooke et al.
2020, PID-Lagrangian; Ji et al. 2023, Safety-Gymnasium.

Differentiation from Wheeled Lab: no constraint formalism, no cost channel — it is a
fidelity-and-randomization framework, which is the received view the turn argues
against. Differentiation from Czechmanowski: they measure the effect of these design
choices on performance and safety informally; this work measures the effect on
constraint satisfaction transfer, with a budget and a violation rate.

Document-only: García & Fernández 2015; Tobin et al. 2017; Peng et al. 2018; Pinto et
al. asymmetric actor–critic; Kumar et al. 2021 RMA.

## Schedule

| Period | Work | Gate |
|---|---|---|
| Sep | Hardware: unconstrained PPO on the car, bench-calibrate the actuation map, annotation protocol | Hardware loop closed; real-world PPO baseline; d grounded |
| Oct | PPO-Lagrangian implemented; Safety-Gymnasium reproduction; RQ1 in simulation | **Gate — thesis viable from here** |
| Nov | RQ2: constrained policy on hardware vs its simulation rate | RQ2 answered |
| Nov–Dec | RQ3: OFAT screening over DR axes, simulation-wide; hardware on selected configs | RQ3 answered |
| Dec | Object Avoidance, conditional on Time Trial completing | Optional |
| Jan | Writing | — |

Object Avoidance is explicitly conditional. Not currently implementable — no obstacle
entities exist in the environment and the reward parameter set is Time Trial only.

## Backup slides

Throughput and renderer table; Lagrangian update with the PID variant; hardware
annotation protocol; compute budget arithmetic; RQ1 failure fallback (characterisation
study of constraint violation across the boundary for unconstrained policies).

## Out of scope

AWS SageMaker, RoboMaker, the DeepRacer console reward-function interface. Action
translation as a separate contribution — the actuation map is calibrated on a bench,
not learned. Interaction effects between DR axes. Constrained POMDP guarantees:
the claim is a CMDP over stacked histories, with guarantees degrading accordingly.
Per-environment lighting randomization, unsupported in Genesis 1.2.

## Threats to the protocol

**Takeoff lottery.** `best_camera_diverse.ipynb` records that identical config and
seed can park or fly on GPU nondeterminism alone. If that variance exceeds the gaps
between the four DR layers, the OFAT ranking is unreadable. An analysis of its
magnitude runs before the ablation is designed. Either outcome is usable: small
variance validates the 5-seed protocol; large variance gives a measured noise floor,
and the ranking is reported as resolving only effects above it. Reporting the noise
floor is a credibility gain, not a weakness.

**Reward hacking, held back.** `best_camera_completion.ipynb` records that
`safe_progress` reward-hacked itself into parking and `lap_bonus` produced
never-crashing crawlers — both the same failure, a shaped reward satisfied by not
driving, which is the strongest available argument for the CMDP framing and is the
user's own evidence rather than a citation. Deliberately **not** on a slide for this
defence: needs more evaluation before it can be defended. Revisit for the
dissertation.

## Open, non-blocking

Reward-shaped baseline specification. Tolerance band epsilon for RQ2. Annotation
protocol detail. User's own version of the CMDP tuple slide layout. Steps-to-convergence
from an existing run, which determines whether the ablation stays OFAT or can widen.
The Gymnasium wording in the current abstract and contributions list still needs
revising to match the rsl-rl contract.
