"""The canonical RL loop, hand-composed.

Graphviz routes with splines and puts edge labels in the middle of the arc. The
figure this deck returns to is the Sutton & Barto one: orthogonal right-angle
routing, the action down the right-hand side, the returns coming back up the
left in nested lanes with their labels outside the loop, and a dashed line
marking the timestep boundary. None of that is a graph layout problem, so this
draws it directly.

A beat asks for it through the generic `builder` hook:

    visual:
      kind: constructible
      sub: geometry
      builder: scenes.rl_loop:loop
      args: {cost: true, accent: c}

Everything comes from the identity tokens, so it sits on the deck like any
catalog layout.
"""

from __future__ import annotations

import numpy as np
from manim import (ArrowTriangleFilledTip, Create, DashedLine, FadeIn, FadeOut,
                   LEFT, RIGHT,
                   Line, ManimColor, MathTex, Rectangle, RoundedRectangle,
                   Transform, TransformMatchingTex, VGroup)
from manim_slides import Slide

from presenting_lib.chrome import DeckMeta, footer
from presenting_lib.slots import Slot
from presenting_lib.tokens import GEOMETRY, GROUND, PALETTE, STRUCTURE, TYPE

# ── canonical geometry, in its own units; scaled into the slot at the end ────
AGENT = (1.6, 1.7, 3.2, 1.25)          # cx, cy, w, h
ENV = (1.6, -1.7, 4.0, 1.25)
ACTION_X = 5.2                          # the action lane, down the right
LANES = {"r": -1.6, "O": -4.0, "c": -6.4}   # return lanes, inner to outer
EXIT_Y = {"r": 0.42, "O": 0.0, "c": -0.42}   # leaving the environment
ENTRY_Y = {"r": -0.42, "O": 0.0, "c": 0.42}  # arriving at the agent
DASH_X = -0.75
#: Small. The default triangle reads as a wedge at this figure's scale.
TIP_LENGTH = 0.10
LABEL_W, LABEL_H = 1.9, 0.9


def _surface(accent):
    return PALETTE.surface(accent) if accent else STRUCTURE


def _box(spec, label, accent=None):
    cx, cy, w, h = spec
    surface = _surface(accent)
    rect = RoundedRectangle(
        width=w, height=h, corner_radius=GEOMETRY.corner_radius,
        color=surface.stroke or PALETTE.structure_stroke,
        fill_color=surface.fill or PALETTE.structure_fill,
        fill_opacity=1.0, stroke_width=GEOMETRY.stroke_weight * 0.7,
    ).move_to([cx, cy, 0])
    text = Slot(f"box_{label}", cx, cy, w * 0.86, h * 0.7,
                style="body").fit_text(label, style="body", on=surface)
    return VGroup(rect, text)


def _polyline(points, colour, *, tip=True, width=None):
    """Right-angle path through `points`, arrowhead on the last segment."""
    group = VGroup()
    stroke = width or GEOMETRY.stroke_weight * 0.85
    for a, b in zip(points, points[1:]):
        group.add(Line([*a, 0], [*b, 0], color=colour, stroke_width=stroke))
    if tip:
        end = np.array([*points[-1], 0.0])
        direction = end - np.array([*points[-2], 0.0])
        norm = float(np.linalg.norm(direction))
        if norm > 1e-9:
            head = ArrowTriangleFilledTip(color=colour, length=TIP_LENGTH)
            head.rotate(np.arctan2(direction[1], direction[0]) - head.tip_angle)
            head.move_to(end - direction / norm * head.length / 2)
            group.add(head)
    return group


def _label(word, tex, x, y, accent=None):
    """The channel's name over its symbol. The symbol is real math — `A_t` set
    as text renders a literal underscore, which is what it was doing."""
    surface = _surface(accent) if accent else GROUND
    anchor = x + LABEL_W / 2
    name = Slot(f"lane_{word[:6]}", anchor, y + 0.26, LABEL_W, 0.42,
                style="body", align="left").fit_text(word, style="body", on=surface)
    # A tight box, or `fit_math` grows the symbol until it dwarfs its own word.
    symbol = Slot(f"sym_{word[:6]}", anchor - LABEL_W * 0.28, y - 0.26, 0.8, 0.42,
                  style="body", align="left").fit_math(tex, on=surface)
    return VGroup(name, symbol)


