"""Node-and-edge diagrams: Graphviz for positioning only, never for drawing.

Letting Graphviz draw would make every diagram look like Graphviz, which is
exactly the thing that stops a deck looking like one person made it. So the
pipeline is:

    node/edge spec -> DOT -> `dot -Tplain` -> parse -> draw with library primitives

`-Tplain` is a stable, documented format:

    graph <scale> <width> <height>
    node <name> <x> <y> <width> <height> <label> <style> <shape> <color> <fillcolor>
    edge <tail> <head> <n> <x1> <y1> ... <xn> <yn> [<label> <xl> <yl>] <style> <color>
    stop

Coordinates are in inches with the origin at the bottom left and y increasing
upward — the same orientation manim uses, verified rather than assumed
(`printf 'digraph{rankdir=TB;a->b;}' | dot -Tplain` puts the top node at the
larger y). So there is no flip here, and adding one would be a bug.

Node sizes are computed from *our* measured text before the DOT is written, at
one graphviz inch to one manim unit, so Graphviz packs boxes that are already
the right size instead of sizing them from its own font metrics.

Scope honestly: this handles graphs. Not a hand-composed spatial figure, not a
paraboloid. Those are `raw` beats or draw.io.
"""

from __future__ import annotations

import shlex
import shutil
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np
from manim import (
    ArrowTriangleFilledTip,
    CubicBezier,
    RoundedRectangle,
    VGroup,
    VMobject,
)

from .errors import DiagramError, SlotOverflow
from .measure import metrics
from .slots import Slot
from .tokens import GEOMETRY, GROUND, PALETTE, STRUCTURE, TYPE

#: Point size handed to graphviz for an edge label. It only has to be close —
#: graphviz uses it to reserve room and to pull parallel edges apart; the glyphs
#: we draw come from the type scale like every other label.
EDGE_LABEL_PT = 13.0

NODE_PAD_X = 0.42
NODE_PAD_Y = 0.30
MIN_NODE_W = 1.3
MIN_NODE_H = 0.62


@dataclass
class Node:
    id: str
    label: str
    accent: str | None = None      # "green" | "yellow" | None -> structure
    shape: str = "box"


@dataclass
class Edge:
    tail: str
    head: str
    label: str = ""
    accent: str | None = None
    dashed: bool = False
    #: graphviz compass points ("n", "sw", ...). Parallel edges land their
    #: labels on top of each other without them — an RL loop has two edges
    #: coming back from the environment and they must be readable apart.
    tailport: str = ""
    headport: str = ""


@dataclass
class DiagramSpec:
    nodes: list[Node]
    edges: list[Edge] = field(default_factory=list)
    rankdir: str = "TB"            # TB | LR | BT | RL
    engine: str = "dot"

    def node(self, node_id: str) -> Node:
        for n in self.nodes:
            if n.id == node_id:
                return n
        raise DiagramError(f"edge references unknown node {node_id!r}")


# ── graphviz ─────────────────────────────────────────────────────────────────

def _node_size(label: str) -> tuple[float, float]:
    m = metrics(TYPE.family("body"), TYPE.size("body"))
    width = m.width_of(label) + 2 * NODE_PAD_X
    height = m.single_line_height + 2 * NODE_PAD_Y
    return max(width, MIN_NODE_W), max(height, MIN_NODE_H)


def to_dot(spec: DiagramSpec, spread: float = 1.0) -> str:
    lines = [
        "digraph presenting {",
        f"  rankdir={spec.rankdir};",
        f"  nodesep={GEOMETRY.gutter * spread:.3f};",
        f"  ranksep={GEOMETRY.gutter * 1.4 * spread:.3f};",
        '  node [shape=box, fixedsize=true, label=""];',
        "  edge [arrowhead=none];",
    ]
    for node in spec.nodes:
        w, h = _node_size(node.label)
        lines.append(f'  {node.id} [width={w:.4f}, height={h:.4f}];')
    for edge in spec.edges:
        ports = "".join(
            f", {name}port={value}"
            for name, value in (("tail", edge.tailport), ("head", edge.headport))
            if value)
        if edge.label:
            # Hand graphviz the text so it routes around the label and pulls
            # parallel edges apart; we still draw the glyphs ourselves, at the
            # position it reports back.
            lines.append(f'  {edge.tail} -> {edge.head} '
                         f'[label="{edge.label}", fontsize={EDGE_LABEL_PT}{ports}];')
        elif ports:
            lines.append(f"  {edge.tail} -> {edge.head} [{ports.lstrip(', ')}];")
        else:
            lines.append(f"  {edge.tail} -> {edge.head};")
    lines.append("}")
    return "\n".join(lines) + "\n"


