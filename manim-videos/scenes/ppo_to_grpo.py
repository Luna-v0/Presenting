"""
PPO to GRPO — minimal animation on a white background.

Flow:
    1. PPO pipeline   : policy -> response -> critic + reward -> A = R - V
    2. GRPO pipeline  : policy -> {y_1..y_G} -> mu, sigma -> A_hat = (r - mu)/sigma
    3. Loss morph     : J_PPO morphs in-place into J_GRPO — only the group
                        sum and the advantage actually change.
"""

from manim import *
import numpy as np


# ── Palette (tuned for white background) ─────────────────────────────
BG        = WHITE
TEXT_C    = BLACK
NEUTRAL_C = DARK_GRAY
PPO_C     = BLUE_E
GRPO_C    = "#1B5E20"   # deep green
CRITIC_C  = "#C62828"   # deep red
REWARD_C  = "#2E7D32"   # deep green (same hue family as GRPO)
NEG_C     = "#C62828"
MID_C     = "#F9A825"   # amber — middle-of-pack
ADV_C     = "#D84315"   # deep orange — advantage accents
STAT_C    = "#00695C"   # dark teal — mu, sigma
HL_C      = "#F9A825"   # highlight boxes for diff callouts
DIFF_C    = "#FF0000"   # blue — highlight differing parts in comparison


