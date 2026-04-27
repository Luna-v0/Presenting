"""
LoRA — Low-Rank Adaptation.

Flow:
    1. Factorization : W + ΔW = W' with blocks, morph ΔW → BA, param savings
    2. Low rank      : rank(BA) ≤ r bottleneck + misconception correction
"""

from manim import *


# ── Palette (white background) ───────────────────────────────────────
BG        = WHITE
TEXT_C    = BLACK
NEUTRAL_C = DARK_GRAY
W_C       = "#1565C0"   # blue — frozen weights
DELTA_C   = "#C62828"   # red — full update matrix
B_C       = "#2E7D32"   # green — B matrix
A_C       = "#D84315"   # deep orange — A matrix
RANK_C    = "#F9A825"   # amber — rank / bottleneck


class LoRAExplainer(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.scene_factorization()
        self.scene_low_rank()

    # ─────────────────────────────────────────────────────────────────
    # 1. Full finetuning blocks → ΔW morphs into BA → param count
    # ─────────────────────────────────────────────────────────────────
    def scene_factorization(self):
        # Equation at top
        eq = MathTex(r"W'", r"=", r"W", r"+", r"\Delta W",
                     font_size=38, color=TEXT_C)
        eq[0].set_color(W_C)
        eq[2].set_color(W_C)
        eq[4].set_color(DELTA_C)
        eq.to_edge(UP, buff=0.6)
        self.play(Write(eq))

        # Full-rank blocks:  W + ΔW = W'
        w_blk = self._matrix_block(r"W", r"d \times k", 2.7, 3.0, W_C)
        plus = MathTex(r"+", font_size=48, color=TEXT_C)
        d_blk = self._matrix_block(r"\Delta W", r"d \times k", 2.7, 3.0, DELTA_C)
        equals = MathTex(r"=", font_size=48, color=TEXT_C)
        w2_blk = self._matrix_block(r"W'", r"d \times k", 2.7, 3.0, W_C)

        blocks = VGroup(w_blk, plus, d_blk, equals, w2_blk)\
            .arrange(RIGHT, buff=0.35).move_to(UP * 0.1)

        self.play(FadeIn(w_blk, shift=LEFT * 0.3))
        self.play(FadeIn(plus), FadeIn(d_blk, shift=RIGHT * 0.3))
        self.play(FadeIn(equals), FadeIn(w2_blk, shift=RIGHT * 0.3))

        full_params = MathTex(r"|\Delta W| = d \cdot k",
                              font_size=28, color=DELTA_C)
        full_params.next_to(blocks, DOWN, buff=0.7)
        self.play(Indicate(d_blk[0], color=DELTA_C, scale_factor=1.03),
                  FadeIn(full_params, shift=UP * 0.15))
        self.wait(1.5)

        # ── Morph equation: ΔW → BA ──
        eq_factored = MathTex(r"W'", r"=", r"W", r"+", r"B", r"A",
                              font_size=38, color=TEXT_C)
        eq_factored[0].set_color(W_C)
        eq_factored[2].set_color(W_C)
        eq_factored[4].set_color(B_C)
        eq_factored[5].set_color(A_C)
        eq_factored.to_edge(UP, buff=0.6)

        # Fade out the full-rank blocks + param label, morph the equation
        self.play(
            FadeOut(blocks), FadeOut(full_params),
            TransformMatchingTex(eq, eq_factored, transform_mismatches=True),
            run_time=1.8,
        )
        self.wait(0.4)

        # Frozen / learned annotations
        frozen = MathTex(r"\text{frozen}", font_size=20, color=W_C)
        frozen.next_to(eq_factored[2], DOWN, buff=0.25)
        learned = MathTex(r"\text{learned}", font_size=20, color=B_C)
        learned.next_to(VGroup(eq_factored[4], eq_factored[5]), DOWN, buff=0.25)
        self.play(FadeIn(frozen, shift=UP * 0.1), FadeIn(learned, shift=UP * 0.1))
        self.wait(0.5)

        # Factorized blocks:  ΔW = B × A
        d_blk2 = self._matrix_block(r"\Delta W", r"d \times k", 2.9, 3.0, DELTA_C)
        d_blk2.shift(LEFT * 4 + DOWN * 0.7)

        eq_sign = MathTex(r"=", font_size=44, color=TEXT_C)
        times = MathTex(r"\times", font_size=38, color=TEXT_C)
        b_blk = self._matrix_block(r"B", r"d \times r", 1.15, 3.0, B_C)
        a_blk = self._matrix_block(r"A", r"r \times k", 3.0, 1.15, A_C)

        VGroup(eq_sign, b_blk, times, a_blk)\
            .arrange(RIGHT, buff=0.35).shift(RIGHT * 1.4 + DOWN * 0.65)

        self.play(FadeIn(d_blk2, shift=LEFT * 0.25))
        self.play(FadeIn(eq_sign))
        self.play(TransformFromCopy(d_blk2[0], b_blk[0]), FadeIn(b_blk[1:]))
        self.play(FadeIn(times),
                  TransformFromCopy(d_blk2[0], a_blk[0]), FadeIn(a_blk[1:]))

        lora_params = MathTex(r"|B|+|A| = r\,(d+k)",
                              font_size=30, color=RANK_C)
        lora_params.next_to(VGroup(d_blk2, b_blk, a_blk), DOWN, buff=0.7)
        self.play(
            Indicate(b_blk[0], color=B_C),
            Indicate(a_blk[0], color=A_C),
            FadeIn(lora_params, shift=UP * 0.15),
        )
        self.wait(2.0)
        self._clear()

    # ─────────────────────────────────────────────────────────────────
    # 2. rank(BA) ≤ r — bottleneck + misconception
    # ─────────────────────────────────────────────────────────────────
    def scene_low_rank(self):
        rank_eq = MathTex(r"\mathrm{rank}(", r"B", r"A", r") \le", r"r",
                          font_size=44, color=TEXT_C)
        rank_eq[1].set_color(B_C)
        rank_eq[2].set_color(A_C)
        rank_eq[4].set_color(RANK_C)
        rank_eq.to_edge(UP, buff=0.7)
        self.play(Write(rank_eq))
        self.wait(0.5)

        # Bottleneck: [k] --A--> [r] --B--> [d]
        left = RoundedRectangle(
            corner_radius=0.12, width=2.8, height=2.0,
            stroke_color=A_C, stroke_width=3,
        ).set_fill(A_C, opacity=0.10)
        mid = RoundedRectangle(
            corner_radius=0.12, width=0.9, height=2.8,
            stroke_color=RANK_C, stroke_width=3,
        ).set_fill(RANK_C, opacity=0.14)
        right = RoundedRectangle(
            corner_radius=0.12, width=2.8, height=2.0,
            stroke_color=B_C, stroke_width=3,
        ).set_fill(B_C, opacity=0.10)

        flow = VGroup(left, mid, right).arrange(RIGHT, buff=1.0)\
            .move_to(DOWN * 0.1)

        a_lbl = MathTex(r"A", font_size=30, color=A_C).next_to(left, UP, buff=0.2)
        b_lbl = MathTex(r"B", font_size=30, color=B_C).next_to(right, UP, buff=0.2)
        r_lbl = MathTex(r"r", font_size=38, color=RANK_C).move_to(mid)
        k_lbl = MathTex(r"k", font_size=26, color=NEUTRAL_C).move_to(left)
        d_lbl = MathTex(r"d", font_size=26, color=NEUTRAL_C).move_to(right)

        arrow1 = Arrow(left.get_right(), mid.get_left(), buff=0.15,
                       color=NEUTRAL_C, stroke_width=3)
        arrow2 = Arrow(mid.get_right(), right.get_left(), buff=0.15,
                       color=NEUTRAL_C, stroke_width=3)

        self.play(LaggedStart(FadeIn(left), FadeIn(mid), FadeIn(right),
                              lag_ratio=0.18))
        self.play(FadeIn(a_lbl), FadeIn(b_lbl), FadeIn(r_lbl),
                  FadeIn(k_lbl), FadeIn(d_lbl))
        self.play(GrowArrow(arrow1), GrowArrow(arrow2))
        self.wait(1.0)

        # Fade bottleneck, show misconception
        self.play(FadeOut(flow), FadeOut(a_lbl), FadeOut(b_lbl),
                  FadeOut(r_lbl), FadeOut(k_lbl), FadeOut(d_lbl),
                  FadeOut(arrow1), FadeOut(arrow2))

        # Wrong: rank(W') ≤ r
        wrong = MathTex(r"\mathrm{rank}(W') \le r",
                        font_size=36, color=DELTA_C)
        wrong.move_to(ORIGIN).shift(UP * 0.3)
        cross = Cross(wrong, color=DELTA_C, stroke_width=4)
        self.play(FadeIn(wrong))
        self.play(Create(cross))
        self.wait(0.5)

        # Right: rank(ΔW) = rank(BA) ≤ r
        correct = MathTex(
            r"\mathrm{rank}(", r"\Delta W", r") = \mathrm{rank}(",
            r"B", r"A", r") \le r",
            font_size=36, color=TEXT_C,
        )
        correct[1].set_color(DELTA_C)
        correct[3].set_color(B_C)
        correct[4].set_color(A_C)
        correct.next_to(wrong, DOWN, buff=0.8)
        self.play(FadeIn(correct, shift=UP * 0.2))
        self.wait(3.0)

    # ─────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────
    def _matrix_block(self, name: str, dims: str,
                      w: float, h: float, color: str) -> VGroup:
        box = RoundedRectangle(
            corner_radius=0.14, width=w, height=h,
            stroke_color=color, stroke_width=3,
        ).set_fill(color, opacity=0.10)
        name_t = MathTex(name, font_size=34, color=TEXT_C).move_to(box)
        if name_t.width > box.width * 0.7:
            name_t.scale_to_fit_width(box.width * 0.7)
        dims_t = MathTex(dims, font_size=24, color=NEUTRAL_C)\
            .next_to(box, DOWN, buff=0.22)
        return VGroup(box, name_t, dims_t)

    def _clear(self):
        self.play(*[FadeOut(m) for m in self.mobjects])