def _tuple(parts, highlight, slot):
    """The tuple, with named parts able to carry the accent.

    Green ink is not permitted on the ground by this identity, so a marked
    symbol gets the accent's own tint behind it and the accent's dark on top —
    the same pairing the annotation boxes use.
    """
    accent = PALETTE.green
    mob = MathTex(*parts, font_size=TYPE.size("claim"), color=PALETTE.ink)
    mob.scale(min(slot.w / mob.width, slot.h / mob.height, 2.4))
    mob.move_to(slot.center)

    group = VGroup()
    for index in highlight:
        piece = mob[index]
        group.add(RoundedRectangle(
            width=piece.width + 0.22, height=piece.height + 0.26,
            corner_radius=0.07, stroke_width=0,
            fill_color=accent.tint, fill_opacity=1.0).move_to(piece.get_center()))
        # `mid`, not `dark`: dark green on the tint reads as black text in a
        # green box, and the point is that the symbol itself is marked.
        piece.set_color(accent.mid)
    group.add(mob)
    # A scene that wants to draw only what is new needs these by name.
    group.tex_mob = mob
    group.boxes = VGroup(*group.submobjects[:len(highlight)])
    return group


def _note(tex, text, x, y, highlight=(), title=None):
    """The beat's own annotation, drawn on the canvas rather than in a title.

    The pieces are named on the way out, so a scene can draw only what is new
    instead of morphing the whole annotation.
    """
    group = VGroup()
    tuple_group = caption = None
    if title:
        group.add(Slot("note_title", x, y + 0.46, 11.0, 0.85,
                       style="title").fit_text(title, style="title", on=GROUND,
                                               weight="BOLD"))
    if tex:
        parts = tex if isinstance(tex, (list, tuple)) else [tex]
        tuple_group = _tuple(parts, highlight,
                             Slot("note_tex", x, y + 0.46, 7.5, 1.15))
        group.add(tuple_group)
    if text:
        drop = -0.62 if tex else (-0.5 if title else 0.0)
        caption = Slot("note_txt", x, y + drop, 11.0, 0.7,
                       style="body").fit_text(text, style="body", on=GROUND)
        group.add(caption)
    group.tuple_group = tuple_group
    group.caption = caption
    return group


