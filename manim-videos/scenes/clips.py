"""Real footage as raw beats.

manim has no video mobject, so a clip plays as a stack of pre-decoded frames
swapped under a single `ImageMobject`. Decoding is PyAV, which is already in
the tree — no new dependency.

A clip beat is a `layout: raw` beat pointing at one of the classes below:

    raw:
      scene: scenes.clips:SimWorks
      class: Safety_SimWorks

Trim by editing `start` / `end` on the class. Everything here reads the deck
identity for its ground and its label type, so a clip beat still looks like the
rest of the deck (see hand-written-beats.md).
"""

from __future__ import annotations

from pathlib import Path

import av
import numpy as np
from manim import ImageMobject, ManimColor, Mobject

from presenting_lib.chrome import DeckMeta, footer
from presenting_lib.slots import Slot
from manim_slides import Slide

from presenting_lib.tokens import PALETTE

FOOTAGE = Path("/mnt/nas/MyPhotos")

#: Decode rate. The source is 30–60fps; nobody needs that to watch a car drive,
#: and every extra frame is an ImageMobject held in memory for the whole scene.
DECODE_FPS = 10
#: Longest edge of a decoded frame, in pixels.
DECODE_WIDTH = 720


def decode(path: Path, start: float, end: float | None, *,
           rotate: int = 0, fps: int = DECODE_FPS,
           width: int = DECODE_WIDTH) -> list[np.ndarray]:
    """Frames from `path` between `start` and `end`, at `fps`, RGB uint8.

    `rotate` is degrees counter-clockwise, for phone footage whose rotation
    lives in a side-data tag that PyAV does not apply for us.
    """
    frames: list[np.ndarray] = []
    step = 1.0 / fps
    want = start
    with av.open(str(path)) as container:
        stream = container.streams.video[0]
        stream.thread_type = "AUTO"
        container.seek(int(max(start - 1.0, 0) / stream.time_base), stream=stream)
        for frame in container.decode(stream):
            t = float(frame.pts * stream.time_base)
            if t < want:
                continue
            if end is not None and t > end:
                break
            image = frame.to_ndarray(format="rgb24")
            if rotate:
                image = np.rot90(image, k=rotate // 90)
            h, w = image.shape[:2]
            if w > width:
                from PIL import Image
                image = np.asarray(
                    Image.fromarray(image).resize((width, round(h * width / w))))
            frames.append(image)
            want += step
    if not frames:
        raise ValueError(f"{path}: no frames between {start} and {end}")
    return frames


class _ClipBase(Slide):
    """Shared ground, labels and playback.

    Geometry is written out here rather than borrowed from a layout: a raw beat
    has no slots, and the catalog has no layout for moving pictures. Labels do
    go through `Slot.fit_text`, so they size and wrap like every other claim in
    the deck (see hand-written-beats.md).
    """

    fps: int = DECODE_FPS
    section_name = ""
    slide_number = 1
    deck_sections: tuple = ()

    def _ground(self):
        self.camera.background_color = ManimColor(PALETTE.ground)
        self.camera.init_background()
        if self.deck_sections:
            self.add(footer(DeckMeta(sections=list(self.deck_sections)),
                            self.section_name, self.slide_number))

    @staticmethod
    def _label(text, x, width):
        if not text:
            return None
        return Slot("label", x, 3.15, width, 0.8,
                    style="claim", align="center").fit_text(
                        str(text), style="claim", weight="BOLD")

    @staticmethod
    def _fit(image, width, height, centre):
        image.scale_to_fit_height(height)
        if image.width > width:
            image.scale_to_fit_width(width)
        image.move_to(centre)
        return image

    def _play(self, pairs):
        """Play `pairs` of (mobject, frames) on one clock.

        Two things this shape is working around.

        One `wait` for the whole clip rather than a wait per frame: manim writes
        a partial movie file per animation, and a hundred single-frame files is
        what manim-slides fails to concatenate.

        And the updater has to sit on the image itself. Manim bakes every
        mobject with no time-based updater into a static background image and
        stops redrawing it, so driving the swap from a separate ticker mobject
        renders the first frame and then freezes on it.

        A shorter stack holds its last frame rather than ending the slide early.
        """
        total = max(len(frames) for _, frames in pairs)
        state = {"t": 0.0, "i": {}}

        for index, (holder, frames) in enumerate(pairs):
            height, centre = holder.height, holder.get_center()

            def advance(mobject, dt, frames=frames, height=height,
                        centre=centre, index=index):
                if index == 0:                    # the first holder carries the clock
                    state["t"] += dt
                want = min(int(state["t"] * self.fps), len(frames) - 1)
                if state["i"].get(index) == want:
                    return
                state["i"][index] = want
                mobject.become(ImageMobject(frames[want])
                               .scale_to_fit_height(height).move_to(centre))

            holder.add_updater(advance)

        self.wait(total / self.fps)
        for holder, _ in pairs:
            holder.clear_updaters()


class Clip(_ClipBase):
    """One clip, centred, with a label above it."""

    clip: str = ""
    start: float = 0.0
    end: float | None = None
    rotate: int = 0
    label: str = ""

    def construct(self):
        self._ground()
        frames = decode(FOOTAGE / self.clip, self.start, self.end,
                        rotate=self.rotate, fps=self.fps)
        image = self._fit(ImageMobject(frames[0]), 12.4, 5.6, [0.0, -0.12, 0.0])
        caption = self._label(self.label, 0.0, 12.0)
        self.add(image)
        if caption is not None:
            self.add(caption)
        self._play([(image, frames)])
        self.wait(0.4)
        self.next_slide()


class ClipPair(_ClipBase):
    """Two clips side by side, each labelled, playing on one clock."""

    clip_l: str = ""
    clip_r: str = ""
    start_l: float = 0.0
    end_l: float | None = None
    start_r: float = 0.0
    end_r: float | None = None
    rotate_l: int = 0
    rotate_r: int = 0
    label_l: str = ""
    label_r: str = ""

    def construct(self):
        self._ground()
        left_frames = decode(FOOTAGE / self.clip_l, self.start_l, self.end_l,
                             rotate=self.rotate_l, fps=self.fps)
        right_frames = decode(FOOTAGE / self.clip_r, self.start_r, self.end_r,
                              rotate=self.rotate_r, fps=self.fps)
        left = self._fit(ImageMobject(left_frames[0]), 6.4, 5.0, [-3.45, -0.3, 0.0])
        right = self._fit(ImageMobject(right_frames[0]), 6.4, 5.0, [3.45, -0.3, 0.0])
        self.add(left, right)
        for text, x in ((self.label_l, -3.45), (self.label_r, 3.45)):
            caption = self._label(text, x, 6.4)
            if caption is not None:
                self.add(caption)
        self._play([(left, left_frames), (right, right_frames)])
        self.wait(0.4)
        self.next_slide()


# ── the deck's clips ─────────────────────────────────────────────────────────

class SimWorks(Clip):
    """1.2 — the policy driving in simulation. Old Gazebo stack; see the beat."""
    clip = "deepracer/up.mp4"
    start, end = 24.0, 38.0
    label = "In the simulator"


class RealByHand(Clip):
    """1.3 — the same car, driven by hand. Trimmed by the user; play it whole."""
    clip = "deepracer/wlad_driver.mp4"
    start, end = 0.0, None
    label = "When we put it in the real world"


class RealByPolicy(Clip):
    """1.4 — the policy driving it badly. Already portrait on disk (480x848),
    so no rotation: the trim baked the orientation in."""
    clip = "deepracer/car_running_away.mp4"
    start, end = 0.0, None
    rotate = 0
    label = "On the real track, by the policy"


class OnboardPair(ClipPair):
    """5.2 — the two camera streams, side by side, plainly not the same."""
    clip_l = "deepracer/pov.mp4"
    start_l, end_l = 18.0, 35.0
    label_l = "Simulated: outdoors, asphalt"
    clip_r = "deepracer/donut_t1.mp4"
    start_r, end_r = 0.0, None
    label_r = "Real: indoors, cloth, foam walls"


# ── related work, in motion ─────────────────────────────────────────────────

class AceVideo(Clip):
    """Project Ace: Sony AI's table tennis robot. Capped at 24s — the source is
    47s and every decoded frame is held in memory for the whole scene."""
    clip = "deepracer/ace.mp4"
    start, end = 0.0, 24.0
    label = "Project Ace"


class WheeledVideo(Clip):
    """Wheeled Lab, played whole."""
    clip = "deepracer/wheeledbot.mp4"
    start, end = 0.0, None
    label = "Wheeled Lab"


class CubeVideo(Clip):
    """OpenAI's Rubik's cube hand, played whole."""
    clip = "deepracer/cube.mp4"
    start, end = 0.0, None
    label = "Solving a Rubik's cube"


class GeneralizationVideo(Clip):
    """Results: the fleet training across tracks at once, played whole."""
    clip = "deepracer/generalization.mp4"
    start, end = 0.0, None
    label = "Held-out tracks, no visual randomization"


class OnnxInference(Clip):
    """Results: the ONNX inference node driving the physical car. 4K source,
    downscaled on decode like the rest."""
    clip = "deepracer/onnx_inference.mp4"
    start, end = 0.0, None
    label = "Inference on the car"


class DriftWheeled(Clip):
    """Wheeled Lab's controlled drifting, played whole. Filename on disk is
    `drift_whelled.mp4` — kept as-is rather than renamed under the user."""
    clip = "deepracer/drift_whelled.mp4"
    start, end = 0.0, None
    label = "Controlled drifting"
