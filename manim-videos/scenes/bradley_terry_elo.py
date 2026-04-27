"""
Bradley-Terry → Softmax → Elo
Formula morphs + numeric example + Elo ranked list.
"""

from manim import *
import numpy as np


# ── Palette (white background) ───────────────────────────────────────
BG        = WHITE
TEXT_C    = BLACK
NEUTRAL_C = DARK_GRAY
BT_C      = "#1565C0"   # blue — BT formula accent
EXP_C     = "#2E7D32"   # green — exponential form
SIG_C     = "#D84315"   # deep orange — sigmoid
SOFT_C    = "#F9A825"   # amber — softmax highlight
MODEL_A_C = "#1565C0"
MODEL_B_C = "#C62828"
ELO_C     = "#6A1B9A"   # purple — Elo


class BradleyTerryToElo(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.scene_bt_formula()
        self.scene_numeric_example()
        self.scene_elo_leaderboard()

    # ─────────────────────────────────────────────────────────────────
    # 1. Bradley-Terry core → exponential form → sigmoid
    # ─────────────────────────────────────────────────────────────────
    def scene_bt_formula(self):
        # Start with the general softmax
        softmax = MathTex(
            r"Softmax(",                                           # 0
            r"i",                                            # 1 → i ≻ j
            r") =",                                         # 2
            r"\frac{e^{",                                    # 3
            r"s_i",                                          # 4 → reward sum
            r"}}{",                                          # 5
            r"\displaystyle\sum_{k=1}^{K} e^{s_k}",         # 6 → pairwise denom
            r"}",                                            # 7
            font_size=44, color=TEXT_C,
        )
        softmax[1].set_color(SOFT_C)
        softmax[6].set_color(SOFT_C)
        self.play(Write(softmax))
        self.wait(1.5)

        # Morph softmax → BT with reward sums
        bt = MathTex(
            r"P(",                                                          # 0
            r"i \succ j",                                                   # 1
            r") =",                                                         # 2
            r"\frac{e^{",                                                   # 3
            r"\sum_t r(s^i_t,a^i_t)",                                       # 4
            r"}}{",                                                         # 5
            r"e^{\sum_t r(s^i_t,a^i_t)} + e^{\sum_t r(s^j_t,a^j_t)}",      # 6
            r"}",                                                           # 7
            font_size=44, color=TEXT_C,
        )
        bt[1].set_color(BT_C)

        self.play(
            TransformMatchingTex(softmax, bt, transform_mismatches=True),
            run_time=2.5,
        )
        self.wait(1.5)

        # Reparametrize p_i = e^{s_i}
        sub = MathTex(r"p_i = e^{s_i}", font_size=26, color=NEUTRAL_C)
        sub.next_to(bt, DOWN, buff=0.6)
        self.play(FadeIn(sub, shift=UP * 0.15))
        self.wait(0.8)
        self._clear()

    # ─────────────────────────────────────────────────────────────────
    # 2. Numeric example: two models → P(A ≻ B)
    # ─────────────────────────────────────────────────────────────────
    def scene_numeric_example(self):
        ref = MathTex(
            r"P(i \succ j) = \frac{e^{s_i}}{e^{s_i} + e^{s_j}}",
            font_size=30, color=NEUTRAL_C,
        ).to_edge(UP, buff=0.5)
        self.play(FadeIn(ref))

        model_a = self._model_node("A", MODEL_A_C).shift(LEFT * 2.5)
        model_b = self._model_node("B", MODEL_B_C).shift(RIGHT * 2.5)
        vs = MathTex(r"\text{vs}", font_size=24, color=NEUTRAL_C)
        scores = VGroup(
            MathTex(r"s_A = 2.0", font_size=24, color=MODEL_A_C)
                .next_to(model_a, DOWN, buff=0.2),
            MathTex(r"s_B = 1.0", font_size=24, color=MODEL_B_C)
                .next_to(model_b, DOWN, buff=0.2),
        )
        self.play(FadeIn(model_a), FadeIn(model_b), FadeIn(vs), FadeIn(scores))
        self.wait(0.5)

        s_a, s_b = 2.0, 1.0
        exp_a, exp_b = np.exp(s_a), np.exp(s_b)
        prob = exp_a / (exp_a + exp_b)

        comp = VGroup(
            MathTex(r"e^{2.0}", r"=", f"{exp_a:.2f}", font_size=26, color=TEXT_C),
            MathTex(r"e^{1.0}", r"=", f"{exp_b:.2f}", font_size=26, color=TEXT_C),
            MathTex(
                r"P(A \succ B)", r"=",
                r"\frac{" + f"{exp_a:.2f}" + r"}{" +
                f"{exp_a:.2f}" + r"+" + f"{exp_b:.2f}" + r"}",
                r"=", f"{prob:.2f}",
                font_size=26, color=TEXT_C,
            ),
        )
        comp[0][0].set_color(MODEL_A_C)
        comp[0][2].set_color(MODEL_A_C)
        comp[1][0].set_color(MODEL_B_C)
        comp[1][2].set_color(MODEL_B_C)
        comp[2][0].set_color(BT_C)
        comp[2][-1].set_color(SOFT_C)
        comp.arrange(DOWN, buff=0.25, aligned_edge=LEFT).shift(DOWN * 1.6)

        for c in comp:
            self.play(Write(c), run_time=0.7)
            self.wait(0.4)
        self.wait(2)
        self._clear()

    # BT and softmax tex — matched substrings stay still during morph.
    # Mismatches (denominator, LHS subscript) shape-transform.
    def _bt_tex(self) -> MathTex:
        return MathTex(
            r"P(",                             # 0
            r"i \succ j",                      # 1 → morphs to "i"
            r") =",                            # 2
            r"\frac{e^{s_i}}{",                # 3
            r"e^{s_i} + e^{s_j}",             # 4 → morphs to Σ
            r"}",                              # 5
            font_size=44, color=TEXT_C,
        )

    def _softmax_tex(self) -> MathTex:
        return MathTex(
            r"P(",                                            # 0
            r"i",                                             # 1
            r") =",                                           # 2
            r"\frac{e^{s_i}}{",                              # 3
            r"\displaystyle\sum_{k=1}^{K} e^{s_k}",         # 4
            r"}",                                             # 5
            font_size=44, color=TEXT_C,
        )

    # ─────────────────────────────────────────────────────────────────
    # 3. BT ∝ Elo — chess leaderboard
    # ─────────────────────────────────────────────────────────────────
    def scene_elo_leaderboard(self):
        # Connection statement instead of the full Elo formula
        bt_ref = MathTex(
            r"P(i \succ j) = \frac{e^{s_i}}{e^{s_i}+e^{s_j}}",
            font_size=30, color=BT_C,
        ).to_edge(UP, buff=0.55)

        prop = MathTex(
            r"\propto \;\text{Elo rating system}",
            font_size=28, color=ELO_C,
        ).next_to(bt_ref, RIGHT, buff=0.25)

        self.play(FadeIn(bt_ref), FadeIn(prop, shift=LEFT * 0.15))
        self.wait(1.5)

        # Chess leaderboard
        players_data = [
            ("Magnus Carlsen",    2830, "#1565C0"),
            ("Fabiano Caruana",   2786, "#6A1B9A"),
            ("Hikaru Nakamura",   2760, "#00695C"),
            ("Ding Liren",        2728, "#D84315"),
            ("Ian Nepomniachtchi", 2693, "#C62828"),
        ]
        rows = VGroup()
        for rank, (name, elo, col) in enumerate(players_data, 1):
            rank_t = MathTex(f"{rank}.", font_size=26, color=NEUTRAL_C)
            name_t = Text(name, font_size=20, color=col, weight=BOLD)
            bar = Rectangle(
                width=elo / 800, height=0.28,
                color=col, fill_color=col, fill_opacity=0.45,
                stroke_width=1.2,
            )
            elo_t = MathTex(str(elo), font_size=22, color=col)

            if name_t.width > 2.2:
                name_t.scale(2.2 / name_t.width)
            rank_t.shift(LEFT * 4)
            name_t.next_to(rank_t, RIGHT, buff=0.2)
            bar.next_to(name_t, RIGHT, buff=0.25)
            bar.align_to(name_t, LEFT).shift(RIGHT * 2.8)
            elo_t.next_to(bar, RIGHT, buff=0.15)
            rows.add(VGroup(rank_t, name_t, bar, elo_t))

        rows.arrange(DOWN, buff=0.25, aligned_edge=LEFT).shift(DOWN * 0.3)

        for row in rows:
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait(3)

    # ─────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────
    def _model_node(self, label: str, color) -> VGroup:
        c = Circle(radius=0.35, color=color, fill_opacity=0.12).set_stroke(color)
        t = MathTex(label, font_size=28, color=color).move_to(c)
        return VGroup(c, t)

    def _clear(self):
        self.play(*[FadeOut(m) for m in self.mobjects])
