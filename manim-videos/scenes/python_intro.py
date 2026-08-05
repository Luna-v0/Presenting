"""O que é Python? — intro deck.

Built from screenplays/python_into.md. Scenes:
    PyIntro_01_Timeline    "O que é Python?" → "Mas desde então…" (one continuous
                           timeline; domains shown as icons around a Python hub)
    PyIntro_02_Manim       "these slides are made with Python + Manim" (logo + code)
    PyIntro_03_Philosophy  verbose Java morphs into short Python
    PyIntro_04_Performance Python → C/C++/Rust hidden behind NumPy/pandas

The first two H1s of the screenplay share one scene so the timeline line is a
single persistent mobject — it never fades between 1991 and 2026, only the year
marker slides across it.

Per the screenplay's direction, NO spoken narration ("Fala") is placed on the
slides — only the visuals and the on-screen text called for by each
"Visual"/"Texto" note.

Domain icons are Tabler outline SVGs in scenes/assets/icons/. Guido's photo lives
at scenes/assets/guido.jpg (a labelled placeholder shows if it is missing).

Render & present:
    uv run manim-slides render scenes/python_intro.py \\
        PyIntro_01_Timeline PyIntro_02_Manim PyIntro_03_Philosophy PyIntro_04_Performance \\
        -q h --disable_caching
    uv run manim-slides present \\
        PyIntro_01_Timeline PyIntro_02_Manim PyIntro_03_Philosophy PyIntro_04_Performance

Note: re-renders need --disable_caching (a manim-slides caching quirk otherwise
raises "you have to play at least one animation before pausing").
"""

from pathlib import Path

import numpy as np

from manim import (
    BLACK,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Circle,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    FadeTransform,
    Group,
    ImageMobject,
    Line,
    ManimBanner,
    MathTex,
    ReplacementTransform,
    Rectangle,
    Square,
    Text,
    Transform,
    Triangle,
    VGroup,
    Write,
)
from manim_beamer.lists import ItemizedList
from manim_beamer.slides import SlideShow
from manim_beamer.slides.base import BeamerSlide


ASSETS_DIR = Path(__file__).resolve().parent / "assets"

# Default 16:9 camera frame (MovingCameraScene). x in [-7.11, 7.11], y in [-4, 4].
FRAME_WIDTH = 14.222222

# ── Palette (white background — see manim_beamer.blocks) ─────────────────────
PY_BLUE = "#3776AB"
PY_YELLOW = "#FFD343"
BEAMER_GREEN = "#007f5f"
BEAMER_GREEN_BG = "#e5f9f6"
SERIF = "TeX Gyre Termes"
MONO = "Noto Sans Mono"

# Timeline geometry (shared by the 1991 and 2026 states).
TL_Y = -3.4
TL_LEFT = -6.0
TL_RIGHT = 6.0


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def text(s: str, font_size: int = 30, weight: str = "NORMAL", color=BLACK, font=SERIF) -> Text:
    return Text(s, font=font, color=color, font_size=font_size, weight=weight)


def asset_image(name: str, max_width: float = 4.0, max_height: float = 4.0):
    """Load scenes/assets/<name>; fall back to a labelled placeholder if missing."""
    path = ASSETS_DIR / name
    if path.exists():
        img = ImageMobject(str(path))
        img.scale_to_fit_width(max_width)
        if img.height > max_height:
            img.scale_to_fit_height(max_height)
        return Group(img)

    rect = Rectangle(width=max_width, height=max_height, color=BLACK,
                     fill_color="#f0f0f0", fill_opacity=1, stroke_width=2)
    label = text(f"[foto: {name}]", font_size=24)
    label.move_to(rect.get_center())
    return Group(VGroup(rect, label))


def manim_logo() -> VGroup:
    """The official ManimCE logo — M with a green circle, blue square, red triangle.

    Returned in z-order (triangle, square, circle, M) so the M sits on top.
    Colours read fine on white; the caller scales and positions it.
    """
    ds_m = MathTex(r"\mathbb{M}", fill_color="#343434").scale(7)
    ds_m.shift(2.25 * LEFT + 1.5 * UP)
    circle = Circle(color="#87c2a5", fill_opacity=1).shift(LEFT)
    square = Square(color="#525893", fill_opacity=1).shift(UP)
    triangle = Triangle(color="#e07a5f", fill_opacity=1).shift(RIGHT)
    logo = VGroup(triangle, square, circle, ds_m)
    logo.move_to(ORIGIN)
    return logo


