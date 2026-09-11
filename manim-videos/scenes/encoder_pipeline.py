"""What the policy actually reads.

Frames out of the environment, through a network, out as a vector of numbers,
into the policy. The vector is drawn as an array of cells because that is what
it is — a table of names and values is a different object and reads as one.

The frames morph into the array: the point is that the network *turns* the
image into those numbers, not that a box sits between them.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from manim import (ArrowTriangleFilledTip, Circle, FadeIn, FadeOut, ImageMobject,
                   Line, ManimColor, Rectangle, RoundedRectangle, Transform,
                   VGroup)
from manim_slides import Slide

from presenting_lib.chrome import DeckMeta, footer
from presenting_lib.slots import Slot
from presenting_lib.tokens import GEOMETRY, GROUND, PALETTE, STRUCTURE, TYPE

FOOTAGE = Path("/mnt/nas/MyPhotos/deepracer")
CLIP, FRAME_TIMES = "donut_t1.mp4", (2.5, 7.5, 12.5)

TITLE = "What the policy actually reads"
#: One entry per cell that gets named, in order. The rest of the vector stays
#: unlabelled on purpose: the beat is about what the numbers *are*, not a full
#: field list. The real list needs checking against the environment code.
CELL_LABELS = ("speed", "distance from the centre line", "heading error")
CELLS = 7
CLOSING = "the network is the part that has to survive the real world"

#: Three bands. The mechanism sits on top; what travels along each arrow is
#: shown under it; and the networks that get the *unrandomized* input sit at the
#: bottom. The asymmetry is the point: the actor reads randomized pixels, the
#: value and cost critics read the true state.
TOP_Y, MID_Y, BOT_Y = 1.70, -0.30, -2.05
#: The trunk that carries the unrandomized state, kept clear of the footer.
TRUNK_Y = -2.85
NET_X = -2.15
VEC_X, CELL_W, CELL_H = 2.35, 0.78, 0.58
NET_LAYERS = (4, 5, 3)

TITLE = "What the policy actually reads"
CELL_VALUES = ("1.24", "0.06", "3.1", "0.82", "0.19", "-0.4", "0.05")
CELL_LABELS = ("speed", "distance from the centre line", "heading error")
TRUE_LABEL = "true state, not randomized"


def _box(text, centre, width, height, accent=None):
    surface = PALETTE.surface(accent) if accent else STRUCTURE
    rect = RoundedRectangle(
        width=width, height=height, corner_radius=GEOMETRY.corner_radius,
        color=surface.stroke or PALETTE.structure_stroke,
        fill_color=surface.fill or PALETTE.structure_fill, fill_opacity=1.0,
        stroke_width=GEOMETRY.stroke_weight * 0.7).move_to(centre)
    label = Slot(f"b{text[:6]}", centre[0], centre[1], width * 0.86, height * 0.58,
                 style="body").fit_text(text, style="body", on=surface)
    return VGroup(rect, label)


def _path(points, colour=None, weight=0.85, tip=True):
    colour = colour or PALETTE.structure_stroke
    group = VGroup()
    for a, b in zip(points, points[1:]):
        group.add(Line([*a, 0], [*b, 0], color=colour,
                       stroke_width=GEOMETRY.stroke_weight * weight))
    if tip:
        end = np.array([*points[-1], 0.0])
        direction = end - np.array([*points[-2], 0.0])
        head = ArrowTriangleFilledTip(color=colour, length=0.14)
        head.rotate(np.arctan2(direction[1], direction[0]) - head.tip_angle)
        head.move_to(end - direction / np.linalg.norm(direction) * 0.07)
        group.add(head)
    return group


def _tag(text, x, y, width=2.6, style="caption"):
    return Slot(f"t{text[:6]}{x:.1f}", x, y, width, 0.42, style=style).fit_text(
        text, style=style, on=GROUND)


def _net(centre_x, y):
    colour = PALETTE.structure_stroke
    columns = []
    for index, count in enumerate(NET_LAYERS):
        x = centre_x + (index - 1) * 0.95
        columns.append([np.array([x, y + (i - (count - 1) / 2) * 0.48, 0.0])
                        for i in range(count)])
    edges = VGroup()
    for left, right in zip(columns, columns[1:]):
        for a in left:
            for b in right:
                edges.add(Line(a, b, color=colour, stroke_width=1.0,
                               stroke_opacity=0.45))
    nodes = VGroup()
    for column in columns:
        for point in column:
            nodes.add(Circle(radius=0.13, color=colour,
                             fill_color=PALETTE.structure_fill, fill_opacity=1.0,
                             stroke_width=GEOMETRY.stroke_weight * 0.5).move_to(point))
    return VGroup(edges, nodes)


def _array():
    group = VGroup()
    left = VEC_X - len(CELL_VALUES) * CELL_W / 2
    for index, value in enumerate(CELL_VALUES):
        x = left + CELL_W * (index + 0.5)
        group.add(Rectangle(
            width=CELL_W, height=CELL_H, color=PALETTE.green.mid,
            fill_color=PALETTE.green.tint, fill_opacity=1.0,
            stroke_width=GEOMETRY.stroke_weight * 0.6).move_to([x, MID_Y, 0]))
        group.add(Slot(f"v{index}", x, MID_Y, CELL_W * 0.82, CELL_H * 0.6,
                       style="caption").fit_text(
                           value, style="caption", on=PALETTE.surface("green")))
    return group


def cell_x(index):
    return VEC_X - len(CELL_VALUES) * CELL_W / 2 + CELL_W * (index + 0.5)


class EncoderPipeline(Slide):
    """The asymmetric loop: randomized pixels to the actor, true state to the
    value and cost critics."""

    section_name = ""
    slide_number = 1
    deck_sections: tuple = ()

    def _frames(self):
        import av
        from PIL import Image

        out = []
        with av.open(str(FOOTAGE / CLIP)) as container:
            stream = container.streams.video[0]
            stream.thread_type = "AUTO"
            wanted = list(FRAME_TIMES)
            for frame in container.decode(stream):
                if not wanted:
                    break
                if float(frame.pts * stream.time_base) < wanted[0]:
                    continue
                wanted.pop(0)
                img = frame.to_ndarray(format="rgb24")
                h, w = img.shape[:2]
                out.append(np.asarray(
                    Image.fromarray(img).resize((280, round(h * 280 / w)))))
        return out

    def construct(self):
        self.camera.background_color = ManimColor(PALETTE.ground)
        self.camera.init_background()
        if self.deck_sections:
            self.add(footer(DeckMeta(sections=list(self.deck_sections)),
                            self.section_name, self.slide_number))
        self.add(Slot("title", 0.0, 3.05, 11.0, 0.8, style="title").fit_text(
            TITLE, style="title", on=GROUND, weight="BOLD"))

        green = PALETTE.green.mid
        env = _box("env", [-6.05, TOP_Y, 0], 1.5, 0.95)
        net = _net(NET_X, TOP_Y)
        actor = _box("actor", [5.85, TOP_Y, 0], 1.7, 0.95)
        a1 = _path([(-5.30, TOP_Y), (-3.35, TOP_Y)])
        a2 = _path([(-0.95, TOP_Y), (4.95, TOP_Y)])
        o_t = Slot("o_t", -4.35, TOP_Y + 0.36, 1.0, 0.44).fit_math(
            "O_t", on=GROUND)
        self.play(FadeIn(VGroup(env, net, actor, a1, a2, o_t), run_time=0.5))
        self.wait(0.4)
        self.next_slide()

        images = []
        for index, frame in enumerate(self._frames()):
            img = ImageMobject(frame).scale_to_fit_width(1.95)
            img.move_to([-4.75 + index * 0.20, MID_Y + 0.28 - index * 0.28, 0])
            images.append(img)
        self.play(Transform(a1, _path([(-5.30, TOP_Y), (-3.35, TOP_Y)], green, 1.5)),
                  *[FadeIn(i) for i in images], run_time=0.6)
        self.wait(0.4)
        self.next_slide()

        vector = _array()
        self.play(Transform(a2, _path([(-0.95, TOP_Y), (4.95, TOP_Y)], green, 1.5)),
                  FadeIn(vector), run_time=0.7)
        self.wait(0.4)
        self.next_slide()

        shown = None
        for index, name in enumerate(CELL_LABELS):
            ring = Rectangle(width=CELL_W, height=CELL_H, color=PALETTE.green.dark,
                             stroke_width=GEOMETRY.stroke_weight * 1.4,
                             fill_opacity=0.0).move_to([cell_x(index), MID_Y, 0])
            tag = _tag(name, VEC_X, MID_Y - 0.78, 5.6, "body")
            steps = [FadeIn(ring), FadeIn(tag)]
            if shown is not None:
                steps.append(FadeOut(shown, run_time=0.25))
            self.play(*steps, run_time=0.5)
            shown = VGroup(ring, tag)
            self.wait(0.4)
            self.next_slide()


SIM_VEC_X = -2.00
SIM_TOP_Y, SIM_BOT_Y, SIM_TRUNK_Y = 1.35, -2.20, -0.85
NO_RANDOM = "no randomization"


class SimPipeline(Slide):
    """In simulation the environment hands over the vector directly.

    The slide before the real-world one, so the two can be told apart: no
    camera, no encoder, and the randomization sits between the vector and the
    actor. The value and cost critics read the same vector with the
    randomization skipped, which is the asymmetry.
    """

    section_name = ""
    slide_number = 1
    deck_sections: tuple = ()

    def construct(self):
        self.camera.background_color = ManimColor(PALETTE.ground)
        self.camera.init_background()
        if self.deck_sections:
            self.add(footer(DeckMeta(sections=list(self.deck_sections)),
                            self.section_name, self.slide_number))
        self.add(Slot("stitle", 0.0, 3.05, 11.0, 0.8, style="title").fit_text(
            "In simulation", style="title", on=GROUND, weight="BOLD"))

        green = PALETTE.green.mid
        env = _box("env", [-6.35, SIM_TOP_Y, 0], 1.5, 0.95)
        cells = VGroup()
        left = SIM_VEC_X - len(CELL_VALUES) * CELL_W / 2
        for index, value in enumerate(CELL_VALUES):
            x = left + CELL_W * (index + 0.5)
            cells.add(Rectangle(
                width=CELL_W, height=CELL_H, color=PALETTE.green.mid,
                fill_color=PALETTE.green.tint, fill_opacity=1.0,
                stroke_width=GEOMETRY.stroke_weight * 0.6).move_to([x, SIM_TOP_Y, 0]))
            cells.add(Slot(f"sv{index}", x, SIM_TOP_Y, CELL_W * 0.82, CELL_H * 0.6,
                           style="caption").fit_text(
                               value, style="caption", on=PALETTE.surface("green")))
        self.play(FadeIn(VGroup(env, _path([(-5.55, SIM_TOP_Y), (-4.80, SIM_TOP_Y)]),
                                cells), run_time=0.5))
        self.wait(0.4)
        self.next_slide()

        rnd = _box("randomization", [2.95, SIM_TOP_Y, 0], 2.8, 0.95, accent="green")
        actor = _box("actor", [6.10, SIM_TOP_Y, 0], 1.7, 0.95)
        self.play(FadeIn(_path([(0.85, SIM_TOP_Y), (1.50, SIM_TOP_Y)], green, 1.4)),
                  FadeIn(rnd),
                  FadeIn(_path([(4.40, SIM_TOP_Y), (5.20, SIM_TOP_Y)], green, 1.4)),
                  FadeIn(actor), run_time=0.6)
        self.wait(0.4)
        self.next_slide()

        value = _box("value network", [-1.15, SIM_BOT_Y, 0], 3.0, 0.95)
        critic = _box("cost critic", [2.75, SIM_BOT_Y, 0], 2.9, 0.95, accent="green")
        trunk = _path([(SIM_VEC_X, SIM_TOP_Y - 0.30), (SIM_VEC_X, SIM_TRUNK_Y),
                       (2.75, SIM_TRUNK_Y)], tip=False)
        stubs = VGroup(_path([(-1.15, SIM_TRUNK_Y), (-1.15, SIM_BOT_Y + 0.50)]),
                       _path([(2.75, SIM_TRUNK_Y), (2.75, SIM_BOT_Y + 0.50)]))
        tag = _tag(NO_RANDOM, 0.60, SIM_TRUNK_Y + 0.36, 2.9)
        self.play(FadeIn(trunk), FadeIn(tag), FadeIn(stubs),
                  FadeIn(value), FadeIn(critic), run_time=0.7)
        self.wait(0.4)
        self.next_slide()
