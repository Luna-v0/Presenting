"""Gradient-descent demo deck built with manim-beamer + manim-slides.

The deck is split across three scenes because the 3D bowl scene needs a
ThreeDScene, which is not compatible with manim-beamer's MovingCameraScene-based
SlideShow. manim-slides plays them as one continuous show:

    uv run manim-slides render scenes/beamer_demo.py BeamerDemoPart1 BowlDescent3D BeamerDemoPart2 -ql
    uv run manim-slides present BeamerDemoPart1 BowlDescent3D BeamerDemoPart2
    # or export a self-contained HTML deck:
    uv run manim-slides convert BeamerDemoPart1 BowlDescent3D BeamerDemoPart2 beamer_demo.html
"""

from manim import (
    BLACK,
    BLUE,
    BLUE_E,
    DEGREES,
    DOWN,
    GREEN,
    LEFT,
    ORANGE,
    RED,
    UP,
    UR,
    YELLOW,
    Create,
    DecimalNumber,
    FadeIn,
    FadeOut,
    Line3D,
    MathTex,
    ReplacementTransform,
    Sphere,
    SurroundingRectangle,
    Surface,
    Text,
    ThreeDAxes,
    TransformMatchingTex,
    ValueTracker,
    Write,
)
from manim_slides import ThreeDSlide
from manim_beamer.blocks import AlertBlock, ExampleBlock, RemarkBlock
from manim_beamer.lists import BulletedList, ItemizedList
from manim_beamer.slides import (
    BeamerSlide,
    SlideShow,
    SlideWithBlocks,
    SlideWithList,
)


def math(tex: str, font_size: int = 30) -> MathTex:
    return MathTex(tex, color=BLACK, font_size=font_size)


def text(s: str, font_size: int = 30) -> Text:
    return Text(s, font="TeX Gyre Termes", color=BLACK, font_size=font_size)


class DerivationSlide(BeamerSlide):
    """Animated derivation of the gradient descent update via Taylor expansion."""

    def __init__(self):
        super().__init__(
            title="Deriving the update rule",
            subtitle="From a Taylor expansion to gradient descent",
        )

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        if target_scene is None:
            target_scene = self

        title = self.title_text.copy()
        subtitle = self.subtitle_text.copy()
        target_scene.play(Write(title), Write(subtitle))
        target_scene.next_slide()

        caption_y = UP * 1.6
        eq_y = DOWN * 0.4

        caption = text("First-order Taylor expansion around x", font_size=30)
        caption.move_to(caption_y)

        eq1 = MathTex(
            r"f(x+\Delta x)", r"\approx", r"f(x)", r"+", r"\nabla f(x)", r"\cdot", r"\Delta x",
            color=BLACK, font_size=48,
        ).move_to(eq_y)

        target_scene.play(Write(caption), Write(eq1))
        target_scene.next_slide()

        caption2 = text("Isolate the change in f", font_size=30).move_to(caption_y)
        eq2 = MathTex(
            r"f(x+\Delta x)", r"-", r"f(x)", r"\approx", r"\nabla f(x)", r"\cdot", r"\Delta x",
            color=BLACK, font_size=48,
        ).move_to(eq_y)
        target_scene.play(
            ReplacementTransform(caption, caption2),
            TransformMatchingTex(eq1, eq2),
        )
        target_scene.next_slide()

        caption3 = text(
            "Steepest decrease: choose \u0394x anti-parallel to \u2207f",
            font_size=30,
        ).move_to(caption_y)
        eq3 = MathTex(
            r"\Delta x", r"=", r"-\eta", r"\nabla f(x)",
            color=BLACK, font_size=52,
        ).move_to(eq_y)
        target_scene.play(
            ReplacementTransform(caption2, caption3),
            FadeOut(eq2),
        )
        target_scene.play(Write(eq3))
        target_scene.next_slide()

        caption4 = text("Apply iteratively  \u21d2  gradient descent", font_size=30).move_to(caption_y)
        eq4 = MathTex(
            r"x_{t+1}", r"=", r"x_t", r"-", r"\eta", r"\nabla f(x_t)",
            color=BLACK, font_size=56,
        ).move_to(eq_y)
        target_scene.play(
            ReplacementTransform(caption3, caption4),
            TransformMatchingTex(eq3, eq4),
        )
        box = SurroundingRectangle(
            eq4, color=ORANGE, buff=0.25, corner_radius=0.1, stroke_width=4,
        )
        target_scene.play(Create(box))
        target_scene.wait(1)
        target_scene.next_slide()