def labeled_box(label: str, fill_color: str = "#e8eef5", stroke_color: str = PY_BLUE,
                width: float = 1.9, height: float = 0.8, font_size: int = 26) -> VGroup:
    box = Rectangle(width=width, height=height, color=stroke_color,
                    fill_color=fill_color, fill_opacity=1.0, stroke_width=2.5)
    txt = text(label, font_size=font_size, weight="BOLD").move_to(box.get_center())
    if txt.width > width - 0.25:
        txt.scale_to_fit_width(width - 0.25)
    return VGroup(box, txt)


def beamer_panel(title: str, items, font_size: int = 26, max_width: float = 6.6) -> VGroup:
    """A width-controlled beamer-style block: green title + underline + arrow list.

    (manim's built-in Title stretches its underline to frame width, which makes
    the stock beamer block far too wide — this hugs the content instead.)
    """
    title_t = text(title, font_size=font_size + 6, color=BEAMER_GREEN)
    list_g = ItemizedList(items=items, font_size=font_size, list_color=BEAMER_GREEN).get_list(1.0)
    w = max(title_t.width, list_g.width)
    underline = Line([0, 0, 0], [w, 0, 0], color=BEAMER_GREEN, stroke_width=2.5)
    body = VGroup(title_t, underline, list_g).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    panel = Rectangle(width=body.width + 0.7, height=body.height + 0.6, color=BEAMER_GREEN,
                      fill_color=BEAMER_GREEN_BG, fill_opacity=1.0, stroke_width=2.5)
    body.move_to(panel.get_center())
    group = VGroup(panel, body)
    if group.width > max_width:
        group.scale_to_fit_width(max_width)
    return group


def code_block(lines, font_size: int):
    """A monospace code panel (sharp rectangle). Single multi-line Text so Pango
    keeps the indentation (per-line VGroups would left-snap and lose it)."""
    code = Text("\n".join(lines), font=MONO, color=BLACK, font_size=font_size, line_spacing=0.6)
    box = Rectangle(width=code.width + 0.9, height=code.height + 0.7, color="#cccccc",
                    fill_color="#f6f8fa", fill_opacity=1.0, stroke_width=2)
    code.move_to(box.get_center())
    return {"box": box, "code": code}


# ─────────────────────────────────────────────────────────────────────────────
# Custom slide base — resets the camera and renders its own (fitted) beamer title
# ─────────────────────────────────────────────────────────────────────────────

class VisualSlide(BeamerSlide):
    """A BeamerSlide whose body is a fully hand-authored animation."""

    def reset_camera(self, target_scene):
        target_scene.camera.frame.move_to(ORIGIN).set(width=FRAME_WIDTH)

    def make_title(self) -> Text:
        title = self.title_text.copy()
        if title.width > 12.5:
            title.scale_to_fit_width(12.5)
        return title.to_edge(UP, buff=0.4)


# ─────────────────────────────────────────────────────────────────────────────
# Scene 1 — O que é Python?  →  Mas desde então…
# ─────────────────────────────────────────────────────────────────────────────

# "Things you can do with Python" — shown as images (voice-over, no text).
DOMAIN_IMAGES = ["deepracer.png", "datavis.jpg", "LLM.png", "webdev.png"]


