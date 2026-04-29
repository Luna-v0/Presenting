"""Fine-tuning & Postprocessing LLMs - Part 2.

Built from screenplays/ft_v2.md. Each H1 in the screenplay is one Scene below;
H2s under each H1 become individual slides inside that Scene.

Two existing animations are spliced into the deck:
    scenes/bradley_terry_elo.py :: BradleyTerryToElo  (recap of part 1)
    scenes/nlhf.py              :: NLHF               (NLHF policy gradient)
Both originally subclass Scene; we wrap them as Slide subclasses below so
manim-slides can present them as single advancing slides inside the deck.

Drop project images into scenes/assets/ — referenced by name from
the screenplay. Until they exist, a labeled placeholder is shown.

Render & present:
    uv run manim-slides render scenes/ft_v2.py FtV2_01_Recap FtV2_BTAnim FtV2_02_RecapAfter \\
        FtV2_03_Continuing FtV2_04_FeedbackNoHumans FtV2_05_WhyBT FtV2_06_NLHFIntro \\
        FtV2_NLHFAnim FtV2_NLHFResults FtV2_07_NoMoreBT FtV2_08_Outro -ql
    uv run manim-slides present FtV2_01_Recap FtV2_BTAnim FtV2_02_RecapAfter \\
        FtV2_03_Continuing FtV2_04_FeedbackNoHumans FtV2_05_WhyBT FtV2_06_NLHFIntro \\
        FtV2_NLHFAnim FtV2_NLHFResults FtV2_07_NoMoreBT FtV2_08_Outro
"""

from pathlib import Path

import numpy as np

from manim import (
    BLACK,
    DOWN,
    ORIGIN,
    UP,
    Arrow,
    Create,
    FadeIn,
    Group,
    ImageMobject,
    Line,
    MathTex,
    Rectangle,
    RoundedRectangle,
    Text,
    VGroup,
    Write,
)
from manim_slides import Slide
from manim_beamer.blocks import AlertBlock, ExampleBlock, RemarkBlock
from manim_beamer.lists import (
    AdvantagesList,
    BulletedList,
    DisadvantagesList,
    ItemizedList,
)
from manim_beamer.slides import (
    BeamerSlide,
    SlideShow,
    SlideWithBlocks,
    SlideWithList,
)

# Existing standalone animation scenes — wrapped as Slides below.
from scenes.bradley_terry_elo import BradleyTerryToElo
from scenes.nlhf import NLHF


ASSETS_DIR = Path(__file__).resolve().parent / "assets"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def math(tex: str, font_size: int = 30) -> MathTex:
    return MathTex(tex, color=BLACK, font_size=font_size)


def text(s: str, font_size: int = 30) -> Text:
    return Text(s, font="TeX Gyre Termes", color=BLACK, font_size=font_size)


def asset_image(name: str, max_width: float = 8.0, max_height: float = 4.5):
    """Load scenes/assets/<name>; fall back to a labelled placeholder if missing.

    Returns a Group (mixed-mobject container) so callers can FadeIn either form.
    """
    path = ASSETS_DIR / name
    if path.exists():
        img = ImageMobject(str(path))
        img.scale_to_fit_width(max_width)
        if img.height > max_height:
            img.scale_to_fit_height(max_height)
        return Group(img)

    rect = Rectangle(
        width=max_width,
        height=max_height,
        color=BLACK,
        fill_color="#f0f0f0",
        fill_opacity=1,
        stroke_width=2,
    )
    label = text(f"[image: {name}]", font_size=28)
    placeholder = VGroup(rect, label)
    label.move_to(rect.get_center())
    return Group(placeholder)


# ─────────────────────────────────────────────────────────────────────────────
# Custom slide types
# ─────────────────────────────────────────────────────────────────────────────