class BowlDescent3D(ThreeDSlide):
    """3D paraboloid f(x,y) = 0.5(x^2 + 3y^2) with a ball rolling down via GD."""

    def construct(self):
        title = Text(
            "Watching it descend",
            font="TeX Gyre Termes",
            color=BLACK,
            font_size=52,
            weight="BOLD",
        ).to_edge(UP)
        subtitle = MathTex(
            r"f(x,y) = \tfrac{1}{2}(x^{2} + 3y^{2}),\quad \eta = 0.2",
            color=BLACK,
            font_size=32,
        ).next_to(title, DOWN, buff=0.2)
        self.add_fixed_in_frame_mobjects(title, subtitle)
        self.play(Write(title), Write(subtitle))
        self.next_slide()

        self.set_camera_orientation(phi=68 * DEGREES, theta=-50 * DEGREES, zoom=0.9)

        axes = ThreeDAxes(
            x_range=[-4, 4, 1],
            y_range=[-3, 3, 1],
            z_range=[0, 12, 3],
            x_length=7,
            y_length=5,
            z_length=4,
            axis_config={"color": BLACK, "stroke_width": 2},
        ).shift(DOWN * 0.5)

        def f(x, y):
            return 0.5 * (x * x + 3 * y * y)

        surface = Surface(
            lambda u, v: axes.c2p(u, v, f(u, v)),
            u_range=[-3.0, 3.0],
            v_range=[-2.0, 2.0],
            resolution=(36, 28),
        )
        surface.set_style(
            fill_opacity=0.65,
            stroke_color=BLUE_E,
            stroke_width=0.5,
        )
        surface.set_fill_by_value(
            axes=axes,
            colorscale=[(BLUE, 0.0), (GREEN, 4.0), (YELLOW, 8.0), (RED, 11.0)],
            axis=2,
        )

        self.play(Create(axes), run_time=1.0)
        self.play(Create(surface), run_time=2.5)
        self.next_slide()

        eta = 0.2
        path = [(3.0, 2.0)]
        for _ in range(9):
            x, y = path[-1]
            path.append((x - eta * x, y - eta * 3 * y))

        step_tracker = ValueTracker(0)
        f_tracker = ValueTracker(f(*path[0]))

        panel_label = Text(
            "Step", font="TeX Gyre Termes", color=BLACK, font_size=30
        ).to_corner(UR).shift(LEFT * 0.4 + DOWN * 1.2)
        step_counter = DecimalNumber(
            0, num_decimal_places=0, color=BLACK, font_size=44
        ).next_to(panel_label, DOWN, buff=0.15)
        step_counter.add_updater(lambda m: m.set_value(step_tracker.get_value()))

        f_label = MathTex(r"f(x_t, y_t)", color=BLACK, font_size=32).next_to(
            step_counter, DOWN, buff=0.45
        )
        f_value = DecimalNumber(
            f(*path[0]), num_decimal_places=3, color=BLACK, font_size=44
        ).next_to(f_label, DOWN, buff=0.15)
        f_value.add_updater(lambda m: m.set_value(f_tracker.get_value()))

        self.add_fixed_in_frame_mobjects(panel_label, step_counter, f_label, f_value)

        x0, y0 = path[0]
        ball = Sphere(
            center=axes.c2p(x0, y0, f(x0, y0)),
            radius=0.18,
            resolution=(16, 16),
        ).set_color(RED)

        self.play(
            FadeIn(ball),
            Write(panel_label),
            FadeIn(step_counter),
            Write(f_label),
            FadeIn(f_value),
        )
        self.next_slide()

        self.begin_ambient_camera_rotation(rate=0.12)

        for i in range(1, len(path)):
            prev_p = path[i - 1]
            new_p = path[i]
            segment = Line3D(
                start=axes.c2p(prev_p[0], prev_p[1], f(*prev_p)),
                end=axes.c2p(new_p[0], new_p[1], f(*new_p)),
                color=ORANGE,
                thickness=0.025,
            )
            self.play(
                Create(segment),
                ball.animate.move_to(axes.c2p(new_p[0], new_p[1], f(*new_p))),
                step_tracker.animate.set_value(i),
                f_tracker.animate.set_value(f(*new_p)),
                run_time=0.75,
            )

        self.stop_ambient_camera_rotation()
        self.wait(1.0)
        self.next_slide()


