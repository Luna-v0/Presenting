"""Policy Gradient — single animated derivation scene.

One continuous scene with two phases:

  Phase 1 — present each of the 5 tricks at center stage (color-coded),
            then dock to a stack on the right. Lineage tricks fade as
            their work is folded into a later trick:
                Trick 3 absorbs Trick 1   → Trick 1 discarded on dock
                Trick 5 absorbs Tricks 3+4 → Tricks 3, 4 discarded on dock

  Phase 2 — main derivation morphs in place on the left. The relevant
            card pulses when applied, then is discarded:
                Step 3 uses Trick 2 → Trick 2 discarded after
                Step 5 uses Trick 5 → Trick 5 discarded after

By the end, the side is clean and only the final boxed result remains.

Render / present:
    uv run manim-slides render scenes/policy_gradient.py PolicyGradientDerivation -ql
    uv run manim-slides present PolicyGradientDerivation
    # or as plain video:
    uv run manim scenes/policy_gradient.py PolicyGradientDerivation -ql
"""

from __future__ import annotations

from manim import (
    BLACK,
    BLUE,
    BOLD,
    DARK_GRAY,
    DOWN,
    LEFT,
    NORMAL,
    ORIGIN,
    RIGHT,
    UP,
    WHITE,
    Create,
    FadeIn,
    FadeOut,
    Indicate,
    Line,
    MathTex,
    ReplacementTransform,
    SurroundingRectangle,
    Text,
    TransformFromCopy,
    TransformMatchingTex,
    VGroup,
    Write,
    config,
    smooth,
)
from manim_slides import Slide


# ── Palette ──────────────────────────────────────────────────────────────────
BODY_GRAY  = DARK_GRAY
ACCENT     = BLUE
ORANGE_C   = "#FB8C00"
NOTE_RED   = "#C62828"

TRICK1_C = "#00897B"   # teal   — Probability of a Trajectory
TRICK2_C = "#1565C0"   # blue   — Log-Derivative Trick
TRICK3_C = "#6A1B9A"   # purple — Log-Prob of a Trajectory
TRICK4_C = "#C62828"   # red    — Env Gradients = 0
TRICK5_C = "#1B5E20"   # green  — Grad-Log-Prob

# ── Pacing (seconds) ─────────────────────────────────────────────────────────
PAUSE   = 3.0
SHORT   = 1.2
MORPH   = 1.5         # equation morphs in the main derivation
DOCK_RT = 1.8         # docking + repack — long enough to read

# ── Side stack geometry ──────────────────────────────────────────────────────
DOCK_X     = 4.7
DOCK_TOP_Y = 2.4
DOCK_GAP   = 1.55


def dock_pos(idx: int):
    return RIGHT * DOCK_X + UP * (DOCK_TOP_Y - idx * DOCK_GAP)


# ── Tiny constructor helpers ─────────────────────────────────────────────────
def text(s: str, font_size: int = 30, weight: str = NORMAL, color=BODY_GRAY) -> Text:
    return Text(s, font="TeX Gyre Termes", color=color, font_size=font_size, weight=weight)


def math(tex: str, font_size: int = 36, color=BLACK) -> MathTex:
    return MathTex(tex, color=color, font_size=font_size)


def make_card(label: str, formula: str, color,
              label_fs: int = 16, eq_fs: int = 15):
    """Compact reference card. Returns (group, title, eq, box) for animation."""
    title = text(label, font_size=label_fs, color=color, weight=BOLD)
    eq = MathTex(formula, color=color, font_size=eq_fs)
    content = VGroup(title, eq).arrange(DOWN, buff=0.10)
    box = SurroundingRectangle(content, color=color, buff=0.18,
                                corner_radius=0.10, stroke_width=2)
    return VGroup(content, box), title, eq, box