class ImageSlide(BeamerSlide):
    """Title + subtitle + a centered image (or placeholder)."""

    def __init__(self, title: str, subtitle: str, image_name: str, caption: str | None = None):
        super().__init__(title=title, subtitle=subtitle)
        self.image_name = image_name
        self.caption_str = caption

    def draw(self, origin=None, scale: float = 1.0, target_scene=None, animate: bool = True):
        if target_scene is None:
            target_scene = self

        img = asset_image(self.image_name, max_width=12.0, max_height=6.5)
        img.move_to(ORIGIN)
        target_scene.play(FadeIn(img))
        target_scene.wait(0.5)
        target_scene.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# Animated PPO-family diagram
# ─────────────────────────────────────────────────────────────────────────────

LIGHT_BLUE = "#bcd0e4"
LIGHT_RED = "#e8b8b8"
BLUE_STROKE = "#5b7da5"
RED_STROKE = "#a95c5c"


def family_node(label: str, fill_color: str, stroke_color: str) -> VGroup:
    box = RoundedRectangle(
        width=1.7,
        height=0.7,
        corner_radius=0.12,
        color=stroke_color,
        fill_color=fill_color,
        fill_opacity=1.0,
        stroke_width=2,
    )
    txt = Text(label, font="TeX Gyre Termes", color=BLACK, font_size=24, weight="BOLD")
    txt.move_to(box.get_center())
    return VGroup(box, txt)


class PPOFamilySlide(BeamerSlide):
    """Hand-drawn PPO/DPO family tree, revealed branch-by-branch."""

    def __init__(self):
        super().__init__(
            title="The PPO family for RL fine-tuning",
            subtitle="A small zoo of PG variants",
        )

    def draw(self, origin=None, scale: float = 1.0, target_scene=None, animate: bool = True):
        if target_scene is None:
            target_scene = self

        title = self.title_text.copy()
        subtitle = self.subtitle_text.copy()
        target_scene.play(Write(title), Write(subtitle))
        target_scene.next_slide()

        ppo = family_node("PPO", LIGHT_BLUE, BLUE_STROKE).move_to([-3.0, 1.2, 0])
        dpo = family_node("DPO", LIGHT_BLUE, BLUE_STROKE).move_to([3.0, 1.2, 0])
        grpo = family_node("GRPO", LIGHT_RED, RED_STROKE).move_to([-3.0, -0.4, 0])
        gspo = family_node("GSPO", LIGHT_RED, RED_STROKE).move_to([-5.0, -2.2, 0])
        gdpo = family_node("GDPO", LIGHT_BLUE, BLUE_STROKE).move_to([-1.0, -2.2, 0])
        qrpo = family_node("QRPO", LIGHT_BLUE, BLUE_STROKE).move_to([3.0, -2.2, 0])

        target_scene.play(FadeIn(ppo), FadeIn(dpo))
        target_scene.next_slide()

        a_ppo_grpo = Arrow(
            ppo.get_bottom(), grpo.get_top(),
            buff=0.1, color=BLACK, stroke_width=3, max_tip_length_to_length_ratio=0.12,
        )
        target_scene.play(FadeIn(grpo), Create(a_ppo_grpo))
        target_scene.next_slide()

        a_grpo_gspo = Arrow(
            grpo.get_bottom(), gspo.get_top(),
            buff=0.1, color=BLACK, stroke_width=3, max_tip_length_to_length_ratio=0.12,
        )
        a_grpo_gdpo = Arrow(
            grpo.get_bottom(), gdpo.get_top(),
            buff=0.1, color=BLACK, stroke_width=3, max_tip_length_to_length_ratio=0.12,
        )
        elbow_start = grpo.get_right()
        elbow_corner = np.array([3.0, elbow_start[1], 0.0])
        a_grpo_qrpo = VGroup(
            Line(elbow_start, elbow_corner, color=BLACK, stroke_width=3),
            Arrow(
                elbow_corner, qrpo.get_top(),
                buff=0.1, color=BLACK, stroke_width=3, max_tip_length_to_length_ratio=0.12,
            ),
        )
        target_scene.play(
            FadeIn(gspo), FadeIn(gdpo), FadeIn(qrpo),
            Create(a_grpo_gspo), Create(a_grpo_gdpo), Create(a_grpo_qrpo),
        )
        target_scene.next_slide()

        a_dpo_qrpo = Arrow(
            dpo.get_bottom(), qrpo.get_top(),
            buff=0.1, color=BLACK, stroke_width=3, max_tip_length_to_length_ratio=0.08,
        )
        target_scene.play(Create(a_dpo_qrpo))
        target_scene.wait(0.5)
        target_scene.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# Aliases for the existing animation Slides — give them deck-flow names