def build_slides():
    title_slide = SlideWithBlocks(
        title="Gradient Descent",
        subtitle="A 5-minute tour, animated with manim-beamer",
        blocks=[],
    )

    motivation = SlideWithList(
        title="Why optimize?",
        subtitle="Learning = fitting parameters to data",
        beamer_list=ItemizedList(
            items=[
                "Most ML reduces to: minimize a loss over parameters.",
                "Closed-form solutions exist only for a small zoo of models.",
                "We need a generic, scalable, derivative-driven recipe.",
                ItemizedList(
                    items=[
                        "Cheap per step",
                        "Works on millions of parameters",
                        "Composes with stochastic mini-batches",
                    ],
                ),
            ],
        ),
    )

    gradient = SlideWithBlocks(
        title="The gradient",
        subtitle="Direction of steepest ascent",
        blocks=[
            ExampleBlock(
                title="Definition",
                content=math(
                    r"\nabla f(x) \;=\; "
                    r"\left[ \tfrac{\partial f}{\partial x_1},"
                    r"\; \dots,\; \tfrac{\partial f}{\partial x_n} \right]^{\top}",
                    font_size=40,
                ),
            ),
            RemarkBlock(
                title="Intuition",
                content=ItemizedList(
                    items=[
                        "Points uphill on the loss surface.",
                        "Magnitude scales with local steepness.",
                        "Negate it to descend.",
                    ],
                ),
            ),
        ],
    )

    update_rule = DerivationSlide()

    failure_modes = SlideWithBlocks(
        title="Failure modes",
        subtitle="Where first-order methods stumble",
        blocks=[
            AlertBlock(
                title="Three classic traps",
                content=ItemizedList(
                    items=[
                        "Saddle points: gradient is zero, but it's not a minimum.",
                        "Non-convex losses admit many local minima.",
                        "Ill-conditioning blows up step counts.",
                    ],
                ),
            ),
            ExampleBlock(
                title="Strongly convex bound",
                content=math(
                    r"f(x_t) - f(x^\star) \;\le\; "
                    r"(1 - \eta\mu)^t \big( f(x_0) - f(x^\star) \big)",
                    font_size=32,
                ),
            ),
        ],
    )

    takeaways = SlideWithList(
        title="Takeaways",
        subtitle="What to remember on Monday",
        beamer_list=BulletedList(
            items=[
                "Gradient descent is the workhorse of modern ML.",
                "Step size is the single most important hyperparameter.",
                "Convexity gives you guarantees; deep nets give you vibes.",
                "Variants (momentum, Adam) are layers on top of this skeleton.",
            ],
        ),
    )

    return [
        title_slide,
        motivation,
        gradient,
        update_rule,
        failure_modes,
        takeaways,
    ]


class BeamerDemoPart1(SlideShow):
    """First half: title, motivation, gradient, animated derivation."""

    def __init__(self, **kwargs):
        super().__init__(slides=build_slides()[:4], **kwargs)


class BeamerDemoPart2(SlideShow):
    """Second half (after the 3D bowl): failure modes, takeaways."""

    def __init__(self, **kwargs):
        super().__init__(slides=build_slides()[4:], **kwargs)