def loop(*, cost: bool = False, reward: bool = True,
         accent: str | None = None,
         insert: tuple[str, str] | None = None, timestep: bool = True,
         note: tuple[object, str] | None = None,
         highlight: tuple[int, ...] = (), split: bool = False,
         title: str | None = None, feedback: bool = False):
    """Build the figure. Returns the `builder(slot)` the layouts expect.

    `accent` marks one channel — "A", "O", "r", "c" — or "env"/"agent" for a box.
    `insert` puts a labelled box on a channel, e.g. ("O", "encoder"), which is
    how the solve pass says "an encoder in front of the agent".
    """
    channels = (["r"] if reward else []) + ["O"] + (["c"] if cost else [])

    def build(slot: Slot):
        ink = PALETTE.structure_stroke
        green = PALETTE.green.mid
        parts = VGroup()
        lane_refs: list = []          # the cost lane, for scenes that draw it in
        reward_refs: list = []        # the reward channel, absent on real hardware
        insert_ref: list = []         # the box sitting on a channel
        channel_refs: dict = {}       # per-channel pieces, for recolouring
        frame_refs: dict = {}         # the two boxes

        agent_box = _box(AGENT, "AGENT", "green" if accent == "agent" else None)
        env_box = _box(ENV, "ENV", "green" if accent == "env" else None)
        parts.add(agent_box, env_box)
        frame_refs["agent"], frame_refs["env"] = agent_box, env_box

        acx, acy, aw, ah = AGENT
        ecx, ecy, ew, eh = ENV
        agent_r, env_r = acx + aw / 2, ecx + ew / 2
        agent_l, env_l = acx - aw / 2, ecx - ew / 2

        # action: out of the agent, down the right, into the environment
        a_marked = accent == "A"
        parts.add(_polyline([(agent_r, acy), (ACTION_X, acy),
                             (ACTION_X, ecy), (env_r, ecy)],
                            green if a_marked else ink,
                            width=GEOMETRY.stroke_weight * (1.5 if a_marked else 0.85)))
        action_tag = _label("action", "A_t", ACTION_X + 0.3, 0.0,
                            "green" if a_marked else None)
        parts.add(action_tag)
        channel_refs["A"] = VGroup(parts[-2], action_tag)

        if timestep:
            parts.add(DashedLine([DASH_X, ecy + eh, 0], [DASH_X, ecy - eh, 0],
                                 color=PALETTE.muted, stroke_width=2,
                                 dash_length=0.12))

        names = {"r": ("reward", "r_t"), "O": ("observation", "O_t"),
                 "c": ("cost", "c_t")}
        stagger = {"r": 0.62, "O": -0.28, "c": -1.18}
        for key in channels:
            lane = LANES[key]
            out_y, in_y = ecy + EXIT_Y[key], acy + ENTRY_Y[key]
            marked = accent == key
            col = green if marked else ink
            pts = [(env_l, out_y), (lane, out_y), (lane, in_y), (agent_l, in_y)]
            # Weight as well as hue: the palette's mid green is dark, and on sand
            # a marked line reads better heavier than it does recoloured alone.
            line = _polyline(pts, col,
                             width=GEOMETRY.stroke_weight * (1.5 if marked else 0.85))
            parts.add(line)
            _keys = ([e[0] for e in insert]
                     if insert is not None and isinstance(insert[0], (list, tuple))
                     else [insert[0]] if insert is not None else [])
            if key not in _keys:
                word, tex = names[key]
                tag = _label(word, tex, lane + 0.28, stagger[key],
                             "green" if marked else None)
                parts.add(tag)
            else:
                tag = None
            channel_refs[key] = VGroup(*[m for m in (line, tag) if m is not None])
            bucket = lane_refs if key == "c" else reward_refs if key == "r" else None
            if bucket is not None:
                bucket.append(line)
                if tag is not None:
                    bucket.append(tag)

        if not cost:
            parts.add(Rectangle(width=0.01, height=0.01, stroke_width=0,
                                fill_opacity=0.0).move_to(
                                    [LANES["c"] - LABEL_W * 0.1, 0.0, 0]))

        if insert is not None:
            entries = insert if isinstance(insert[0], (list, tuple)) else [insert]
            for key, text in entries:
                lane = LANES[key] if key in LANES else ACTION_X
                where = stagger.get(key, 0.0) if key in LANES else 0.0
                box = _box((lane, where, 2.6, 0.95), text, "green")
                insert_ref.append((key, box))
                parts.add(box)
                if feedback and key == "A":
                    # Around the outside and into the top of the agent, rather
                    # than cutting back inside the action lane.
                    top = acy + AGENT[3] / 2
                    parts.add(_polyline(
                        [(lane + 1.3, where), (lane + 1.75, where),
                         (lane + 1.75, top + 0.85), (acx, top + 0.85),
                         (acx, top)], green,
                        width=GEOMETRY.stroke_weight * 1.2))

        # The annotation is placed after the loop is fitted, into a band
        # reserved at the top. Folding it into the fit made the loop shrink and
        # shift the moment a note appeared — the opposite of one held canvas.
        # A tuple needs a tall band and a smaller figure under it; a one-line
        # caption needs neither, and squeezing the figure for a band that is not
        # there is what left it stranded at the bottom of the frame.
        has_tuple = note is not None and bool(note[0])
        band = (2.5 if has_tuple
                else 2.2 if title
                else 1.5 if note is not None
                else 0.0)
        cap = TYPE.scale["claim"] / TYPE.scale["body"]
        inner_h = slot.h - band
        factor = (min(slot.w / parts.width, inner_h / parts.height, cap)
                  * (0.88 if has_tuple else 1.0))
        parts.scale(factor).move_to([slot.x, slot.bottom + inner_h / 2, 0])

        whole = VGroup(parts)
        whole.add(Rectangle(width=slot.w, height=band, stroke_width=0,
                            fill_opacity=0.0).move_to(
                                [slot.x, slot.top - band / 2, 0]))
        note_group = None
        if note is not None:
            note_group = _note(note[0], note[1], slot.x, slot.top - band / 2,
                               highlight, title)
            whole.add(note_group)
        if not split:
            return whole
        return whole, {
            "cost": VGroup(*lane_refs),
            "reward": VGroup(*reward_refs),
            "insert": insert_ref[0][1] if insert_ref else None,
            "inserts": {k: v for k, v in insert_ref},
            "channels": channel_refs,
            "frame": frame_refs,
            "note": note_group,
            "tuple": None if note_group is None else note_group.tuple_group,
            "caption": None if note_group is None else note_group.caption,
        }

    return build


# ── the gap pass: one canvas, annotated in place ────────────────────────────