class PolicyGradientDerivation(Slide):
    def construct(self):
        config.background_color = WHITE
        self.camera.background_color = WHITE

        STAGE = LEFT * 1.8   # presentation center for each trick

        # ═══════════════════════════════════════════════════════════════════
        # TRICK 1 — Probability of a Trajectory  (TEAL)
        # ═══════════════════════════════════════════════════════════════════
        t1_title = text("Trick 1 — Probability of a Trajectory",
                        font_size=38, color=TRICK1_C, weight=BOLD)
        t1_intro = text("Probability of trajectory τ under π_θ:", font_size=26)
        t1_eq = math(
            r"P(\tau|\theta) \;=\; \rho_{0}(s_0)\,\prod_{t=0}^{T} "
            r"P(s_{t+1}|s_t, a_t)\,\pi_{\theta}(a_t|s_t)",
            font_size=38, color=TRICK1_C,
        )
        VGroup(t1_title, t1_intro, t1_eq).arrange(DOWN, buff=0.5).move_to(STAGE)

        self.play(FadeIn(t1_title, shift=UP * 0.2), run_time=1.0)
        self.play(FadeIn(t1_intro), run_time=0.8)
        self.play(Write(t1_eq), run_time=2.0)
        self.wait(PAUSE)

        # ── Dock at idx=0 ────────────────────────────────────────────────
        c1, c1_t, c1_e, c1_b = make_card(
            "Trick 1 · Probability of Trajectory",
            r"P(\tau|\theta) = \rho_{0}(s_0)\,\prod_{t} P(s_{t+1}|s_t,a_t)\,\pi_{\theta}(a_t|s_t)",
            TRICK1_C, eq_fs=12,
        )
        c1.move_to(dock_pos(0))
        self.play(
            FadeOut(t1_intro, shift=DOWN * 0.15),
            ReplacementTransform(t1_title, c1_t),
            ReplacementTransform(t1_eq, c1_e),
            Create(c1_b),
            run_time=DOCK_RT, rate_func=smooth,
        )
        self.wait(SHORT)

        # ═══════════════════════════════════════════════════════════════════
        # TRICK 2 — Log-Derivative Trick  (BLUE)
        # ═══════════════════════════════════════════════════════════════════
        t2_title = text("Trick 2 — The Log-Derivative Trick",
                        font_size=38, color=TRICK2_C, weight=BOLD)
        t2_a = math(r"\frac{d}{dx}\log(x) \;=\; \frac{1}{x}",
                    font_size=42, color=TRICK2_C)
        t2_arr1 = math(r"\Downarrow", font_size=36, color=BODY_GRAY)
        t2_b = math(r"\frac{d}{dx}\,f(x) \;=\; f(x)\,\frac{d}{dx}\log f(x)",
                    font_size=42, color=TRICK2_C)
        t2_arr2 = math(r"\Downarrow", font_size=36, color=BODY_GRAY)
        t2_c = math(
            r"\nabla_{\theta} P(\tau|\theta) \;=\; "
            r"P(\tau|\theta)\,\nabla_{\theta}\log P(\tau|\theta)",
            font_size=40, color=TRICK2_C,
        )
        VGroup(t2_title, t2_a, t2_arr1, t2_b, t2_arr2, t2_c) \
            .arrange(DOWN, buff=0.30).move_to(STAGE)

        self.play(FadeIn(t2_title, shift=UP * 0.2), run_time=1.0)
        self.play(Write(t2_a), run_time=1.3)
        self.wait(SHORT)
        self.play(FadeIn(t2_arr1), Write(t2_b), run_time=1.5)
        self.wait(SHORT)
        self.play(FadeIn(t2_arr2), Write(t2_c), run_time=1.5)
        self.wait(PAUSE)

        # ── Dock at idx=1 ────────────────────────────────────────────────
        c2, c2_t, c2_e, c2_b = make_card(
            "Trick 2 · Log-Derivative Trick",
            r"\nabla_\theta P(\tau|\theta) = P(\tau|\theta)\,\nabla_\theta \log P(\tau|\theta)",
            TRICK2_C, eq_fs=14,
        )
        c2.move_to(dock_pos(1))
        self.play(
            FadeOut(VGroup(t2_a, t2_arr1, t2_b, t2_arr2), shift=DOWN * 0.15),
            ReplacementTransform(t2_title, c2_t),
            ReplacementTransform(t2_c, c2_e),
            Create(c2_b),
            run_time=DOCK_RT, rate_func=smooth,
        )
        self.wait(SHORT)

        # ═══════════════════════════════════════════════════════════════════
        # TRICK 3 — Log-Prob of a Trajectory  (PURPLE)
        #    uses Trick 1  →  Trick 1 discarded on dock (its job is done)
        # ═══════════════════════════════════════════════════════════════════
        t3_title = text("Trick 3 — Log-Probability of a Trajectory",
                        font_size=36, color=TRICK3_C, weight=BOLD)
        t3_note  = text("Take the log of Trick 1:", font_size=24)
        VGroup(t3_title, t3_note).arrange(DOWN, buff=0.3).move_to(STAGE + UP * 2.0)

        self.play(FadeIn(t3_title, shift=UP * 0.2), run_time=1.0)
        self.play(FadeIn(t3_note),
                  Indicate(c1, color=TRICK1_C, scale_factor=1.10),
                  run_time=1.2)

        t3_from = math(
            r"P(\tau|\theta) \;=\; \rho_{0}(s_0)\,\prod_{t=0}^{T} "
            r"P(s_{t+1}|s_t, a_t)\,\pi_{\theta}(a_t|s_t)",
            font_size=30,
        )
        t3_arrow = math(r"\Downarrow\;\;\log", font_size=28, color=BODY_GRAY)
        t3_log = math(
            r"\log P(\tau|\theta) \;=\; \log \rho_{0}(s_0) \;+\; "
            r"\sum_{t=0}^{T} \big(\log P(s_{t+1}|s_t, a_t) "
            r"+ \log \pi_{\theta}(a_t|s_t)\big)",
            font_size=28, color=TRICK3_C,
        )
        VGroup(t3_from, t3_arrow, t3_log).arrange(DOWN, buff=0.35) \
            .move_to(STAGE + DOWN * 0.4)

        self.play(Write(t3_from), run_time=1.6)
        self.wait(SHORT)
        self.play(FadeIn(t3_arrow))
        self.play(TransformFromCopy(t3_from, t3_log), run_time=2.0)
        self.wait(PAUSE)

        # ── Dock at idx=1 (final position after repack),
        #    discard Trick 1, slide Trick 2 up to idx=0 — all in one beat
        c3, c3_t, c3_e, c3_b = make_card(
            "Trick 3 · Log-Prob of Trajectory",
            r"\log P(\tau|\theta) = \log\rho_{0} + \sum_t \big(\log P(s_{t+1}|s_t,a_t) + \log \pi_\theta(a_t|s_t)\big)",
            TRICK3_C, eq_fs=10,
        )
        c3.move_to(dock_pos(1))
        self.play(
            FadeOut(t3_note, shift=DOWN * 0.15),
            FadeOut(VGroup(t3_from, t3_arrow), shift=DOWN * 0.15),
            ReplacementTransform(t3_title, c3_t),
            ReplacementTransform(t3_log, c3_e),
            Create(c3_b),
            FadeOut(c1, shift=RIGHT * 0.3),
            c2.animate.move_to(dock_pos(0)),
            run_time=DOCK_RT, rate_func=smooth,
        )
        self.wait(SHORT)

        # ═══════════════════════════════════════════════════════════════════
        # TRICK 4 — Environment Gradients = 0  (RED)
        # ═══════════════════════════════════════════════════════════════════
        t4_title = text("Trick 4 — Environment Gradients = 0",
                        font_size=38, color=TRICK4_C, weight=BOLD)
        t4_intro = text("The environment has no θ-dependence, so:", font_size=26)
        t4_e1 = math(r"\nabla_{\theta}\,\rho_{0}(s_0) \;=\; 0", font_size=36, color=TRICK4_C)
        t4_e2 = math(r"\nabla_{\theta}\,P(s_{t+1}|s_t, a_t) \;=\; 0", font_size=36, color=TRICK4_C)
        t4_e3 = math(r"\nabla_{\theta}\,R(\tau) \;=\; 0", font_size=36, color=TRICK4_C)
        zeros = VGroup(t4_e1, t4_e2, t4_e3).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        VGroup(t4_title, t4_intro, zeros).arrange(DOWN, buff=0.4).move_to(STAGE)

        self.play(FadeIn(t4_title, shift=UP * 0.2), run_time=1.0)
        self.play(FadeIn(t4_intro))
        for z in zeros:
            self.play(FadeIn(z, shift=UP * 0.1), run_time=0.6)
        self.wait(PAUSE)

        # ── Dock at idx=2 (no discards) ──────────────────────────────────
        c4, c4_t, c4_e, c4_b = make_card(
            "Trick 4 · Env Gradients = 0",
            r"\nabla_\theta \rho_{0} = 0,\;\; \nabla_\theta P(s'|s,a) = 0,\;\; \nabla_\theta R(\tau) = 0",
            TRICK4_C, eq_fs=12,
        )
        c4.move_to(dock_pos(2))
        self.play(
            FadeOut(t4_intro, shift=DOWN * 0.15),
            ReplacementTransform(t4_title, c4_t),
            ReplacementTransform(zeros, c4_e),
            Create(c4_b),
            run_time=DOCK_RT, rate_func=smooth,
        )
        self.wait(SHORT)

        # ═══════════════════════════════════════════════════════════════════
        # TRICK 5 — Grad-Log-Prob  (GREEN)
        #    uses Tricks 3 + 4  →  both discarded on dock
        # ═══════════════════════════════════════════════════════════════════
        t5_title = text("Trick 5 — Grad-Log-Prob of a Trajectory",
                        font_size=36, color=TRICK5_C, weight=BOLD)
        t5_note  = text("Take ∇_θ of Trick 3 and apply Trick 4 to cancel env terms:",
                        font_size=24)
        VGroup(t5_title, t5_note).arrange(DOWN, buff=0.3).move_to(STAGE + UP * 2.1)

        self.play(FadeIn(t5_title, shift=UP * 0.2), run_time=1.0)
        self.play(
            FadeIn(t5_note),
            Indicate(c3, color=TRICK3_C, scale_factor=1.10),
            Indicate(c4, color=TRICK4_C, scale_factor=1.10),
            run_time=1.4,
        )

        t5_expanded = MathTex(
            r"\nabla_{\theta}\log P(\tau|\theta) \;=\;",             # 0
            r"\nabla_{\theta}\log \rho_{0}(s_0)",                     # 1 — cancel
            r"\;+\; \sum_{t=0}^{T}\Big(",                             # 2
            r"\nabla_{\theta}\log P(s_{t+1}|s_t, a_t)",               # 3 — cancel
            r"\;+\; \nabla_{\theta}\log \pi_{\theta}(a_t|s_t)\Big)",  # 4
            color=BLACK, font_size=26,
        ).move_to(STAGE + DOWN * 0.3)

        self.play(Write(t5_expanded), run_time=2.0)
        self.wait(SHORT)

        cross_a = Line(
            t5_expanded[1].get_left() + LEFT * 0.05,
            t5_expanded[1].get_right() + RIGHT * 0.05,
            color=NOTE_RED, stroke_width=5,
        ).rotate(0.05)
        cross_b = Line(
            t5_expanded[3].get_left() + LEFT * 0.05,
            t5_expanded[3].get_right() + RIGHT * 0.05,
            color=NOTE_RED, stroke_width=5,
        ).rotate(0.05)
        cancel_note = text("(= 0 by Trick 4)", font_size=22, color=NOTE_RED) \
            .next_to(t5_expanded, DOWN, buff=0.3)
        self.play(Create(cross_a), Create(cross_b), FadeIn(cancel_note), run_time=1.2)
        self.wait(PAUSE)

        t5_final = math(
            r"\nabla_{\theta}\log P(\tau|\theta) \;=\; "
            r"\sum_{t=0}^{T} \nabla_{\theta}\log \pi_{\theta}(a_t|s_t)",
            font_size=38, color=TRICK5_C,
        ).move_to(t5_expanded.get_center())
        self.play(
            FadeOut(VGroup(t5_expanded, cross_a, cross_b, cancel_note)),
            FadeIn(t5_final, shift=UP * 0.1),
            run_time=1.3,
        )
        self.wait(PAUSE)

        # ── Dock at idx=1 (final position), discard Tricks 3 + 4,
        #    Trick 2 stays at idx=0 — all smooth in one beat
        c5, c5_t, c5_e, c5_b = make_card(
            "Trick 5 · Grad-Log-Prob",
            r"\nabla_\theta \log P(\tau|\theta) = \sum_{t} \nabla_\theta \log \pi_\theta(a_t|s_t)",
            TRICK5_C, eq_fs=14,
        )
        c5.move_to(dock_pos(1))
        self.play(
            FadeOut(t5_note, shift=DOWN * 0.15),
            ReplacementTransform(t5_title, c5_t),
            ReplacementTransform(t5_final, c5_e),
            Create(c5_b),
            FadeOut(c3, shift=RIGHT * 0.3),
            FadeOut(c4, shift=RIGHT * 0.3),
            run_time=DOCK_RT, rate_func=smooth,
        )
        self.wait(PAUSE)

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 2 — Main derivation
        # ═══════════════════════════════════════════════════════════════════
        kickoff = text("Now we derive the policy gradient",
                       font_size=28, color=ACCENT, weight=BOLD) \
            .to_edge(UP, buff=0.4)
        self.play(FadeIn(kickoff, shift=DOWN * 0.15))
        self.wait(SHORT)

        main_anchor = LEFT * 2.6 + UP * 0.3
        note_offset = DOWN * 1.4

        # Step 0 ─────────────────────────────────────────────────────────
        step0 = MathTex(
            r"\nabla_{\theta} J(\pi_{\theta})", r"=",
            r"\nabla_{\theta}", r"\mathbb{E}_{\tau \sim \pi_{\theta}}",
            r"\big[", r"R(\tau)", r"\big]",
            font_size=42, color=BLACK,
        ).move_to(main_anchor)
        self.play(Write(step0), run_time=MORPH)
        self.wait(PAUSE)

        # Step 1 ─────────────────────────────────────────────────────────
        step1 = MathTex(
            r"\nabla_{\theta} J(\pi_{\theta})", r"=",
            r"\nabla_{\theta}", r"\int_{\tau}",
            r"P(\tau|\theta)", r"\,R(\tau)",
            font_size=42, color=BLACK,
        ).move_to(main_anchor)
        note1 = text("expand expectation as an integral",
                     font_size=24).move_to(main_anchor + note_offset)
        self.play(
            TransformMatchingTex(step0, step1),
            FadeIn(note1, shift=UP * 0.2),
            run_time=MORPH,
        )
        self.wait(PAUSE)

        # Step 2 ─────────────────────────────────────────────────────────
        step2 = MathTex(
            r"\nabla_{\theta} J(\pi_{\theta})", r"=",
            r"\int_{\tau}", r"\nabla_{\theta}",
            r"P(\tau|\theta)", r"\,R(\tau)",
            font_size=42, color=BLACK,
        ).move_to(main_anchor)
        note2 = text("swap gradient and integral",
                     font_size=24).move_to(main_anchor + note_offset)
        self.play(
            FadeOut(note1, shift=DOWN * 0.2),
            TransformMatchingTex(step1, step2),
            FadeIn(note2, shift=UP * 0.2),
            run_time=MORPH,
        )
        self.wait(PAUSE)

        # Step 3 ── apply Trick 2 ────────────────────────────────────────
        step3 = MathTex(
            r"\nabla_{\theta} J(\pi_{\theta})", r"=",
            r"\int_{\tau}",
            r"P(\tau|\theta)", r"\,\nabla_{\theta}\log P(\tau|\theta)",
            r"\,R(\tau)",
            font_size=38, color=BLACK,
        ).move_to(main_anchor)
        step3[4].set_color(TRICK2_C)
        note3 = text("apply Trick 2 — log-derivative trick",
                     font_size=24, color=TRICK2_C, weight=BOLD) \
            .move_to(main_anchor + note_offset)
        self.play(
            FadeOut(note2),
            TransformMatchingTex(step2, step3),
            FadeIn(note3, shift=UP * 0.2),
            Indicate(c2, color=TRICK2_C, scale_factor=1.14),
            run_time=MORPH,
        )
        self.wait(PAUSE)

        # ── Discard Trick 2; Trick 5 slides up to idx=0 ─────────────────
        self.play(
            FadeOut(c2, shift=RIGHT * 0.3),
            c5.animate.move_to(dock_pos(0)),
            run_time=1.3, rate_func=smooth,
        )
        self.wait(SHORT)

        # Step 4 ─────────────────────────────────────────────────────────
        step4 = MathTex(
            r"\nabla_{\theta} J(\pi_{\theta})", r"=",
            r"\mathbb{E}_{\tau \sim \pi_{\theta}}", r"\big[",
            r"\nabla_{\theta}\log P(\tau|\theta)", r"\,R(\tau)",
            r"\big]",
            font_size=42, color=BLACK,
        ).move_to(main_anchor)
        step4[4].set_color(TRICK2_C)
        note4 = text("rewrite as expectation",
                     font_size=24).move_to(main_anchor + note_offset)
        self.play(
            FadeOut(note3),
            TransformMatchingTex(step3, step4),
            FadeIn(note4, shift=UP * 0.2),
            run_time=MORPH,
        )
        self.wait(PAUSE)

        # Step 5 ── apply Trick 5 ────────────────────────────────────────
        step5 = MathTex(
            r"\nabla_{\theta} J(\pi_{\theta})", r"=",
            r"\mathbb{E}_{\tau \sim \pi_{\theta}}", r"\Big[",
            r"\sum_{t=0}^{T} \nabla_{\theta}\log \pi_{\theta}(a_t|s_t)",
            r"\,R(\tau)",
            r"\Big]",
            font_size=38, color=BLACK,
        ).move_to(main_anchor)
        step5[4].set_color(TRICK5_C)
        note5 = text("apply Trick 5 — grad-log-prob",
                     font_size=24, color=TRICK5_C, weight=BOLD) \
            .move_to(main_anchor + note_offset)
        self.play(
            FadeOut(note4),
            TransformMatchingTex(step4, step5),
            FadeIn(note5, shift=UP * 0.2),
            Indicate(c5, color=TRICK5_C, scale_factor=1.14),
            run_time=MORPH,
        )
        self.wait(PAUSE)

        # ── Discard Trick 5 + box + center final reveal ─────────────────
        final_box = SurroundingRectangle(step5, color=ORANGE_C, buff=0.22,
                                          corner_radius=0.12, stroke_width=4)
        self.play(
            FadeOut(c5, shift=RIGHT * 0.3),
            FadeOut(note5),
            Create(final_box),
            run_time=1.5, rate_func=smooth,
        )
        final_group = VGroup(step5, final_box)
        self.play(
            FadeOut(kickoff),
            final_group.animate.move_to(ORIGIN).scale(1.15),
            run_time=1.8, rate_func=smooth,
        )
        self.wait(PAUSE * 2)
        self.next_slide()