# matching the screenplay order (the originals already inherit from Slide).
# ─────────────────────────────────────────────────────────────────────────────

class FtV2_BTAnim(BradleyTerryToElo):
    """Bradley-Terry → Softmax → Elo (recap animation, part 1 deck)."""


class FtV2_NLHFAnim(NLHF):
    """Natural Language Human Feedback policy-gradient animation."""


# ─────────────────────────────────────────────────────────────────────────────
# Slide factories — one per H1 scene in the screenplay
# ─────────────────────────────────────────────────────────────────────────────

def _scene01_recap_before_bt():
    """Title + first three 'Previously we talked about' slides (LoRA/SFT, RLHF, BT lead-in)."""
    title_slide = SlideWithBlocks(
        title="Fine-tuning & Postprocessing LLMs",
        subtitle="Part 2 — recap and what comes next",
        blocks=[],
    )

    recap_lora = SlideWithList(
        title="Previously we talked about",
        subtitle="Part 1 quick recap",
        beamer_list=ItemizedList(
            items=[
                "LoRA (low-rank adapters)",
                "Supervised fine-tuning (SFT)",
                "Distillation (less central — set aside for today)",
            ],
        ),
    )

    bt_lead_in = SlideWithList(
        title="Previously we talked about",
        subtitle="Bradley-Terry as a chess-Elo rating problem",
        beamer_list=ItemizedList(
            items=[
                "Pairwise preferences → reward / rating per response.",
                "Same shape as Elo: pick a winner, update the score.",
                "Watch the formulas morph — Bradley-Terry → softmax → Elo.",
            ],
        ),
    )

    rl_robot = ImageSlide(
        title="Previously we talked about",
        subtitle="RL + HF + Robotics",
        image_name="rl_robot.png",
        caption="RL from human feedback can be used to train on RL tasks.",
    )

    return [title_slide, recap_lora, bt_lead_in, rl_robot]


def _scene02_recap_after_bt():
    """Final 'Previously...' slide (PPO with LLMs)."""
    recap_ppo = SlideWithList(
        title="Previously we talked about",
        subtitle="RL with LLMs — the OpenAI recipe",
        beamer_list=ItemizedList(
            items=[
                "SFT to get a reasonable starting policy.",
                "Train a reward model from human preferences (Bradley-Terry).",
                "PPO to optimize the policy against that reward model.",
            ],
        ),
    )

    recap_rlhf = ImageSlide(
        title="Previously we talked about",
        subtitle="How this training is done",
        image_name="rlhf_loop.png",
        caption="Reward learned from preferences is almost the same as a normally trained RL model.",
    )
    return [recap_ppo, recap_rlhf]


def _scene03_continuing():
    """'Continuing...' banner + PPO family image."""
    banner = SlideWithBlocks(
        title="Continuing\u2026",
        subtitle="Where the field went after PPO+RLHF",
        blocks=[],
    )

    ppo_family = PPOFamilySlide()

    return [banner, ppo_family]


