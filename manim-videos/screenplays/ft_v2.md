<!---
Take each Heading 1 as a separated scene.
Take each Heading 2 as a slide.
-->

# Fine-tuning and Postprocessing LLMs part 2

## Previously we talked about

LoRA, SFT and Distillation (but it is not much important)

## Previously we talked about

RL and Human Feedback in RL problems. Where the reward is almost near a reward of a normally trained RL model.

(use rl_loop.png image)

## Previously we talked about

The Bradley Terry model and how it is a simillar problem as a chess Elo rating system.

<!---
Use the animation from the bradley terry elo py video in this repo. 
-->

## Previously we talked about

We also talked about RL with LLMs and how OpenAI trained using STF and PPO. 

# Continuing...

## The PPO family for RL FT

(Image of PPO family)

# Feedback without Humans

## RL from Verifiable Reward (RLVR)

GRPO is a variation of PPO, I can explain it at the end of the presentation. But the important nuance is that rather then using human feedback it goes back to using simple reward functions based on rules to train the model.

## RL from Verifiable Reward (RLVR)

In the original paper for GRPO they used it to train a model to be better at solving math problems. They did a lot in the paper, but we will focus on the math reward function.

## RL from Verifiable Reward (RLVR)

<!---
Will put later
-->

## RL from AI Feedback (RLAIF)

A trend that started is to use LLMs to train the Reward Model instead of Humans. It is highly associated with Anthropic and their Constitutional AI. It is definetly more scalablen than humans and it is highly used. 

# Why I mention Bradley-Terry (a few times)

## Bradley Terry do NOT presumes

1. People can be reasoning agents and still give contradicting preferences.
2. The reward model that is learning it is biases to the distribution of the initial model by design. 

This makes it a lot more scalable than the older methods.

## It is not transitive

P(A≻B),P(B≻C),P(C≻A).

But for a ELO ranking system this is impossible since:

r(A)>r(B)>r(C)>r(A) --> Contradiction

## Why biased to the dataset ?

Because if amount of A > C then Bradley-Terry will give a higher reward for A than C. 

# What to use then?

## Nash Learning From Human Feedback

The general idea is really simple, instead of BT, lets train a binary classifier to predict the preference. (given two answers, which one is better?)

Then we treat this as a two player game between the human and the model.

## NLHF Policy Gradient 


<!---
Use the animation from the nlhf.py 
-->

# So no more Bradley-Terry right?


## Not really

For well behaved problems, (like the ones solvable by RLVR) BT works perfectly.

# If you want to play with all that

## Interesting Libraries

TRL – RL for LLM algorithms
PEFT – LoRA and other Adapters
UNSLOTH – Easy Training Loop for a whole FT pipeline for LLMs
ART – Adaptable training loop for RL pipelines for LLMs

## Harness

Hermes agents – Claude-code-like CLI that uses online RL to learn based on your feedback (uses the cloud and no local computation!)

## Some thesis ideas

1. Fine tune Deep Racer (using this new gym interface) (but no real world test)
2. Test other PG algorithms without no Bradley Terry
3. Fine tune a robotics problem to solve a task using some ideas of LLM fine tuning
    a. Use a preference Model instead of Bradley Terry
    b. Use a non-deterministic model and do GRPO
4. Fine tune SLMs for a RLVR task (coding, websearch, reasoning, etc)
5. Evaluate LoRA with other domains. 
6. Human Feedback to create a time-to-talk model (based on the BT model).