#: Element, then the notation and the line that goes with it. Order is
#: load-bearing: four elements that behave the same way, and then `c` breaks the
#: pattern on its own beats.
GAP_STEPS = [
    ("O", (r"O_{sim} \neq O_{real}", "surface, lighting, what is behind the track")),
    ("A", (r"A_{sim} \neq A_{real}", "commanded is not the control that is realised")),
    ("env", (r"P_{sim} \neq P_{real}", "friction, slip, actuation latency")),
    ("r", (r"r_{sim} = r_{real}", "reward is chosen, not measured, but computable in simulation only")),
]

#: Both tuples are split on the SAME boundaries. TransformMatchingTex matches
#: parts by their tex string, so the shared pieces slide to their new positions
#: and only `c` and `d` fade in. With the MDP side as one blob nothing matched
#: and the whole tuple crossfaded, which is what looked wrong.
_TUPLE_BODY = r"= \langle O, A, P, r"
_TUPLE_TAIL = r", \gamma \rangle"
#: One layout, used for both states. `_c`, `, c` and `, d` start invisible and
#: fade in where they already sit, so `M` becomes `M_c` and the two elements
#: appear in place instead of the rest of the tuple sliding to make room.
TUPLE_PARTS = [r"\mathcal{M}", r"_c", _TUPLE_BODY, r", c", r", d", _TUPLE_TAIL]
TUPLE_HIDDEN = (1, 3, 4)      # _c, ", c", ", d"
CMDP_NEW = (3, 4)             # the two that get the accent box

SOLVE_STEPS = [
    ("O", "encoder", "a robust encoder in front of the agent, and image-layer randomization"),
    ("A", "actuation map g", "the map from commanded to realised control, measured on a bench"),
    ("O", "history", "stacked observation and action history, implicit system identification"),
]


class _Canvas(Slide):
    """Draw the loop once, then modify it.

    No title and no rule — the figure is the slide — but it keeps the footer,
    so a bare canvas still says where in the deck it sits. The compiler fills
    the three attributes below on every raw beat.
    """

    slot = None
    section_name = ""
    slide_number = 1
    deck_sections: tuple = ()

    def _open(self):
        self.camera.background_color = ManimColor(PALETTE.ground)
        self.camera.init_background()
        # Kept clear of the footer rather than centred on the frame.
        self.slot = Slot("visual", 0.0, 0.06, 12.6, 6.6, role="visual")
        if self.deck_sections:
            self.add(footer(DeckMeta(sections=list(self.deck_sections)),
                            self.section_name, self.slide_number))

    def _hold(self):
        self.wait(0.4)
        self.next_slide()


#: The pass in order. `c` is last and is asked as a question, because whether
#: it differs is the thing the next section is about.
GAP_STEPS_ALL = [n for _, n in GAP_STEPS] + [
    # No caption on the last step. The question mark is the whole point and a
    # sentence underneath it only softens the pause.
    (r"c_{sim} \stackrel{?}{=} c_{real}", "")]
GAP_ORDER = [k for k, _ in GAP_STEPS] + ["c"]


class GapPass(_Canvas):
    """One canvas, one element marked at a time, the constraint marked last.

    Nothing is morphed and nothing appears or disappears: the loop is drawn once
    with every channel present, and each step recolours one channel's line and
    swaps the caption underneath. The cost channel is on screen the whole way
    and is marked at the end, as the fifth difference between simulation and
    reality rather than as something arriving late.
    """

    def construct(self):
        self._open()
        # Built WITH a note so the annotation band is reserved and the figure is
        # sized and placed for it; the note itself is then lifted out. Building
        # it without one left the figure full-height and the captions landed on
        # top of the AGENT box.
        figure, ex = loop(cost=True, note=GAP_STEPS_ALL[0], split=True)(self.slot)
        figure.remove(ex["note"])
        self.add(figure)
        self._hold()

        notes = []
        for entry in GAP_STEPS_ALL:
            _, spare = loop(cost=True, note=entry, split=True)(self.slot)
            notes.append(spare["note"])

        green, quiet = PALETTE.green.mid, PALETTE.structure_stroke
        heavy = GEOMETRY.stroke_weight * 1.5
        light = GEOMETRY.stroke_weight * 0.85
        showing = marked = None

        def mark(key, on: bool):
            """Only the line changes colour. Recolouring the label too turned it
            the line's tan and washed the text out."""
            if key == "env":
                return ex["frame"]["env"][0].animate.set_fill(
                    PALETTE.green.tint if on else PALETTE.structure_fill)
            line = ex["channels"][key][0]
            return (line.animate.set_color(green).set_stroke(width=heavy) if on
                    else line.animate.set_color(quiet).set_stroke(width=light))

        for index, key in enumerate(GAP_ORDER):
            steps = [FadeIn(notes[index])]
            if showing is not None:
                steps.append(FadeOut(showing, run_time=0.25))
            if marked is not None:
                steps.append(mark(marked, False))
            steps.append(mark(key, True))
            self.play(*steps, run_time=0.6)
            showing, marked = notes[index], key
            self._hold()