def _scene04_feedback_no_humans():
    """RLVR (3 slides) + RLAIF."""
    section = SlideWithBlocks(
        title="Feedback without humans",
        subtitle="When the reward stops being a person",
        blocks=[],
    )

    rlvr_intro = SlideWithBlocks(
        title="RL from Verifiable Reward (RLVR)",
        subtitle="GRPO swaps human feedback for rule-based rewards",
        blocks=[
            ExampleBlock(
                title="GRPO",
                content="A PPO variant that drops the human reward model and uses verifiable, rule-based reward functions.",
            ),
            RemarkBlock(
                title="Why it matters",
                content=ItemizedList(
                    items=[
                        "No reward-model training step.",
                        "No preference dataset bottleneck.",
                        "Detail later — for now, take the punchline.",
                    ],
                ),
            ),
        ],
    )

    rlvr_math = SlideWithBlocks(
        title="RL from Verifiable Reward (RLVR)",
        subtitle="GRPO paper — math reasoning",
        blocks=[
            RemarkBlock(
                title="The reward",
                content="Just compare the model's response to the math result — match → reward, mismatch → no reward.",
            ),
        ],
    )

    rlvr_tbd = SlideWithList(
        title="RL from Verifiable Reward (RLVR)",
        subtitle="(more here later)",
        beamer_list=ItemizedList(
            items=[
                "Slot reserved for follow-up content from the screenplay.",
            ],
        ),
    )

    rlaif = SlideWithBlocks(
        title="RL from AI Feedback (RLAIF)",
        subtitle="Let an LLM grade the answers",
        blocks=[
            ExampleBlock(
                title="The trend",
                content="Use an LLM (often a stronger one) as the reward model instead of humans.",
            ),
            RemarkBlock(
                title="Where you'll see it",
                content=ItemizedList(
                    items=[
                        "Anthropic's Constitutional AI is the canonical example.",
                        "Far more scalable than human preference collection.",
                        "Already widely adopted in production pipelines.",
                    ],
                ),
            ),
        ],
    )

    return [section, rlvr_intro, rlvr_math, rlvr_tbd, rlaif]


def _scene05_why_bt():
    """Why I mention Bradley-Terry (a few times)."""
    section = SlideWithBlocks(
        title="Why I mention Bradley-Terry",
        subtitle="A few times — there's a reason",
        blocks=[],
    )

    bt_does_not_assume = SlideWithBlocks(
        title="Bradley-Terry does NOT presume",
        subtitle="Two assumptions it gracefully drops",
        blocks=[
            ExampleBlock(
                title="What BT skips",
                content=ItemizedList(
                    items=[
                        "Reasoning agents may give contradictory preferences — that's fine.",
                        "The reward model is biased toward the initial model's distribution by design.",
                    ],
                ),
            ),
            RemarkBlock(
                title="Net effect",
                content="Strictly more scalable than older preference-learning methods.",
            ),
        ],
    )

    not_transitive = SlideWithBlocks(
        title="It is not transitive",
        subtitle="A feature, not a bug",
        blocks=[
            ExampleBlock(
                title="The rock paper scissors",
                content=math(
                    r"P(Rock \succ Paper),\; P(Paper \succ Scissors),\; P(Scissors \succ Rock) \;\;\text{can all be} > \tfrac{1}{2}",
                    font_size=32,
                ),
            ),
            AlertBlock(
                title="BT and Elo cannot",
                content=math(
                    r"r(Rock) > r(Paper) > r(Scissors) > r(Rock) \;\;\Rightarrow\;\; \text{contradiction}",
                    font_size=32,
                ),
            ),
        ],
    )

    biased_to_dataset = SlideWithBlocks(
        title="Why \"biased to the dataset\"?",
        subtitle="Frequencies leak into the reward",
        blocks=[
            ExampleBlock(
                title="Intuition",
                content="If Rock appears more often than Scissors in the preference data, BT inflates Rock's reward over Scissors — no matter what.",
            ),
            RemarkBlock(
                title="Where it bites",
                content=ItemizedList(
                    items=[
                        "Dataset coverage shapes the reward landscape.",
                        "Re-weighting and active sampling can mitigate it.",
                    ],
                ),
            ),
        ],
    )

    return [section, bt_does_not_assume, not_transitive, biased_to_dataset]


