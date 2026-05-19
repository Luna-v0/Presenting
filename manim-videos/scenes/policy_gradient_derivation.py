"""Policy Gradient — animated derivation, tricks live and color-coded.

A single continuous scene that derives the policy gradient theorem from
J(π_θ) = E[R(τ)]. The two key tricks are derived inline and color-coded:

    Trick 1 (BLUE):   log-derivative trick    ∇P = P ∇log P
    Trick 2 (GREEN):  grad-log-prob simplification

Each trick is derived front-and-center, then shrinks to a small reference
panel on the right while the main derivation morphs through. The colored
piece of the main equation matches the color of the trick that produced it.

Render:
    uv run manim scenes/policy_gradient_derivation.py PolicyGradientDerivation -ql
"""

from manim import (
    BLACK,
    BOLD,
    DARK_GRAY,
    DOWN,
    LEFT,
    NORMAL,
    RIGHT,
    UP,
    WHITE,
    Create,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    ReplacementTransform,
    Scene,
    SurroundingRectangle,
    Text,
    TransformFromCopy,
    TransformMatchingTex,
    VGroup,
    Write,
)


# ── Palette ──────────────────────────────────────────────────────────────────
TEXT_C   = BLACK
DARK     = DARK_GRAY
TRICK1_C = "#1565C0"   # log-derivative trick  (deep blue)
TRICK2_C = "#1B5E20"   # grad-log-prob         (deep green)
CANCEL_C = "#C62828"   # cancelled terms       (deep red)
NOTE_C   = "#6A1B9A"   # generic step note     (deep purple)
FRAME_C  = "#FB8C00"   # final-box accent      (orange)

# ── Pacing ───────────────────────────────────────────────────────────────────
PAUSE = 3.0     # main beat between steps
SHORT = 1.5     # short pause inside trick mini-derivations
RT    = 1.4     # default run_time for equation morphs


def text(s: str, font_size: int = 28, color=DARK, weight=NORMAL) -> Text:
    return Text(s, font="TeX Gyre Termes", color=color, font_size=font_size, weight=weight)


def make_panel(title_str: str, formula_tex: str, color,
               title_fs: int = 20, eq_fs: int = 22):
    """Small color-coded reference card for a trick."""
    title = text(title_str, font_size=title_fs, color=color, weight=BOLD)
    eq = MathTex(formula_tex, font_size=eq_fs, color=color)
    grp = VGroup(title, eq).arrange(DOWN, buff=0.18)
    box = SurroundingRectangle(grp, color=color, buff=0.22,
                                corner_radius=0.12, stroke_width=2)
    return VGroup(grp, box), title, eq, box