@dataclass
class Plain:
    width: float
    height: float
    nodes: dict[str, tuple[float, float, float, float]]   # id -> x, y, w, h
    edges: list[tuple[str, str, list[tuple[float, float]]]]
    #: One entry per edge in `edges`, positionally: where graphviz put that
    #: edge's label, or None. Keying by (tail, head) collapses parallel edges —
    #: and an RL loop is two edges from the environment back to the agent.
    edge_labels: list[tuple[float, float] | None] = field(default_factory=list)


def run_dot(dot_source: str, engine: str = "dot") -> Plain:
    if shutil.which(engine) is None:
        raise DiagramError(
            f"{engine!r} is not on PATH. Install graphviz, or give the beat a "
            "`raw` layout and place the figure by hand."
        )
    result = subprocess.run(
        [engine, "-Tplain"], input=dot_source, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise DiagramError(f"{engine} failed: {result.stderr.strip()}")
    return parse_plain(result.stdout)


def parse_plain(text: str) -> Plain:
    width = height = 0.0
    nodes: dict[str, tuple[float, float, float, float]] = {}
    edges: list[tuple[str, str, list[tuple[float, float]]]] = []
    edge_labels: list[tuple[float, float] | None] = []

    for line in text.splitlines():
        try:
            parts = shlex.split(line)
        except ValueError:                 # an unbalanced quote is not ours
            parts = line.split()
        if not parts:
            continue
        if parts[0] == "graph":
            width, height = float(parts[2]), float(parts[3])
        elif parts[0] == "node":
            nodes[parts[1]] = (float(parts[2]), float(parts[3]),
                               float(parts[4]), float(parts[5]))
        elif parts[0] == "edge":
            count = int(parts[3])
            coords = [(float(parts[4 + 2 * i]), float(parts[5 + 2 * i]))
                      for i in range(count)]
            edges.append((parts[1], parts[2], coords))
            # `edge t h n x1 y1 .. xn yn [label xl yl] style color` — the
            # optional label triple is the only thing that makes the tail five
            # tokens long instead of two.
            rest = parts[4 + 2 * count:]
            edge_labels.append((float(rest[1]), float(rest[2]))
                               if len(rest) >= 5 else None)
        elif parts[0] == "stop":
            break
    return Plain(width, height, nodes, edges, edge_labels)


# ── drawing ──────────────────────────────────────────────────────────────────

def _surface(accent: str | None):
    return PALETTE.surface(accent) if accent else STRUCTURE


def _node_mobject(node: Node, box: tuple[float, float, float, float],
                  to_frame, scale: float) -> VGroup:
    x, y, w, h = box
    surface = _surface(node.accent)
    centre = to_frame(x, y)
    rect = RoundedRectangle(
        width=w * scale, height=h * scale,
        corner_radius=GEOMETRY.corner_radius,
        color=surface.stroke or PALETTE.structure_stroke,
        fill_color=surface.fill or PALETTE.structure_fill,
        fill_opacity=1.0,
        stroke_width=GEOMETRY.stroke_weight * 0.7,
    )
    rect.move_to(centre)

    label_slot = Slot(f"node_{node.id}", centre[0], centre[1],
                      (w - 2 * NODE_PAD_X * 0.6) * scale,
                      (h - 2 * NODE_PAD_Y * 0.5) * scale, style="body")
    label = label_slot.fit_text(node.label, style="body", on=surface)
    return VGroup(rect, label)


def _edge_label_mobject(edge: Edge, position, to_frame) -> VGroup:
    """The edge's own text, on a patch of ground so the line does not run
    through it."""
    surface = _surface(edge.accent) if edge.accent else GROUND
    centre = to_frame(*position)
    text = Slot(f"edge_{edge.tail}_{edge.head}", centre[0], centre[1],
                4.0, 0.5, style="caption").fit_text(
                    edge.label, style="caption", on=surface)
    backing = RoundedRectangle(
        width=text.width + 0.18, height=text.height + 0.12,
        corner_radius=0.06, stroke_width=0,
        fill_color=surface.fill or PALETTE.ground, fill_opacity=1.0)
    backing.move_to(centre)
    return VGroup(backing, text)


def _edge_mobject(edge: Edge, points, to_frame) -> VGroup:
    frame_points = [to_frame(x, y) for x, y in points]
    colour = (_surface(edge.accent).stroke if edge.accent
              else PALETTE.structure_stroke)
    path = VGroup()
    for i in range(0, len(frame_points) - 3, 3):
        path.add(CubicBezier(*frame_points[i:i + 4], color=colour,
                             stroke_width=GEOMETRY.stroke_weight * 0.8))
    if len(path) == 0:
        return path

    end, before = frame_points[-1], frame_points[-2]
    direction = end - before
    norm = float(np.linalg.norm(direction))
    if norm > 1e-6:
        tip = ArrowTriangleFilledTip(color=colour, length=0.22)
        # The tip is built pointing along +x; rotate by the delta to the edge's
        # own heading, then sit its point on the edge's last point.
        tip.rotate(np.arctan2(direction[1], direction[0]) - tip.tip_angle)
        tip.move_to(end - direction / norm * tip.length / 2)
        path.add(tip)
    return path


def build(spec: DiagramSpec, slot: Slot) -> tuple[VGroup, list[VGroup]]:
    """Lay out and draw `spec` inside `slot`.

    Returns the whole diagram plus a reveal sequence: node declaration order,
    each node arriving with the edges that connect it to something already on
    screen. Graphviz gives us that ordering for free.
    """
    plain = run_dot(to_dot(spec), spec.engine)
    if not plain.nodes:
        raise DiagramError("graphviz returned no nodes")

    # A small graph marooned in the middle of a big slot reads as a mistake, and
    # a full-bleed figure that fills a fifth of the frame is not full-bleed. The
    # fix is to spread the graph, not to magnify it: node boxes are sized from
    # our own measured text, so scaling up would push the labels off the type
    # scale. Re-running dot with wider separations fills the slot at the same
    # text size. The residual scale-up is capped where `body` would reach
    # `claim` — both real steps — so it can never invent a size.
    plain = _spread_to_fill(spec, plain, slot)
    max_scale = TYPE.scale["claim"] / TYPE.scale["body"]
    scale = (min(slot.w / plain.width, slot.h / plain.height, max_scale)
             if plain.width and plain.height else 1.0)
    if scale * TYPE.size("body") < TYPE.min_legible_body:
        raise SlotOverflow(
            slot.name,
            " / ".join(n.label for n in spec.nodes),
            min_size=round(TYPE.min_legible_body, 1),
            tried_size=round(scale * TYPE.size("body"), 1),
        )

    def to_frame(x: float, y: float) -> np.ndarray:
        return np.array([
            slot.x + (x - plain.width / 2) * scale,
            slot.y + (y - plain.height / 2) * scale,
            0.0,
        ])

    node_mobs = {n.id: _node_mobject(n, plain.nodes[n.id], to_frame, scale)
                 for n in spec.nodes if n.id in plain.nodes}

    # Parallel edges share a (tail, head) pair, so they are consumed in
    # declaration order rather than looked up — graphviz emits them in the
    # order they were declared, which is the order they are in `spec.edges`.
    laid_out: dict[tuple[str, str], list] = defaultdict(list)
    for index, (tail, head, points) in enumerate(plain.edges):
        laid_out[(tail, head)].append(
            (points, plain.edge_labels[index]
             if index < len(plain.edge_labels) else None))
    taken: dict[tuple[str, str], int] = defaultdict(int)
    order = [n.id for n in spec.nodes]
    revealed: set[str] = set()
    steps: list[VGroup] = []

    for node_id in order:
        group = VGroup(node_mobs[node_id])
        revealed.add(node_id)
        for edge in spec.edges:
            if edge.head != node_id and edge.tail != node_id:
                continue
            other = edge.tail if edge.head == node_id else edge.head
            if other not in revealed:
                continue
            pair = (edge.tail, edge.head)
            index = taken[pair]
            if index >= len(laid_out[pair]):
                continue
            taken[pair] += 1
            points, where = laid_out[pair][index]
            if points:
                group.add(_edge_mobject(edge, points, to_frame))
                if edge.label and where:
                    group.add(_edge_label_mobject(edge, where, to_frame))
        steps.append(group)

    whole = VGroup(*steps)
    # Carry the reveal sequence on the mobject. Graphviz gives us the node
    # ordering for free and it was being thrown away — every diagram arrived
    # fully drawn in one beat, which is the opposite of the point.
    whole.presenting_reveal = steps
    return whole, steps


#: Stop spreading once the graph is at least this fraction of the slot.
FILL_TARGET = 0.82
MAX_SPREAD = 6.0


def _spread_to_fill(spec: DiagramSpec, plain: "Plain", slot: Slot) -> "Plain":
    """Re-lay the graph with wider separations until it roughly fills `slot`."""
    if not plain.width or not plain.height:
        return plain

    spread = 1.0
    for _ in range(2):
        fill = max(plain.width / slot.w, plain.height / slot.h)
        if fill >= FILL_TARGET or fill <= 0:
            return plain
        spread = min(spread * (FILL_TARGET / fill), MAX_SPREAD)
        candidate = run_dot(to_dot(spec, spread), spec.engine)
        if not candidate.nodes:
            return plain
        # Wider separations move nodes apart but never resize them, so a graph
        # that stops growing has hit its own aspect ratio, not a bug.
        if max(candidate.width, candidate.height) <= max(plain.width, plain.height):
            return candidate
        plain = candidate
    return plain


def builder(spec: DiagramSpec):
    """A `visual` callable for a beat: `visual=diagrams.builder(spec)`."""

    def make(slot: Slot):
        whole, _ = build(spec, slot)
        return whole

    return make