def _scene06_nlhf_intro():
    """What to use then? — NLHF + lead-in to the policy-gradient animation."""
    section = SlideWithBlocks(
        title="What to use then?",
        subtitle="An alternative to Bradley-Terry",
        blocks=[],
    )

    nlhf_idea = SlideWithBlocks(
        title="Nash Learning From Human Feedback",
        subtitle="Replace BT with a binary preference classifier",
        blocks=[
            ExampleBlock(
                title="The setup",
                content=ItemizedList(
                    items=[
                        "Train a binary classifier: given two answers, which one wins?",
                        "Treat it as a two-player game.",
                        "Solve for a Nash equilibrium of that game.",
                    ],
                ),
            ),
            RemarkBlock(
                title="Why it dodges the BT pitfalls",
                content="No transitive-reward assumption, no implicit dataset-frequency bias.",
            ),
        ],
    )

    return [section, nlhf_idea]


def _scene06b_nlhf_results():
    """Post-animation result image for NLHF."""
    results = ImageSlide(
        title="NLHF — empirical results",
        subtitle="What the policy gradient buys you",
        image_name="results_nlhf.png",
    )
    return [results]


def _scene07_no_more_bt():
    """So no more Bradley-Terry, right?"""
    section = SlideWithBlocks(
        title="So no more Bradley-Terry, right?",
        subtitle="Hold on",
        blocks=[],
    )

    not_really = SlideWithBlocks(
        title="Not really",
        subtitle="BT still wins where the world is well-behaved",
        blocks=[
            ExampleBlock(
                title="When BT shines",
                content="For well-behaved problems (the kind RLVR can also solve), BT works perfectly and is cheap.",
            ),
        ],
    )

    return [section, not_really]


def _scene08_outro():
    """If you want to play with all that — libraries, harness, thesis ideas."""
    section = SlideWithBlocks(
        title="If you want to play with all that",
        subtitle="Some libs and tools",
        blocks=[],
    )

    libraries = SlideWithBlocks(
        title="Interesting libraries",
        subtitle="",
        blocks=[
            ExampleBlock(
                title="The usual suspects",
                content=ItemizedList(
                    items=[
                        "TRL — RL algorithms for LLMs.",
                        "PEFT — LoRA and other adapters.",
                        "Unsloth — easy training loop for full FT pipelines.",
                        "ART — adaptable training loop for RL pipelines.",
                    ],
                ),
            ),
        ],
    )

    harness = SlideWithBlocks(
        title="Harness",
        subtitle="",
        blocks=[
            RemarkBlock(
                title="Hermes agents",
                content="Claude-Code-like CLI that uses online RL to learn from your feedback. Runs in the cloud — no local compute.",
            ),
        ],
    )

    thesis_ideas = SlideWithList(
        title="Some thesis ideas",
        subtitle="",
        beamer_list=ItemizedList(
            items=[
                "Fine-tune DeepRacer via the new Gym interface (no real-world test).",
                "Test other PG algorithms without Bradley-Terry.",
                ItemizedList(
                    items=[
                        "Robotics task with a preference model instead of BT.",
                        "Non-deterministic policy + GRPO for the same task.",
                    ],
                ),
                "Fine-tune SLMs for an RLVR task (coding, web search, reasoning).",
                "Evaluate LoRA on other domains.",
                "Human-feedback time-to-talk model.",
            ],
        ),
    )

    return [section, libraries, harness, thesis_ideas]


# ─────────────────────────────────────────────────────────────────────────────
# Public Scene classes — render order matches the screenplay
# ─────────────────────────────────────────────────────────────────────────────

class FtV2_01_Recap(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=_scene01_recap_before_bt(), **kwargs)


class FtV2_02_RecapAfter(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=_scene02_recap_after_bt(), **kwargs)


class FtV2_03_Continuing(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=_scene03_continuing(), **kwargs)


class FtV2_04_FeedbackNoHumans(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=_scene04_feedback_no_humans(), **kwargs)


class FtV2_05_WhyBT(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=_scene05_why_bt(), **kwargs)


class FtV2_06_NLHFIntro(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=_scene06_nlhf_intro(), **kwargs)


class FtV2_NLHFResults(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=_scene06b_nlhf_results(), **kwargs)


class FtV2_07_NoMoreBT(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=_scene07_no_more_bt(), **kwargs)


class FtV2_08_Outro(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=_scene08_outro(), **kwargs)