class PythonTimeline(VisualSlide):
    def __init__(self):
        super().__init__(title="O que é Python?", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)

        # ── Beamer title ─────────────────────────────────────────────────────
        title = self.make_title()
        ts.play(Write(title))
        ts.next_slide()

        # ── Persistent timeline line (drawn ONCE, never faded here) ──────────
        line = Line([TL_LEFT, TL_Y, 0], [TL_RIGHT, TL_Y, 0], color=BLACK, stroke_width=3)
        dot = Dot([TL_LEFT, TL_Y, 0], color=PY_BLUE, radius=0.11)
        year = text("1991", font_size=30, weight="BOLD", color=PY_BLUE)
        year.next_to(dot, UP, buff=0.15)
        ts.play(Create(line))
        ts.play(FadeIn(dot), Write(year))
        ts.next_slide()

        # ── Guido, on the left ───────────────────────────────────────────────
        photo = asset_image("guido.jpg", max_width=3.0, max_height=3.4)
        photo.move_to([-4.3, 0.45, 0])
        name = text("Guido van Rossum", font_size=24, weight="BOLD")
        name.next_to(photo, DOWN, buff=0.2)
        ts.play(FadeIn(photo), Write(name))
        ts.next_slide()

        # ── Beamer-style panel describing Python, aligned with the photo ─────
        panel = beamer_panel(
            "Python",
            items=[
                "Linguagem criada por Guido van Rossum",
                "Países Baixos, 1991",
                "Junção de Bash com C, porém mais legível",
                "Nome inspirado no Monty Python",
            ],
            font_size=26,
        )
        panel.move_to([2.7, photo.get_center()[1], 0])
        ts.play(FadeIn(panel))
        ts.wait(0.4)
        ts.next_slide()

        # ── Transition: "Mas desde então…" — line stays, marker slides to 2026 ─
        new_title = text("Mas desde então…", font_size=60, weight="BOLD").to_edge(UP, buff=0.4)
        year_2026 = text("2026", font_size=30, weight="BOLD", color=PY_BLUE)
        year_2026.next_to(np.array([TL_RIGHT, TL_Y, 0]), UP, buff=0.15)
        ts.play(
            FadeOut(photo), FadeOut(name), FadeOut(panel),
            FadeTransform(title, new_title),
            dot.animate.move_to([TL_RIGHT, TL_Y, 0]),
            FadeTransform(year, year_2026),
            run_time=1.6,
        )
        ts.next_slide()

        # ── Things you can do with Python — images only (voice-over) ─────────
        row = Group()
        for nm in DOMAIN_IMAGES:
            row.add(asset_image(nm, max_width=3.0, max_height=1.9))
        row.arrange(RIGHT, buff=0.5, aligned_edge=DOWN)
        if row.width > 13.5:
            row.scale_to_fit_width(13.5)
        row.move_to([0.0, 1.0, 0])
        ts.play(*[FadeIn(im, scale=0.85) for im in row], run_time=1.8)
        ts.next_slide()

        # ── At the end: the Manim logo, each part flying in from a side ──────
        logo = manim_logo().scale_to_fit_height(2.0).move_to([0.0, -1.55, 0])
        triangle, square, circle, ds_m = logo  # VGroup order = back-to-front z-order
        ts.play(
            # listed back-to-front so the assembled z-order is preserved;
            # each part still flies in from its own side.
            FadeIn(triangle, shift=LEFT * 3.0),   # from the right
            FadeIn(square, shift=DOWN * 3.0),     # from the top
            FadeIn(circle, shift=RIGHT * 3.0),    # from the left
            FadeIn(ds_m, shift=UP * 3.0),         # from the bottom
            run_time=1.4,
        )
        ts.wait(0.5)
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# Scene 2 — Estes slides são feitos em Python, com Manim
# ─────────────────────────────────────────────────────────────────────────────

MANIM_SNIPPET = [
    "from manim import *",
    "",
    "class Slide(Scene):",
    "    def construct(self):",
    '        titulo = Text("Python + Manim")',
    "        self.play(Write(titulo))",
]


class MadeWithManim(VisualSlide):
    def __init__(self):
        super().__init__(title="Feito em Python, com Manim", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)
        ts.play(Write(self.make_title()))
        ts.next_slide()

        # Manim logo: play the create/expand flourish at centre, then tuck it
        # to the left at a controlled size (expand() alone overflows the frame).
        banner = ManimBanner().scale(0.6)
        ts.play(banner.create())
        ts.play(banner.expand())
        ts.play(banner.animate.scale_to_fit_width(4.4).move_to([-3.8, -0.3, 0]))
        ts.next_slide()

        # The code that builds a slide, on the right.
        cb = code_block(MANIM_SNIPPET, font_size=22)
        code_group = VGroup(cb["box"], cb["code"])
        if code_group.width > 7.2:
            code_group.scale_to_fit_width(7.2)
        code_group.move_to([3.3, -0.3, 0])
        ts.play(Create(cb["box"]), Write(cb["code"]))
        ts.wait(0.5)
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# Scene 3 — Filosofia do Python  (verbose Java → morphs into short Python)
# ─────────────────────────────────────────────────────────────────────────────

JAVA_CODE = [
    "public class Main {",
    "    public static void main(String[] args) {",
    "        int[] nums = {1, 2, 3, 4, 5};",
    "        int total = 0;",
    "        for (int i = 0; i < nums.length; i++) {",
    "            total += nums[i];",
    "        }",
    "        System.out.println(\"Soma: \" + total);",
    "    }",
    "}",
]

PYTHON_CODE = [
    "nums = [1, 2, 3, 4, 5]",
    'print("Soma:", sum(nums))',
]


