"""O que é Python? — intro deck.

Built from screenplays/python_into.md. Scenes:
    PyIntro_01_Timeline    "O que é Python?" → "Mas desde então…" (one continuous
                           timeline; domains shown as icons around a Python hub)
    PyIntro_02_Manim       "these slides are made with Python + Manim" (logo + code)
    PyIntro_03_Philosophy  verbose Java morphs into short Python
    PyIntro_04_Performance Python → C/C++/Rust hidden behind NumPy/pandas
    PyIntro_05_Basics      variables & if/else — verbose C vs clean Python
    PyIntro_06_CommandLine the command line — python <arquivo>, pip install <pacote>
    PyIntro_07_Venv        virtual environments — install packages, contained
    PyIntro_08_Jupyter     notebooks — stacked cells share one kernel (state)
    PyIntro_09_Pause       divider — "Botando a mão na massa"
    PyIntro_10_DataStructures list / tuple / set / dict, with tiny examples

The first two H1s of the screenplay share one scene so the timeline line is a
single persistent mobject — it never fades between 1991 and 2026, only the year
marker slides across it.

Per the screenplay's direction, NO spoken narration ("Fala") is placed on the
slides — only the visuals and the on-screen text called for by each
"Visual"/"Texto" note.

Domain images live in scenes/assets/ (deepracer/datavis/LLM/webdev + guido.jpg);
a labelled placeholder shows if one is missing.

Render & present (PyIntro_10_DataStructures is the last scene — it holds on its
final content instead of fading to blank):
    uv run manim-slides render scenes/python_intro.py \\
        PyIntro_01_Timeline PyIntro_02_Manim PyIntro_03_Philosophy PyIntro_04_Performance \\
        PyIntro_05_Basics PyIntro_06_CommandLine PyIntro_07_Venv PyIntro_08_Jupyter \\
        PyIntro_09_Pause PyIntro_10_DataStructures \\
        -q h --disable_caching
    uv run manim-slides present \\
        PyIntro_01_Timeline PyIntro_02_Manim PyIntro_03_Philosophy PyIntro_04_Performance \\
        PyIntro_05_Basics PyIntro_06_CommandLine PyIntro_07_Venv PyIntro_08_Jupyter \\
        PyIntro_09_Pause PyIntro_10_DataStructures

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
    Arrow,
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
    SurroundingRectangle,
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


def code_block(lines, font_size: int, width: float = None, align: str = "center",
               fill: str = "#f6f8fa", stroke: str = "#cccccc"):
    """A monospace code panel (sharp rectangle). Single multi-line Text so Pango
    keeps the indentation (per-line VGroups would left-snap and lose it).

    ``width`` forces a fixed panel width (else it hugs the code); ``align='left'``
    left-justifies the code inside the panel (for terminal / notebook cells).
    """
    code = Text("\n".join(lines), font=MONO, color=BLACK, font_size=font_size, line_spacing=0.6)
    w = code.width + 0.9 if width is None else width
    box = Rectangle(width=w, height=code.height + 0.7, color=stroke,
                    fill_color=fill, fill_opacity=1.0, stroke_width=2)
    if align == "left":
        code.align_to(box, LEFT).shift(RIGHT * 0.45)
        code.set_y(box.get_center()[1])
    else:
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
# Scene 5 — O básico de Python (variáveis e condicionais)
# ─────────────────────────────────────────────────────────────────────────────

C_BASICS = [
    "#include <stdio.h>",
    "",
    "int main() {",
    '    char nome[] = "Ana";',
    "    int idade = 20;",
    "    if (idade >= 18) {",
    '        printf("maior de idade");',
    "    } else {",
    '        printf("menor de idade");',
    "    }",
    "    return 0;",
    "}",
]

PY_BASICS = [
    'nome = "Ana"',
    "idade = 20",
    "if idade >= 18:",
    '    print("maior de idade")',
    "else:",
    '    print("menor de idade")',
]

C_COLOR = "#5c6bc0"


class PythonBasicsSlide(VisualSlide):
    def __init__(self):
        super().__init__(title="O básico de Python", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)
        ts.play(Write(self.make_title()))
        ts.next_slide()

        # Same tiny program (variables + if/else) — verbose C vs clean Python.
        c = code_block(C_BASICS, font_size=18, align="left")
        c_lbl = text("C", font_size=24, weight="BOLD", color=C_COLOR)
        c_group = VGroup(c_lbl, c["box"], c["code"])
        c_lbl.next_to(c["box"], UP, buff=0.15).align_to(c["box"], LEFT)
        c_group.move_to([-3.6, -0.35, 0])
        ts.play(Create(c["box"]), Write(c["code"]), Write(c_lbl))
        ts.next_slide()

        py = code_block(PY_BASICS, font_size=22, align="left")
        py_lbl = text("Python", font_size=24, weight="BOLD", color=PY_BLUE)
        py_group = VGroup(py_lbl, py["box"], py["code"])
        py_lbl.next_to(py["box"], UP, buff=0.15).align_to(py["box"], LEFT)
        py_group.move_to([3.6, 0, 0])
        # align the Python panel's top with the C panel's top
        py_group.shift(UP * (c["box"].get_top()[1] - py["box"].get_top()[1]))
        ts.play(Create(py["box"]), Write(py["code"]), Write(py_lbl))
        ts.next_slide()

        caption = text("Sem tipos, sem chaves, sem ponto e vírgula — a indentação define os blocos",
                       font_size=24, weight="BOLD", color=PY_BLUE)
        if caption.width > 13.5:
            caption.scale_to_fit_width(13.5)
        caption.move_to([0, -3.5, 0])
        ts.play(Write(caption))
        ts.wait(0.5)
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# Scene 6 — A linha de comando (python <arquivo>, pip install <pacote>)
# ─────────────────────────────────────────────────────────────────────────────

class CommandLineSlide(VisualSlide):
    def __init__(self):
        super().__init__(title="A linha de comando", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)
        ts.play(Write(self.make_title()))
        ts.next_slide()

        # Two commands, each with an arrow to its explanation.
        rows = [
            ("$ python <arquivo>.py", "Executa um arquivo Python"),
            ("$ pip install <pacote>", "Instala um pacote (do PyPI)"),
        ]
        for (cmd, expl), y in zip(rows, [0.9, -0.9]):
            cb = code_block([cmd], font_size=24, align="left")
            cmd_group = VGroup(cb["box"], cb["code"]).move_to([-3.3, y, 0])
            over = -6.6 - cmd_group.get_left()[0]
            if over > 0:
                cmd_group.shift(RIGHT * over)
            expl_t = text(expl, font_size=26, weight="BOLD", color=PY_BLUE).move_to([3.3, y, 0])
            arrow = Arrow(cmd_group.get_right(), expl_t.get_left(), buff=0.35,
                          color=BLACK, stroke_width=3, max_tip_length_to_length_ratio=0.18)
            ts.play(Create(cb["box"]), Write(cb["code"]))
            ts.play(Create(arrow), Write(expl_t))
            ts.next_slide()

        caption = text("Os dois comandos que você mais vai usar",
                       font_size=26, weight="BOLD", color=PY_BLUE)
        if caption.width > 13:
            caption.scale_to_fit_width(13)
        caption.move_to([0, -2.9, 0])
        ts.play(Write(caption))
        ts.wait(0.5)
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# Scene 7 — Ambientes virtuais (venv)
# ─────────────────────────────────────────────────────────────────────────────

class VenvSlide(VisualSlide):
    def __init__(self):
        super().__init__(title="Ambientes virtuais (venv)", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)
        ts.play(Write(self.make_title()))
        ts.next_slide()

        # Terminal commands on the left (kept inside the left frame edge).
        term = code_block(
            [
                "$ python -m venv .venv",
                "$ source .venv/bin/activate",
                "(.venv) $ pip install numpy pandas",
            ],
            font_size=20, align="left",
        )
        term_lbl = text("Terminal", font_size=22, weight="BOLD", color=PY_BLUE)
        term_group = VGroup(term_lbl, term["box"], term["code"])
        term_lbl.next_to(term["box"], UP, buff=0.15).align_to(term["box"], LEFT)
        term_group.move_to([-3.5, 0.3, 0])
        left_over = -6.7 - term_group.get_left()[0]
        if left_over > 0:
            term_group.shift(RIGHT * left_over)
        ts.play(Create(term["box"]), Write(term["code"]), Write(term_lbl))
        ts.next_slide()

        # The contained environment on the right — box auto-sized to its content.
        venv_lbl = text(".venv", font_size=26, weight="BOLD", color=PY_BLUE)
        pkgs = VGroup(*[
            labeled_box(p, fill_color="#e8eef5", stroke_color=PY_BLUE,
                        width=2.4, height=0.6, font_size=22)
            for p in ["numpy", "pandas", "requests"]
        ]).arrange(DOWN, buff=0.22)
        inner = VGroup(venv_lbl, pkgs).arrange(DOWN, buff=0.3)
        inner.move_to([3.5, 0.25, 0])
        container = SurroundingRectangle(
            inner, color=PY_BLUE, fill_color="#eef3f8", fill_opacity=1.0,
            buff=0.4, stroke_width=3, corner_radius=0.0,
        ).set_z_index(-1)
        ts.play(Create(container), Write(venv_lbl))
        ts.next_slide()

        # Packages land inside the box (installed into the environment).
        ts.play(*[FadeIn(p, shift=UP * 0.2) for p in pkgs], run_time=1.2)
        ts.next_slide()

        caption = text("Pacotes ficam contidos no ambiente — isolados do sistema",
                       font_size=26, weight="BOLD", color=PY_BLUE)
        if caption.width > 13:
            caption.scale_to_fit_width(13)
        caption.move_to([0, -3.2, 0])
        ts.play(Write(caption))
        ts.wait(0.5)
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# Scene 8 — Jupyter Notebooks (stacked cells share one kernel)
# ─────────────────────────────────────────────────────────────────────────────

JUPYTER_RED = "#e07a5f"


class JupyterSlide(VisualSlide):
    def __init__(self):
        super().__init__(title="Jupyter Notebooks", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)
        ts.play(Write(self.make_title()))
        ts.next_slide()

        # Stacked cells — a document made of code blocks.
        cell_w = 4.6
        cells_src = [(1, ["x = 10"]), (2, ["y = x * 2"]), (3, ["print(x, y)   # 10 20"])]
        cells = VGroup()
        for n, lines in cells_src:
            cb = code_block(lines, font_size=24, width=cell_w, align="left")
            prompt = text(f"In [{n}]:", font_size=20, weight="BOLD", color=PY_BLUE, font=MONO)
            prompt.next_to(cb["box"], LEFT, buff=0.2)
            cells.add(VGroup(prompt, cb["box"], cb["code"]))
        cells.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        cells.move_to([-0.9, 0.25, 0])
        for cell in cells:
            ts.play(FadeIn(cell, shift=UP * 0.2), run_time=0.5)
        ts.next_slide()

        # One kernel spine on the left, connected to every cell → shared state.
        spine_x = cells.get_left()[0] - 0.7
        spine = Line([spine_x, cells.get_top()[1], 0], [spine_x, cells.get_bottom()[1], 0],
                     color=JUPYTER_RED, stroke_width=5)
        connectors = VGroup(*[
            Line([spine_x, c.get_center()[1], 0], [c.get_left()[0], c.get_center()[1], 0],
                 color=JUPYTER_RED, stroke_width=2)
            for c in cells
        ])
        kernel_lbl = text("Kernel", font_size=24, weight="BOLD", color=JUPYTER_RED)
        kernel_lbl.next_to(spine, LEFT, buff=0.25)
        ts.play(Create(spine), *[Create(c) for c in connectors], Write(kernel_lbl))
        ts.next_slide()

        # What the notebook is, on the right.
        notes = VGroup(
            text("Documento + ambiente Python", font_size=24, weight="BOLD"),
            text("1 kernel por servidor", font_size=22),
            text("e por documento", font_size=22),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        notes.move_to([4.4, 0.6, 0])
        ts.play(*[FadeIn(line, shift=RIGHT * 0.2) for line in notes], run_time=1.0)
        ts.next_slide()

        caption = text("O que roda em uma célula afeta as outras (estado compartilhado)",
                       font_size=26, weight="BOLD", color=JUPYTER_RED)
        if caption.width > 13:
            caption.scale_to_fit_width(13)
        caption.move_to([0, -3.2, 0])
        ts.play(Write(caption))
        ts.wait(0.5)
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# Scene 9 — Pause / section divider
# ─────────────────────────────────────────────────────────────────────────────

class PauseSlide(VisualSlide):
    def __init__(self):
        super().__init__(title="Botando a mão na massa", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)

        phrase = text("Botando a mão na massa", font_size=64, weight="BOLD")
        if phrase.width > 12.5:
            phrase.scale_to_fit_width(12.5)
        phrase.move_to([0, 0.25, 0])
        underline = Line(phrase.get_left(), phrase.get_right(),
                         color=PY_BLUE, stroke_width=5)
        underline.next_to(phrase, DOWN, buff=0.3)
        ts.play(Write(phrase))
        ts.play(Create(underline))
        ts.wait(0.5)
        ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# Scene 10 — Estruturas de dados (list / tuple / set / dict)
# ─────────────────────────────────────────────────────────────────────────────

class DataStructuresSlide(VisualSlide):
    def __init__(self):
        super().__init__(title="Estruturas de dados", subtitle=None)

    def draw(self, origin=None, scale=1.0, target_scene=None, animate=True):
        ts = target_scene if target_scene is not None else self
        self.reset_camera(ts)
        ts.play(Write(self.make_title()))
        ts.next_slide()

        # 2×2 grid: type + one-line property, with a tiny example.
        # Columns are anchored by their LEFT edge so the widest box stays on-screen.
        left_x, right_x = -6.3, 0.7
        specs = [
            ("list — ordenada, mutável", 'frutas = ["maçã", "banana"]', left_x, 1.5),
            ("tuple — ordenada, imutável", "ponto = (10, 20)", right_x, 1.5),
            ("set — sem ordem, únicos", "ids = {1, 2, 3}", left_x, -1.6),
            ("dict — chave → valor", 'pessoa = {"nome": "Ana"}', right_x, -1.6),
        ]
        for label, code_line, x_left, y in specs:
            cb = code_block([code_line], font_size=20, align="left")  # hug content
            lbl = text(label, font_size=22, weight="BOLD", color=PY_BLUE)
            cell = VGroup(lbl, cb["box"], cb["code"])
            lbl.next_to(cb["box"], UP, buff=0.12).align_to(cb["box"], LEFT)
            cell.move_to([0, y, 0])
            cell.shift(RIGHT * (x_left - cb["box"].get_left()[0]))  # anchor box left edge
            ts.play(Create(cb["box"]), Write(cb["code"]), Write(lbl))
            ts.next_slide()


# ─────────────────────────────────────────────────────────────────────────────
# Public Scene classes — render order matches the screenplay
# ─────────────────────────────────────────────────────────────────────────────

class EndHeldSlideShow(SlideShow):
    """A SlideShow that ends held on its final content instead of the default
    fade-to-blank — use it for the LAST scene of the deck so nothing vanishes."""

    def construct(self):
        for slide in self.slides:
            slide.draw(origin=None, scale=1.0, target_scene=self, animate=True)
        self.wait(1)  # counts as an animation, so the trailing pause stays valid


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


class PyIntro_05_Basics(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[PythonBasicsSlide()], **kwargs)


class PyIntro_06_CommandLine(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[CommandLineSlide()], **kwargs)


class PyIntro_07_Venv(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[VenvSlide()], **kwargs)


class PyIntro_08_Jupyter(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[JupyterSlide()], **kwargs)


class PyIntro_09_Pause(SlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[PauseSlide()], **kwargs)


class PyIntro_10_DataStructures(EndHeldSlideShow):
    def __init__(self, **kwargs):
        super().__init__(slides=[DataStructuresSlide()], **kwargs)
