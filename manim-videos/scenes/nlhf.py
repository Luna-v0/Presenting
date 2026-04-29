"""
NLHF — Natural Language Human Feedback.

Flow:
    1. Policy gradient with A highlighted
    2. Standard advantage A = Σγ^τ R_τ − b(S_t), baseline b highlighted
    3. NLHF advantage   A = P(y≻y'|x) − 1/2 − τ log(π/μ)
    4. Connect b ↔ 1/2
    5. Substitute into the policy gradient → unified formula
"""

from manim import *
from manim_slides import Slide


# ── Palette (white background) ───────────────────────────────────────
BG        = WHITE
TEXT_C    = BLACK
NEUTRAL_C = DARK_GRAY
ADV_C     = "#D84315"   # deep orange — advantage
BASE_C    = "#6A1B9A"   # purple — baseline b / ½
PREF_C    = "#1565C0"   # blue — preference probability
KL_C      = "#00695C"   # teal — KL penalty


class NLHF(Slide):
    def construct(self):
        self.camera.background_color = BG
        self.scene_nlhf()

    def scene_nlhf(self):
        # ── 1. Policy gradient — highlight A ─────────────────────────
        pg = MathTex(
            r"\nabla_\theta J(\pi_\theta) = "
            r"\mathbb{E}_{\tau \sim \pi_\theta}",                       # 0
            r"\left[\sum_{t=0}^T "
            r"\nabla_\theta \log \pi_\theta(a_t|s_t)\;",               # 1
            r"A^{\pi_\theta}(s_t, a_t)",                                # 2
            r"\right]",                                                 # 3
            font_size=30, color=TEXT_C,
        )
        pg[2].set_color(ADV_C)
        pg.to_edge(UP, buff=0.7)

        self.play(Write(pg), run_time=2.0)
        box_a = SurroundingRectangle(pg[2], color=ADV_C,
                                     buff=0.06, stroke_width=2.5)
        self.play(Create(box_a))
        self.wait(4.0)
        self.next_slide()

        # ── 2. Standard advantage (same orange), baseline b purple ───
        std = MathTex(
            r"A",                                                       # 0
            r"= \sum_{\tau=t}^{T} \gamma^\tau R_\tau",                  # 1
            r"-",                                                       # 2
            r"b(S_t)",                                                  # 3
            font_size=34, color=ADV_C,
        )
        std[3].set_color(BASE_C)
        std.next_to(pg, DOWN, buff=0.9)

        self.play(FadeOut(box_a), Write(std))
        box_b = SurroundingRectangle(std[3], color=BASE_C,
                                     buff=0.06, stroke_width=2.5)
        self.play(Create(box_b))
        self.wait(4.0)
        self.next_slide()

        # ── 3. NLHF advantage ───────────────────────────────────────
        nlhf = MathTex(
            r"A",                                                       # 0
            r"= \mathcal{P}(y \succ y'|x)",                            # 1
            r"-",                                                       # 2
            r"\tfrac{1}{2}",                                            # 3
            r"- \tau \log \frac{\pi_\theta(y|x)}{\mu(y|x)}",           # 4
            font_size=34, color=ADV_C,
        )
        nlhf[3].set_color(BASE_C)
        nlhf.next_to(std, DOWN, buff=0.9)

        self.play(FadeOut(box_b), Write(nlhf))
        self.wait(4.0)
        self.next_slide()

        # ── 4. Connect  b(S_t)  ↔  1/2 ──────────────────────────────
        box_b2   = SurroundingRectangle(std[3],  color=BASE_C,
                                        buff=0.06, stroke_width=2)
        box_half = SurroundingRectangle(nlhf[3], color=BASE_C,
                                        buff=0.06, stroke_width=2)
        link = Arrow(box_b2.get_bottom(), box_half.get_top(),
                     buff=0.08, color=BASE_C, stroke_width=2)

        self.play(Create(box_b2), Create(box_half), GrowArrow(link))
        self.wait(4.0)
        self.next_slide()

        # ── 5. Merge into unified policy gradient ────────────────────
        self.play(
            FadeOut(std), FadeOut(nlhf),
            FadeOut(box_b2), FadeOut(box_half), FadeOut(link),
        )

        unified = MathTex(
            r"\nabla_\theta J(\pi_\theta) = "
            r"\mathbb{E}_{\tau \sim \pi_\theta}",                       # 0
            r"\left[\sum_{t=0}^T "
            r"\nabla_\theta \log \pi_\theta(a_t|s_t)\;",               # 1
            r"\Big(",                                                   # 2
            r"\mathcal{P}(y \succ y'|x)",                               # 3
            r"- \tfrac{1}{2}",                                          # 4
            r"- \tau \log \tfrac{\pi_\theta(y|x)}{\mu(y|x)}",          # 5
            r"\Big)",                                                   # 6
            r"\right]",                                                 # 7
            font_size=26, color=TEXT_C,
        )
        unified[3].set_color(PREF_C)
        unified[4].set_color(BASE_C)
        unified[5].set_color(KL_C)
        unified.scale_to_fit_width(13).move_to(ORIGIN)

        self.play(
            TransformMatchingTex(pg, unified, transform_mismatches=True),
            run_time=2.8,
        )
        self.wait(1.5)
        self.next_slide()