class PythonPhilosophy(VisualSlide):
    def __init__(self):
        super().__init__(title="Filosofia do Python", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)
        ts.play(Write(self.make_title()))
        ts.next_slide()

        # Dense, verbose Java block — fills most of the frame.
        java = code_block(JAVA_CODE, font_size=26)
        java_lang = text("Java", font_size=26, weight="BOLD", color="#b07219")
        java_group = VGroup(java["box"], java["code"], java_lang)
        java_lang.next_to(java["box"], UP, buff=0.2).align_to(java["box"], LEFT)
        java_group.move_to([0, -0.4, 0])
        ts.play(Create(java["box"]), Write(java["code"]), Write(java_lang))
        ts.wait(0.5)
        ts.next_slide()

        # Morph: the volume collapses into a couple of clean Python lines.
        py = code_block(PYTHON_CODE, font_size=30)
        py_lang = text("Python", font_size=26, weight="BOLD", color=PY_BLUE)
        py_group = VGroup(py["box"], py["code"], py_lang)
        py_lang.next_to(py["box"], UP, buff=0.2).align_to(py["box"], LEFT)
        py_group.move_to([0, -0.4, 0])
        ts.play(
            Transform(java["box"], py["box"]),
            ReplacementTransform(java["code"], py["code"]),
            Transform(java_lang, py_lang),
            run_time=2.0,
        )
        ts.wait(0.5)
        ts.next_slide()

        # The visual argument: same result, a fraction of the volume.
        caption = text("Mesmo resultado, uma fração do código",
                       font_size=28, weight="BOLD", color=PY_BLUE)
        caption.next_to(py["box"], DOWN, buff=0.5)
        ts.play(Write(caption))
        ts.wait(0.5)
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# Scene 4 — E quando precisamos de performance
# ─────────────────────────────────────────────────────────────────────────────

class PythonPerformance(VisualSlide):
    def __init__(self):
        super().__init__(title="E quando precisamos de performance?", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)
        ts.play(Write(self.make_title()))
        ts.next_slide()

        # Python at the centre.
        hub = labeled_box("Python", fill_color=PY_BLUE, stroke_color=PY_BLUE,
                          width=2.4, height=1.0, font_size=34)
        hub[1].set_color(PY_YELLOW)
        hub.move_to([0, 1.2, 0])
        ts.play(FadeIn(hub, scale=0.6))
        ts.next_slide()

        # Plugs to the compiled languages that provide the muscle.
        plugs, engine_group = VGroup(), VGroup()
        for label, x in [("C", -3.6), ("C++", 0.0), ("Rust", 3.6)]:
            box = labeled_box(label, fill_color="#f0e6d2", stroke_color="#a9761f",
                              width=1.7, height=0.85, font_size=28).move_to([x, -1.4, 0])
            plugs.add(Line(hub.get_bottom(), box.get_top(), color=BLACK, stroke_width=2.5))
            engine_group.add(box)
        ts.play(*[Create(p) for p in plugs],
                *[FadeIn(b, shift=UP * 0.3) for b in engine_group], run_time=1.8)
        ts.next_slide()

        # The compiled blocks slide behind well-known library "faces".
        lib_group = VGroup()
        for label, x in [("NumPy", -1.9), ("pandas", 1.9)]:
            lib_group.add(labeled_box(label, fill_color="#e8eef5", stroke_color=PY_BLUE,
                                      width=2.4, height=1.0, font_size=30).move_to([x, -1.4, 0]))
        ts.play(
            engine_group.animate.move_to([0, -1.5, 0]).scale(0.85).set_opacity(0.45),
            FadeOut(plugs),
            run_time=1.2,
        )
        lib_plugs = VGroup(
            *[Line(hub.get_bottom(), lib.get_top(), color=BLACK, stroke_width=2.5) for lib in lib_group]
        )
        ts.play(*[FadeIn(lib, shift=UP * 0.2) for lib in lib_group],
                *[Create(p) for p in lib_plugs], run_time=1.4)
        ts.next_slide()

        caption = text("Python é a superfície; C, C++ e Rust são o motor escondido",
                       font_size=26, weight="BOLD", color=PY_BLUE)
        if caption.width > 13:
            caption.scale_to_fit_width(13)
        caption.move_to([0, -3.3, 0])
        ts.play(Write(caption))
        ts.wait(0.5)
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# Public Scene classes — render order matches the screenplay
# ─────────────────────────────────────────────────────────────────────────────

class PyIntro_01_Timeline(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[PythonTimeline()], **kwargs)


class PyIntro_02_Manim(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[MadeWithManim()], **kwargs)


class PyIntro_03_Philosophy(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[PythonPhilosophy()], **kwargs)


class PyIntro_04_Performance(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[PythonPerformance()], **kwargs)

    def construct(self):
        # Last scene of the deck: end held on the final content instead of the
        # SlideShow's usual fade-to-blank (that empty final slide is why "the
        # last part of the performance did not appear"). self.wait() counts as
        # an animation for manim-slides, so the trailing pause stays valid.
        for slide in self.slides:
            slide.draw(origin=None, scale=1.0, target_scene=self, animate=True)
        self.wait(1)