class PPOToGRPO(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.scene_ppo_pipeline()
        self.scene_grpo_pipeline()
        self.scene_loss_morph()

    # ─────────────────────────────────────────────────────────────────
    # 1. PPO pipeline
    # ─────────────────────────────────────────────────────────────────
    def scene_ppo_pipeline(self):
        title = Text("PPO", font_size=36, color=PPO_C, weight=BOLD).to_edge(UP, buff=0.6)
        self.play(FadeIn(title))

        policy = self._policy_node(r"\pi", PPO_C).shift(LEFT * 4.5 + UP * 0.3)
        resp   = self._response_box(r"y").shift(LEFT * 1.8 + UP * 0.3)
        a1     = self._arrow(policy.get_right(), resp.get_left(), stroke_width=2)
        self.play(FadeIn(policy), GrowArrow(a1), FadeIn(resp))

        critic = VGroup(
            Text("Critic", font_size=14, color=CRITIC_C),
            MathTex(r"V(s)=0.6", font_size=22, color=CRITIC_C),
        ).arrange(DOWN, buff=0.06).shift(RIGHT * 0.8 + UP * 1.3)

        reward = VGroup(
            Text("Reward", font_size=14, color=REWARD_C),
            MathTex(r"R=0.8", font_size=22, color=REWARD_C),
        ).arrange(DOWN, buff=0.06).shift(RIGHT * 0.8 + DOWN * 0.7)

        a2 = self._arrow(resp.get_right(), critic.get_left())
        a3 = self._arrow(resp.get_right(), reward.get_left())
        self.play(GrowArrow(a2), GrowArrow(a3), FadeIn(critic), FadeIn(reward))

        adv = MathTex(r"A", r"=", r"0.8", r"-", r"0.6", r"=", r"0.2",
                      font_size=32, color=TEXT_C)
        adv[0].set_color(ADV_C)
        adv[2].set_color(REWARD_C)
        adv[4].set_color(CRITIC_C)
        adv[6].set_color(ADV_C)
        adv.shift(RIGHT * 4 + UP * 0.3)

        a4 = self._arrow(VGroup(critic, reward).get_right(), adv.get_left(),
                         stroke_width=1.5)
        self.play(GrowArrow(a4), Write(adv))
        self.wait(3.0)
        self._clear()

    # ─────────────────────────────────────────────────────────────────
    # 2. GRPO pipeline — sampling + group-relative advantage
    # ─────────────────────────────────────────────────────────────────
    def scene_grpo_pipeline(self):
        title = Text("GRPO", font_size=36, color=GRPO_C, weight=BOLD).to_edge(UP, buff=0.6)
        self.play(FadeIn(title))

        policy = self._policy_node(r"\pi", GRPO_C).shift(LEFT * 5.5)

        data = [(r"y_1", 0.8, REWARD_C),
                (r"y_2", 0.5, MID_C),
                (r"y_3", 0.2, NEG_C),
                (r"y_4", 0.9, REWARD_C),
                (r"y_5", 0.1, NEG_C)]

        rows = VGroup()
        for lab, r, col in data:
            row = VGroup(
                MathTex(lab, font_size=22, color=TEXT_C),
                MathTex(r"\rightarrow", font_size=20, color=NEUTRAL_C),
                MathTex(f"r={r}", font_size=22, color=col),
            ).arrange(RIGHT, buff=0.12)
            rows.add(row)
        rows.arrange(DOWN, buff=0.18, aligned_edge=LEFT).shift(LEFT * 2.3)

        brace = Brace(rows, LEFT, buff=0.12, color=NEUTRAL_C)
        a_pol = self._arrow(policy.get_right(), brace.get_left(), stroke_width=2)

        self.play(FadeIn(policy), GrowArrow(a_pol))
        self.play(FadeIn(brace), FadeIn(rows))
        self.wait(1.0)

        rewards = [0.8, 0.5, 0.2, 0.9, 0.1]
        mu  = float(np.mean(rewards))
        sig = float(np.std(rewards))

        stats = VGroup(
            MathTex(r"\mu",    r"=", f"{mu:.2f}",  font_size=28, color=TEXT_C),
            MathTex(r"\sigma", r"=", f"{sig:.2f}", font_size=28, color=TEXT_C),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT).shift(RIGHT * 1.5 + UP * 1.2)
        stats[0][0].set_color(STAT_C)
        stats[1][0].set_color(STAT_C)
        self.play(Write(stats))

        formula = MathTex(r"\hat{A}_i", r"=", r"\frac{r_i - \mu}{\sigma}",
                          font_size=36, color=ADV_C).shift(RIGHT * 1.5 + DOWN * 0.2)
        self.play(Write(formula))
        self.wait(1.5)

        callout = Text("advantage is normalized by the group mean — no critic",
                       font_size=22, color=STAT_C).to_edge(DOWN, buff=0.9)
        self.play(FadeIn(callout, shift=UP * 0.2))
        self.wait(3.0)
        self._clear()

    # ─────────────────────────────────────────────────────────────────
    # 3. J_PPO morphs into J_GRPO
    #
    # The only *real* differences are (a) the group average  1/G Σ_i
    # and  (b) the advantage  A_t  →  Â_{i,t}.  Everything else
    # (ratio, clip) matches and stays still during the morph.
    # ─────────────────────────────────────────────────────────────────
    def scene_loss_morph(self):
        ppo  = self._ppo_loss_tex()
        grpo = self._grpo_loss_tex()

        # Scale both to the same visible width so the unchanged parts
        # land on top of their twins during TransformMatchingTex.
        ppo.scale_to_fit_width(12.5).move_to(ORIGIN)
        grpo.scale_to_fit_width(13.2).move_to(ORIGIN)

        self.play(Write(ppo), run_time=2.2)
        self.wait(1.6)

        self.play(
            TransformMatchingTex(ppo, grpo, transform_mismatches=True),
            run_time=2.6,
        )
        self.wait(3.0)

        # ── Show PPO underneath GRPO for comparison ──
        self.play(grpo.animate.shift(UP * 1.2))

        ppo_compare = self._ppo_loss_tex()
        ppo_compare.scale_to_fit_width(12.5).next_to(grpo, DOWN, buff=1.4)

        # Pre-color the differing parts blue before fading in
        _PPO_DIFF = [1, 3, 6, 8, 10, 12, 14, 15]   # PPO-only parts
        for i in _PPO_DIFF:
            ppo_compare[i].set_color(DIFF_C)

        grpo_label = Text("GRPO", font_size=22, color=GRPO_C, weight=BOLD)
        grpo_label.next_to(grpo, UP, buff=0.15, aligned_edge=LEFT)
        ppo_label = Text("PPO", font_size=22, color=PPO_C, weight=BOLD)
        ppo_label.next_to(ppo_compare, UP, buff=0.15, aligned_edge=LEFT)

        # Animate GRPO diff parts to blue while fading in PPO
        _GRPO_DIFF = [1, 3, 5, 7, 9, 11, 13, 15, 16, 17]  # GRPO-only parts (incl KL)
        self.play(
            FadeIn(grpo_label, shift=DOWN * 0.1),
            FadeIn(ppo_compare, shift=UP * 0.3),
            FadeIn(ppo_label, shift=DOWN * 0.1),
            *[grpo[i].animate.set_color(DIFF_C) for i in _GRPO_DIFF],
        )
        self.wait(3.5)

    # ── Loss builders ────────────────────────────────────────────────
    #
    # PPO and GRPO are built from chunk lists whose common substrings
    # match exactly.  TransformMatchingTex keeps matched submobjects
    # put and pairs the mismatches so the morph reads as "same shape,
    # with these two pieces swapped out".
    #
    # Chunks that differ (and what they become):
    #     _{\mathrm{PPO}}     →  _{\mathrm{GRPO}}
    #     o                   →  \{o_i\}_{i=1}^{G}
    #     |o|                 →  |o_i|
    #     r_t                 →  r_{i,t}
    #     A_t                 →  \hat{A}_{i,t}
    #   (+ new)               →  \tfrac{1}{G}\sum_{i=1}^{G}
    # ─────────────────────────────────────────────────────────────────

    # Index lookups into the GRPO MathTex for post-morph highlights.
    _GRPO_IDX_GROUP_SUM = 5
    _GRPO_IDX_ADV_1     = 11
    _GRPO_IDX_ADV_2     = 15
    _GRPO_IDX_KL        = 17

    def _ppo_loss_tex(self) -> MathTex:
        return MathTex(
            r"\mathcal{J}",                             # 0
            r"_{\mathrm{PPO}}",                         # 1
            r"(\theta) = \mathbb{E}\!\big[q,\,",        # 2
            r"o",                                       # 3
            r"\sim\pi_{\theta_{old}}\big]\;",           # 4
            # (no group sum here — GRPO will grow one in)
            r"\tfrac{1}{",                              # 5
            r"|o|",                                     # 6
            r"}\sum_t \min\!\big(",                     # 7
            r"r_t",                                     # 8
            r"(\theta)\,",                              # 9
            r"A_t",                                     # 10
            r",\;\mathrm{clip}(",                       # 11
            r"r_t",                                     # 12
            r",1\!\pm\!\varepsilon)\,",                 # 13
            r"A_t",                                     # 14
            r"\big)",                                    # 15
            font_size=30, color=TEXT_C,
        )

    def _grpo_loss_tex(self) -> MathTex:
        return MathTex(
            r"\mathcal{J}",                             # 0
            r"_{\mathrm{GRPO}}",                        # 1
            r"(\theta) = \mathbb{E}\!\big[q,\,",        # 2
            r"\{o_i\}_{i=1}^{G}",                       # 3
            r"\sim\pi_{\theta_{old}}\big]\;",           # 4
            r"\tfrac{1}{G}\sum_{i=1}^{G}",              # 5  ← group sum
            r"\tfrac{1}{",                              # 6
            r"|o_i|",                                   # 7
            r"}\sum_t \min\!\big(",                     # 8
            r"r_{i,t}",                                 # 9
            r"(\theta)\,",                              # 10
            r"\hat{A}_{i,t}",                           # 11 ← advantage
            r",\;\mathrm{clip}(",                       # 12
            r"r_{i,t}",                                 # 13
            r",1\!\pm\!\varepsilon)\,",                 # 14
            r"\hat{A}_{i,t}",                           # 15 ← advantage
            r"\big)",                                    # 16
            r"\;-\;\beta\,\mathbb{D}_{KL}"              # 17  ← KL (GRPO only)
            r"\!\big[\pi_\theta\|\pi_{ref}\big]",
            font_size=30, color=TEXT_C,
        )

    # ─────────────────────────────────────────────────────────────────
    # Small helpers
    # ─────────────────────────────────────────────────────────────────
    def _policy_node(self, tex: str, color) -> VGroup:
        c = Circle(radius=0.4, color=color, fill_opacity=0.12).set_stroke(color)
        t = MathTex(tex, font_size=34, color=color).move_to(c)
        return VGroup(c, t)

    def _response_box(self, tex: str) -> VGroup:
        box = RoundedRectangle(corner_radius=0.1, width=1.4, height=0.45,
                               color=NEUTRAL_C, stroke_width=1.2)
        t = MathTex(tex, font_size=26, color=TEXT_C).move_to(box)
        return VGroup(box, t)

    def _arrow(self, start, end, stroke_width: float = 1.5) -> Arrow:
        return Arrow(start, end, buff=0.1, color=NEUTRAL_C, stroke_width=stroke_width)

    def _clear(self):
        self.play(*[FadeOut(m) for m in self.mobjects])