class PolicyGradientDerivation(Scene):
    def construct(self):
        self.camera.background_color = WHITE

        # ═══════════════════════════════════════════════════════════════════
        # PREAMBLE — set the goal
        # ═══════════════════════════════════════════════════════════════════
        intro = text("We aim to maximize the expected return", font_size=32)
        intro.move_to(UP * 2.4)

        obj = MathTex(
            r"J(\pi_{\theta}) \;=\; \mathbb{E}_{\tau \sim \pi_{\theta}}\big[R(\tau)\big]",
            font_size=54, color=TEXT_C,
        ).next_to(intro, DOWN, buff=0.6)

        self.play(Write(intro), run_time=1.2)
        self.play(Write(obj), run_time=1.5)
        self.wait(PAUSE)

        intro2 = text("To improve the policy by gradient ascent, we need", font_size=32)
        intro2.next_to(obj, DOWN, buff=0.9)

        target = MathTex(
            r"\nabla_{\theta} J(\pi_{\theta}) \;=\; ?",
            font_size=54, color=TEXT_C,
        ).next_to(intro2, DOWN, buff=0.5)

        self.play(Write(intro2), run_time=1.2)
        self.play(Write(target), run_time=1.2)
        self.wait(PAUSE)

        self.play(*[FadeOut(m) for m in [intro, intro2, obj, target]], run_time=0.8)

        # ═══════════════════════════════════════════════════════════════════
        # MAIN DERIVATION — morphs in place, leaves space on right for panels
        # ═══════════════════════════════════════════════════════════════════
        main_anchor = LEFT * 2.0 + UP * 0.4
        note_offset = DOWN * 1.3

        step0 = MathTex(
            r"\nabla_{\theta} J(\pi_{\theta})", r"=",
            r"\nabla_{\theta}", r"\mathbb{E}_{\tau \sim \pi_{\theta}}",
            r"\big[", r"R(\tau)", r"\big]",
            font_size=44, color=TEXT_C,
        ).move_to(main_anchor)

        self.play(Write(step0), run_time=RT)
        self.wait(PAUSE)

        # Step 1 — expand expectation
        step1 = MathTex(
            r"\nabla_{\theta} J(\pi_{\theta})", r"=",
            r"\nabla_{\theta}", r"\int_{\tau}",
            r"P(\tau|\theta)", r"\,R(\tau)",
            font_size=44, color=TEXT_C,
        ).move_to(main_anchor)
        note1 = text("expand expectation as an integral", font_size=26, color=NOTE_C)
        note1.move_to(main_anchor + note_offset)
        self.play(
            TransformMatchingTex(step0, step1),
            FadeIn(note1, shift=UP * 0.2),
            run_time=RT,
        )
        self.wait(PAUSE)

        # Step 2 — swap gradient and integral
        step2 = MathTex(
            r"\nabla_{\theta} J(\pi_{\theta})", r"=",
            r"\int_{\tau}", r"\nabla_{\theta}",
            r"P(\tau|\theta)", r"\,R(\tau)",
            font_size=44, color=TEXT_C,
        ).move_to(main_anchor)
        note2 = text("swap gradient and integral (Leibniz)", font_size=26, color=NOTE_C)
        note2.move_to(main_anchor + note_offset)
        self.play(
            FadeOut(note1, shift=DOWN * 0.2),
            TransformMatchingTex(step1, step2),
            FadeIn(note2, shift=UP * 0.2),
            run_time=RT,
        )
        self.wait(PAUSE)

        # ═══════════════════════════════════════════════════════════════════
        # TRICK 1 — log-derivative trick (BLUE)
        # ═══════════════════════════════════════════════════════════════════
        self.play(
            FadeOut(note2),
            step2.animate.scale(0.85).to_edge(UP, buff=0.4).to_edge(LEFT, buff=1.0),
            run_time=0.9,
        )

        t1_label = text("Trick 1:  the log-derivative trick",
                        font_size=32, color=TRICK1_C, weight=BOLD)
        t1_rule_a = MathTex(
            r"\frac{d}{dx}\log(x) \;=\; \frac{1}{x}",
            font_size=42, color=TRICK1_C,
        )
        t1_arrow = MathTex(r"\Downarrow", font_size=40, color=DARK)
        t1_rule_b = MathTex(
            r"\nabla_{\theta} P(\tau|\theta) \;=\; "
            r"P(\tau|\theta)\,\nabla_{\theta}\log P(\tau|\theta)",
            font_size=40, color=TRICK1_C,
        )
        VGroup(t1_label, t1_rule_a, t1_arrow, t1_rule_b).arrange(DOWN, buff=0.35).move_to(DOWN * 0.4)

        self.play(FadeIn(t1_label, shift=UP * 0.2), run_time=1.0)
        self.play(Write(t1_rule_a), run_time=1.2)
        self.wait(SHORT)
        self.play(FadeIn(t1_arrow))
        self.play(Write(t1_rule_b), run_time=1.5)
        self.wait(PAUSE)

        # Shrink trick 1 to the top-right reference panel
        _, p1_title, p1_eq, p1_box = make_panel(
            "log-derivative trick",
            r"\nabla_{\theta} P = P\,\nabla_{\theta}\log P",
            TRICK1_C,
        )
        VGroup(p1_title, p1_eq, p1_box).to_edge(RIGHT, buff=0.4).shift(UP * 2.4)

        self.play(
            FadeOut(t1_rule_a),
            FadeOut(t1_arrow),
            ReplacementTransform(t1_label, p1_title),
            ReplacementTransform(t1_rule_b, p1_eq),
            Create(p1_box),
            run_time=1.5,
        )
        self.play(step2.animate.move_to(main_anchor).scale(1 / 0.85), run_time=0.8)
        self.wait(SHORT)

        # Step 3 — apply trick 1 (new piece is BLUE)
        step3 = MathTex(
            r"\nabla_{\theta} J(\pi_{\theta})", r"=",
            r"\int_{\tau}",
            r"P(\tau|\theta)", r"\,\nabla_{\theta}\log P(\tau|\theta)",
            r"\,R(\tau)",
            font_size=40, color=TEXT_C,
        ).move_to(main_anchor)
        step3[4].set_color(TRICK1_C)

        note3 = text("apply the log-derivative trick", font_size=26, color=TRICK1_C)
        note3.move_to(main_anchor + note_offset)

        self.play(
            TransformMatchingTex(step2, step3),
            FadeIn(note3, shift=UP * 0.2),
            run_time=RT,
        )
        self.wait(PAUSE)

        # Step 4 — fold back to expectation
        step4 = MathTex(
            r"\nabla_{\theta} J(\pi_{\theta})", r"=",
            r"\mathbb{E}_{\tau \sim \pi_{\theta}}", r"\big[",
            r"\nabla_{\theta}\log P(\tau|\theta)", r"\,R(\tau)",
            r"\big]",
            font_size=42, color=TEXT_C,
        ).move_to(main_anchor)
        step4[4].set_color(TRICK1_C)

        note4 = text("rewrite as an expectation", font_size=26, color=NOTE_C)
        note4.move_to(main_anchor + note_offset)

        self.play(
            FadeOut(note3),
            TransformMatchingTex(step3, step4),
            FadeIn(note4, shift=UP * 0.2),
            run_time=RT,
        )
        self.wait(PAUSE)

        # ═══════════════════════════════════════════════════════════════════
        # TRICK 2 — grad-log-prob simplification (GREEN)
        # ═══════════════════════════════════════════════════════════════════
        self.play(
            FadeOut(note4),
            step4.animate.scale(0.85).to_edge(UP, buff=0.4).to_edge(LEFT, buff=1.0),
            run_time=0.9,
        )

        t2_label = text("Trick 2:  grad-log-prob of a trajectory",
                        font_size=30, color=TRICK2_C, weight=BOLD)
        traj_p = MathTex(
            r"P(\tau|\theta) \;=\; \rho_0(s_0) \prod_{t=0}^{T} "
            r"P(s_{t+1}|s_t, a_t)\,\pi_{\theta}(a_t|s_t)",
            font_size=30, color=TEXT_C,
        )
        log_p = MathTex(
            r"\log P(\tau|\theta) \;=\; \log \rho_0(s_0) \;+\; "
            r"\sum_{t=0}^{T} \big(\log P(s_{t+1}|s_t, a_t) "
            r"+ \log \pi_{\theta}(a_t|s_t)\big)",
            font_size=26, color=TEXT_C,
        )
        # Split into chunks so we can strike through the env-only terms.
        grad_log_p = MathTex(
            r"\nabla_{\theta}\log P(\tau|\theta) \;=\;",                # 0
            r"\nabla_{\theta}\log \rho_0(s_0)",                          # 1  ← canceled
            r"\;+\; \sum_{t=0}^{T}\big(",                                # 2
            r"\nabla_{\theta}\log P(s_{t+1}|s_t, a_t)",                  # 3  ← canceled
            r"\;+\; \nabla_{\theta}\log \pi_{\theta}(a_t|s_t)\big)",     # 4
            font_size=24, color=TEXT_C,
        )

        VGroup(t2_label, traj_p, log_p, grad_log_p).arrange(DOWN, buff=0.40).move_to(DOWN * 0.4)

        self.play(FadeIn(t2_label, shift=UP * 0.2), run_time=1.0)
        self.play(Write(traj_p), run_time=1.6)
        self.wait(SHORT)
        self.play(TransformFromCopy(traj_p, log_p), run_time=1.8)
        self.wait(SHORT)
        self.play(TransformFromCopy(log_p, grad_log_p), run_time=1.8)
        self.wait(SHORT)

        # Cross out the env-only terms (no θ dependence ⇒ gradient = 0)
        cross_a = Line(
            grad_log_p[1].get_left() + LEFT * 0.05,
            grad_log_p[1].get_right() + RIGHT * 0.05,
            color=CANCEL_C, stroke_width=5,
        ).rotate(0.04)
        cross_b = Line(
            grad_log_p[3].get_left() + LEFT * 0.05,
            grad_log_p[3].get_right() + RIGHT * 0.05,
            color=CANCEL_C, stroke_width=5,
        ).rotate(0.04)
        env_note = text("(no dependence on θ — gradients vanish)",
                        font_size=22, color=CANCEL_C)
        env_note.next_to(grad_log_p, DOWN, buff=0.3)

        self.play(Create(cross_a), Create(cross_b), FadeIn(env_note), run_time=1.2)
        self.wait(PAUSE)

        # Collapse to the clean grad-log-prob result
        t2_result = MathTex(
            r"\nabla_{\theta}\log P(\tau|\theta) \;=\; "
            r"\sum_{t=0}^{T} \nabla_{\theta}\log \pi_{\theta}(a_t|s_t)",
            font_size=34, color=TRICK2_C,
        ).move_to(grad_log_p.get_center())

        self.play(
            FadeOut(traj_p),
            FadeOut(log_p),
            FadeOut(grad_log_p),
            FadeOut(cross_a),
            FadeOut(cross_b),
            FadeOut(env_note),
            FadeIn(t2_result),
            run_time=1.2,
        )
        self.wait(PAUSE)

        # Shrink trick 2 to the lower-right reference panel
        _, p2_title, p2_eq, p2_box = make_panel(
            "grad-log-prob",
            r"\nabla_{\theta}\log P(\tau|\theta) = "
            r"\sum_t \nabla_{\theta}\log \pi_{\theta}(a_t|s_t)",
            TRICK2_C,
            title_fs=20, eq_fs=18,
        )
        VGroup(p2_title, p2_eq, p2_box).to_edge(RIGHT, buff=0.4).shift(DOWN * 0.3)

        self.play(
            ReplacementTransform(t2_label, p2_title),
            ReplacementTransform(t2_result, p2_eq),
            Create(p2_box),
            run_time=1.5,
        )
        self.play(step4.animate.move_to(main_anchor).scale(1 / 0.85), run_time=0.8)
        self.wait(SHORT)

        # Step 5 — apply trick 2 (new piece is GREEN)
        step5 = MathTex(
            r"\nabla_{\theta} J(\pi_{\theta})", r"=",
            r"\mathbb{E}_{\tau \sim \pi_{\theta}}", r"\Big[",
            r"\sum_{t=0}^{T} \nabla_{\theta}\log \pi_{\theta}(a_t|s_t)",
            r"\,R(\tau)",
            r"\Big]",
            font_size=38, color=TEXT_C,
        ).move_to(main_anchor)
        step5[4].set_color(TRICK2_C)

        note5 = text("apply the grad-log-prob simplification",
                     font_size=26, color=TRICK2_C)
        note5.move_to(main_anchor + note_offset)

        self.play(
            TransformMatchingTex(step4, step5),
            FadeIn(note5, shift=UP * 0.2),
            run_time=RT,
        )
        self.wait(PAUSE)

        # Final boxed result
        final_box = SurroundingRectangle(
            step5, color=FRAME_C, buff=0.25, corner_radius=0.15, stroke_width=4,
        )
        self.play(Create(final_box), run_time=1.2)
        self.wait(PAUSE * 2)