MDP_LINE = ("observation, not state: the car acts on a 160×120 image "
            "and a feature vector")
CMDP_LINE = "c is one wheel off track · d is a budget, set from hardware"


class MdpToCmdp(_Canvas):
    """The loop and its tuple on one canvas, then the constraint arrives.

    Two things this is working around.

    The cost lane comes from a second build rather than being hidden in the
    first: `extras["cost"]` is a fresh VGroup wrapping the same mobjects, so
    removing *it* from the figure removes nothing and the lane draws anyway.
    The no-cost build reserves the lane's width, so both builds land on the
    same scale and the lane can be drawn onto the first without anything moving.

    And the tuple is laid out for the CMDP, then collapsed: `_c`, `, c` and
    `, d` are hidden *and* the pieces after them are shifted left to close the
    gap they would leave. Growing back moves only what is to the right of each
    new symbol, so the prefix never moves and there is no hole to look at.
    """

    def construct(self):
        self._open()
        figure, m = loop(note=(TUPLE_PARTS, MDP_LINE), split=True)(self.slot)
        _, c = loop(cost=True, accent="c", highlight=CMDP_NEW,
                    note=(TUPLE_PARTS, CMDP_LINE), split=True)(self.slot)

        tex = m["tuple"].tex_mob
        sub_w = tex[1].width                        # the "_c" subscript
        cd_w = tex[3].width + tex[4].width          # ", c" and ", d"

        body, tail = tex[2], tex[5]
        appearing = VGroup(tex[1], tex[3], tex[4], *m["tuple"].boxes)
        moving_with_cd = VGroup(tex[3], tex[4], *m["tuple"].boxes)

        # collapse to the MDP reading
        for piece in (body, tail):
            piece.shift(LEFT * sub_w)
        moving_with_cd.shift(LEFT * sub_w)
        tail.shift(LEFT * cd_w)
        appearing.set_opacity(0.0)

        figure.remove(m["note"])
        self.play(FadeIn(figure, run_time=0.4), FadeIn(m["note"], run_time=0.4))
        self._hold()

        self.play(
            Create(c["cost"]),
            tex[1].animate.set_opacity(1.0),
            body.animate.shift(RIGHT * sub_w),
            moving_with_cd.animate.set_opacity(1.0).shift(RIGHT * sub_w),
            tail.animate.shift(RIGHT * (sub_w + cd_w)),
            FadeOut(m["caption"], run_time=0.25),
            FadeIn(c["caption"]),
            run_time=0.9,
        )
        self._hold()


SIM_LINE = ("in simulation both what the camera sees and what the actuators do "
            "can be randomized, and the reward is there to read")
REAL_LINE = ("on the car it arrives through the encoder, and there is no reward "
             "signal in the world to read at all")


class Observation(_Canvas):
    """The observation channel, in simulation and then on the car.

    Two views of the same loop rather than two figures: what changes is where
    the observation comes from, and that the real world has no reward to read.
    Only the parts that differ are animated.
    """

    def construct(self):
        self._open()
        # No cost channel here. This canvas is about where the observation comes
        # from and whether there is a reward to read; the cost lane only invites
        # a question the beat does not answer.
        # Randomization lands in two places, not one: what the camera sees and
        # what the actuators do with a command.
        sim, s = loop(insert=[("O", "randomization"), ("A", "randomization")],
                      title="In the simulator",
                      note=("", SIM_LINE), split=True)(self.slot)
        real, r = loop(reward=False, insert=[("O", "encoder")],
                       title="In the real world",
                       note=("", REAL_LINE), split=True)(self.slot)

        sim.remove(s["note"])
        self.play(FadeIn(sim, run_time=0.4), FadeIn(s["note"], run_time=0.4))
        self._hold()

        self.play(
            FadeOut(s["reward"]),
            Transform(s["inserts"]["O"], r["inserts"]["O"]),
            FadeOut(s["inserts"]["A"]),
            FadeOut(s["note"], run_time=0.25),
            FadeIn(r["note"]),
            run_time=0.8,
        )
        self._hold()
