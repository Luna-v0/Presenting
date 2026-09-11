#!/usr/bin/env python3
"""The mechanical half of deck-review.

    uv run python scripts/review_deck.py decks/ft-v2/screenplay.md
    uv run python scripts/review_deck.py decks/ft-v2/screenplay.md --frames media/review

Three passes, cheapest first:

1. **Screenplay** — everything `presenting_lib.compile.validate` can see without
   rendering: budgets, missing bridges, empty visual slots, time overrun.
2. **Model** — builds every beat through the layout library and checks geometry
   exactly: inside the safe area, inside its own slot, no collision between
   slots, no visual slot still holding a placeholder.
3. **Pixels** — over frames pulled by `extract_frames.py`. This pass exists for
   the one failure class the other two structurally cannot see: a slide that is
   correct in code and unreadable on screen. During the identity work a colour
   was silently overridden downstream and every label rendered light-on-light;
   the geometry was perfect and a human eye was the only thing that caught it.

The accent-consistency check ("is this accent being used for its assigned
meaning?") is *skipped and says so* while the meanings are unassigned in
identity/tokens.yaml. A check that cannot state what it is checking against
would only produce noise.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from presenting_lib import compile as C  # noqa: E402
from presenting_lib.chrome import CONTENT_BY_TIER, NONE  # noqa: E402
from presenting_lib.screenplay import Beat, Deck, load  # noqa: E402
from presenting_lib.slots import frame as full_frame, safe_area  # noqa: E402
from presenting_lib.tokens import PALETTE, T  # noqa: E402

TOL = 0.03


@dataclass
class Report:
    findings: list[C.Finding]
    skipped: list[str]

    def by_level(self, level: str) -> list[C.Finding]:
        return [f for f in self.findings if f.level == level]


# ── pass 2: model geometry ───────────────────────────────────────────────────

def build_beat(beat: Beat, deck: Deck, number: int):
    layout = C.layout_for(beat)
    content = C.content_for(beat, deck, number=number,
                            deck_dir=deck.path.parent if deck.path else None)
    return layout, layout.build(content, target=deck.target)


def check_model(deck: Deck) -> tuple[list[C.Finding], dict[str, int], dict]:
    findings: list[C.Finding] = []
    slide_counts: dict[str, int] = {}
    boxes_by_beat: dict[str, list] = {}
    ordered = deck.main_beats() + deck.backup_beats()

    for number, beat in enumerate(ordered, start=1):
        if beat.is_raw():
            slide_counts[beat.id] = 1
            findings.append(C.Finding(
                "note", beat.id,
                "raw beat — the library does not lay it out, so geometry and "
                "contrast here are the author's to check by eye."))
            continue
        try:
            layout, built = build_beat(beat, deck, number)
        except Exception as exc:
            findings.append(C.Finding("error", beat.id,
                                      f"{type(exc).__name__}: {exc}"))
            slide_counts[beat.id] = 0
            continue

        # Count what the compiler will actually emit: a step whose visual
        # carries a reveal sequence becomes several slides.
        slide_counts[beat.id] = sum(
            1
            for step in built.steps
            for sub in C.expand_reveals(step)
            if sub.elements and sub.pause
        )
        bounds = full_frame() if built.chrome == NONE else safe_area()
        area = CONTENT_BY_TIER[built.chrome]

        placed: list[tuple[str, object]] = []
        for step in built.steps:
            for element in step.elements:
                mob = element.mobject
                if mob.width == 0 and mob.height == 0:
                    continue
                if not bounds.contains(mob, tol=TOL):
                    findings.append(C.Finding(
                        "error", beat.id,
                        f"{layout.name}.{element.slot} leaves the safe area: "
                        f"x[{mob.get_left()[0]:.2f},{mob.get_right()[0]:.2f}] "
                        f"y[{mob.get_bottom()[1]:.2f},{mob.get_top()[1]:.2f}] "
                        f"vs x±{bounds.w / 2:.2f} y±{bounds.h / 2:.2f}"))
                slot = layout.slots.get(element.slot)
                if slot is not None and not slot.contains(mob, tol=TOL):
                    findings.append(C.Finding(
                        "warn", beat.id,
                        f"{layout.name}.{element.slot} overflows its own slot"))
                placed.append((element.slot, mob))

        for i, (slot_a, mob_a) in enumerate(placed):
            for slot_b, mob_b in placed[i + 1:]:
                if slot_a == slot_b or not slot_a or not slot_b:
                    continue
                if _overlap(mob_a, mob_b) > 0.02:
                    findings.append(C.Finding(
                        "error", beat.id,
                        f"{layout.name}: {slot_a} and {slot_b} collide"))

        spec = beat.visual or {}
        if spec.get("kind", "none") not in ("none", "") and not spec.get("graph") \
                and not spec.get("data"):
            from presenting_lib.placeholders import VisualSpec

            probe = VisualSpec(kind=spec["kind"], sub=spec.get("sub", ""),
                               intent=spec.get("intent", ""), asset=spec.get("asset"))
            deck_dir = deck.path.parent if deck.path else None
            if probe.resolved_asset(deck_dir) is None:
                findings.append(C.Finding(
                    "warn", beat.id,
                    f"visual slot still holds a placeholder ({spec.get('sub') or spec['kind']}"
                    f": {spec.get('intent', '')[:60]}). SHOTS.md should have an entry."))

        boxes_by_beat[beat.id] = text_boxes(built)
    return findings, slide_counts, boxes_by_beat


def _overlap(a, b) -> float:
    ax0, ax1 = a.get_left()[0], a.get_right()[0]
    ay0, ay1 = a.get_bottom()[1], a.get_top()[1]
    bx0, bx1 = b.get_left()[0], b.get_right()[0]
    by0, by1 = b.get_bottom()[1], b.get_top()[1]
    dx = min(ax1, bx1) - max(ax0, bx0)
    dy = min(ay1, by1) - max(ay0, by0)
    return max(dx, 0.0) * max(dy, 0.0)


# ── pass 3: pixels ───────────────────────────────────────────────────────────

def _srgb_to_linear(channel: np.ndarray) -> np.ndarray:
    return np.where(channel <= 0.04045, channel / 12.92,
                    ((channel + 0.055) / 1.055) ** 2.4)


def luminance(rgb: np.ndarray) -> np.ndarray:
    linear = _srgb_to_linear(rgb.astype(np.float64) / 255.0)
    return (0.2126 * linear[..., 0] + 0.7152 * linear[..., 1] + 0.0722 * linear[..., 2])


def contrast(l1: float, l2: float) -> float:
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def palette_colours() -> np.ndarray:
    values = [PALETTE.ground, PALETTE.ink, PALETTE.muted,
              PALETTE.structure_fill, PALETTE.structure_stroke]
    for ramp in (PALETTE.green, PALETTE.yellow):
        values += [ramp.tint, ramp.mid, ramp.dark]
    return np.array([[int(v.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
                     for v in values], dtype=np.float64)


#: WCAG's own floor for large text. Anything under this is not "subtle", it is
#: a label the back of the room cannot read.
MIN_CONTRAST = 3.0


def text_boxes(built) -> list[tuple[int, str, tuple[float, float, float, float]]]:
    """(step index, slot, frame-coordinate box) for every text mobject drawn.

    Located from the model rather than guessed from pixels. A tile heuristic
    has to infer where the text is, gets it wrong on compression noise, and
    then reports every slide as broken; the layout library already knows.
    """
    from manim import MathTex, Text

    # Indexed against the *expanded* steps, the same sequence the compiler
    # emits slides for. Indexing the unexpanded steps checks a text box on
    # frames rendered before that text exists, and an empty box measures 1.00:1
    # — a whole screen of false light-on-light reports.
    found = []
    index = 0
    for step in built.steps:
        for sub in C.expand_reveals(step):
            for element in sub.elements:
                for mob in _text_mobjects(element.mobject):
                    found.append((index, element.slot,
                                  (mob.get_left()[0], mob.get_bottom()[1],
                                   mob.get_right()[0], mob.get_top()[1])))
            if sub.elements and sub.pause:
                index += 1
    return found


def _text_mobjects(mobject) -> list:
    from manim import MathTex, Text

    if isinstance(mobject, (Text, MathTex)):
        return [mobject]
    out = []
    for child in getattr(mobject, "submobjects", []):
        out += _text_mobjects(child)
    return out


def to_pixels(box, width: int, height: int) -> tuple[int, int, int, int]:
    from presenting_lib.tokens import GEOMETRY

    x0, y0, x1, y1 = box
    px0 = int((x0 + GEOMETRY.frame_width / 2) / GEOMETRY.frame_width * width)
    px1 = int((x1 + GEOMETRY.frame_width / 2) / GEOMETRY.frame_width * width)
    py0 = int((GEOMETRY.frame_height / 2 - y1) / GEOMETRY.frame_height * height)
    py1 = int((GEOMETRY.frame_height / 2 - y0) / GEOMETRY.frame_height * height)
    return (max(px0, 0), max(py0, 0), min(px1, width), min(py1, height))


def box_contrast(lum: np.ndarray, rect: tuple[int, int, int, int]) -> float | None:
    """Contrast between a text box's glyphs and its own background.

    Against the *median* — the background — rather than across a percentile
    spread. Glyph coverage inside a box varies from about a third for a dense
    line of body text down to under a tenth for a wide equation, and a spread
    wide enough to survive the sparse case reads the dense case as broken.
    The median is the background whatever the coverage is.
    """
    x0, y0, x1, y1 = rect
    if x1 - x0 < 3 or y1 - y0 < 3:
        return None
    patch = lum[y0:y1, x0:x1]
    background = float(np.median(patch))
    lo, hi = np.percentile(patch, 2), np.percentile(patch, 98)
    foreground = lo if abs(background - lo) > abs(hi - background) else hi
    return contrast(background, foreground)


def check_frame(path: Path, *, boxes, allow_offpalette: bool) -> list[str]:
    """Everything about a frame that only pixels can answer."""
    from PIL import Image

    image = np.asarray(Image.open(path).convert("RGB"))
    height, width = image.shape[:2]
    lum = luminance(image)
    issues: list[str] = []

    # Contrast, measured inside the rectangles the library actually placed text
    # in. This is the check that exists because a colour can be correct in code
    # and unreadable on screen.
    for slot, box in boxes:
        ratio = box_contrast(lum, to_pixels(box, width, height))
        if ratio is not None and ratio < MIN_CONTRAST:
            issues.append(
                f"{slot or 'text'} reads at {ratio:.2f}:1 against its own background, "
                f"floor {MIN_CONTRAST}:1 — this is the light-on-light failure")

    # A third colour behaving like an accent: pixels far from every palette
    # colour and from every blend of two of them (anti-aliasing makes blends).
    if not allow_offpalette:
        palette = palette_colours()
        sample = image.reshape(-1, 3)[::37].astype(np.float64)
        stray = float((_distance_to_palette_blends(sample, palette) > 26.0).mean())
        if stray > 0.02:
            issues.append(
                f"{stray:.1%} of sampled pixels are off-palette — something is "
                "using a colour that is not in identity/tokens.yaml")
    return issues


def _distance_to_palette_blends(pixels: np.ndarray, palette: np.ndarray) -> np.ndarray:
    """Distance from each pixel to the nearest segment between two palette colours."""
    best = np.full(len(pixels), np.inf)
    count = len(palette)
    for i in range(count):
        for j in range(i, count):
            a, b = palette[i], palette[j]
            ab = b - a
            denom = float(ab @ ab)
            if denom < 1e-9:
                proj = np.zeros(len(pixels))
            else:
                proj = np.clip(((pixels - a) @ ab) / denom, 0.0, 1.0)
            closest = a + proj[:, None] * ab
            best = np.minimum(best, np.linalg.norm(pixels - closest, axis=1))
    return best


def frame_beat_map(deck: Deck, slide_counts: dict[str, int]) -> dict[str, list]:
    """scene name -> [(beat_id, slide index within the beat)] in render order.

    Mapped per *scene*, not across the whole deck. A raw beat runs code the
    library never sees and can call `next_slide()` as many times as it likes,
    so any deck-wide index silently shifts after the first one and every later
    frame gets attributed to the wrong beat.
    """
    per_scene: dict[str, list] = {}
    for group in C.scene_groups(deck):
        if group.kind == "raw":
            per_scene[group.name] = []          # unknown, and not ours to check
            continue
        entries = []
        for beat in group.beats:
            for i in range(max(slide_counts.get(beat.id, 1), 1)):
                entries.append((beat.id, i + 1))
        per_scene[group.name] = entries
    return per_scene


def check_pixels(deck: Deck, frames_dir: Path, slide_counts: dict[str, int],
                 boxes_by_beat: dict) -> list[C.Finding]:
    findings: list[C.Finding] = []
    frames = sorted(frames_dir.glob("*.png"))
    if not frames:
        findings.append(C.Finding(
            "warn", "", f"no frames in {frames_dir} — render at -ql and run "
                        "scripts/extract_frames.py first; the pixel pass is the only "
                        "one that can see an unreadable slide."))
        return findings

    per_scene = frame_beat_map(deck, slide_counts)
    by_scene: dict[str, list[Path]] = {}
    for path in frames:
        by_scene.setdefault(path.stem.rsplit("-", 1)[0], []).append(path)

    imaged = {b.id for b in deck.beats()
              if (b.visual or {}).get("kind") in ("referential", "chart")}
    checked = 0

    for scene, scene_frames in sorted(by_scene.items()):
        entries = per_scene.get(scene)
        if entries is None:
            findings.append(C.Finding(
                "note", "", f"{scene}: frames present but no such scene in the "
                            "screenplay — stale render?"))
            continue
        if not entries:
            # A raw scene has no slots to check, but it is still in the deck and
            # it is the most likely thing in it to be off-identity — hand-written
            # scenes usually predate the palette. Report how far off it is
            # rather than skipping it silently.
            findings += _raw_scene_palette(scene, scene_frames)
            continue
        if len(entries) != len(scene_frames):
            findings.append(C.Finding(
                "warn", "",
                f"{scene}: {len(scene_frames)} frames but {len(entries)} slides "
                "predicted from the screenplay. The render is out of date, or the "
                "compiler and the model disagree about where the slides break."))
            continue
        for path, (beat_id, step_no) in zip(scene_frames, entries):
            # Frame k of a beat shows everything revealed up to and including step k.
            boxes = [(slot, box) for step, slot, box in boxes_by_beat.get(beat_id, [])
                     if step < step_no]
            checked += 1
            for issue in check_frame(path, boxes=boxes,
                                     allow_offpalette=beat_id in imaged):
                findings.append(C.Finding("error", beat_id, f"{path.name}: {issue}"))

    findings.append(C.Finding(
        "note", "", f"pixel pass: {checked} of {len(frames)} frames checked "
                    f"({len(frames) - checked} belong to raw scenes or unmapped renders)."))
    return findings


#: Above this fraction of off-palette pixels, a hand-written scene is visibly
#: not part of the deck rather than merely using a tint we did not anticipate.
RAW_OFFPALETTE_LIMIT = 0.12


def _raw_scene_palette(scene: str, frames: list[Path]) -> list[C.Finding]:
    from PIL import Image

    palette = palette_colours()
    worst = 0.0
    for path in frames:
        image = np.asarray(Image.open(path).convert("RGB"))
        sample = image.reshape(-1, 3)[::53].astype(np.float64)
        worst = max(worst, float(
            (_distance_to_palette_blends(sample, palette) > 26.0).mean()))
    if worst <= RAW_OFFPALETTE_LIMIT:
        return []
    return [C.Finding(
        "warn", "",
        f"{scene}: a hand-written scene, and {worst:.0%} of its pixels are off "
        "the identity — it will read as belonging to a different deck. The "
        "library does not touch raw beats, so restyling it is a deliberate "
        "choice: take colours from presenting_lib.tokens.PALETTE and set the "
        "camera background to PALETTE.ground.")]


# ── slide hand-offs ──────────────────────────────────────────────────────────

#: A slide's video plays on entry, so anything cleared before it starts is
#: already gone in frame 0. The viewer then sees the full previous slide, a
#: near-empty one, and the content animating back — a visible flicker on every
#: beat change. The cure is to let the outgoing beat leave *inside* the new
#: video, which makes frame 0 match the previous slide's last frame.
HANDOFF_TOLERANCE = 3.0


def check_handoffs(scenes: list[str]) -> list[C.Finding]:
    """Compare each slide's first frame with the previous slide's last frame."""
    import json
    import subprocess
    import tempfile

    import numpy as np
    from PIL import Image

    findings: list[C.Finding] = []
    for scene in scenes:
        config = REPO / "slides" / f"{scene}.json"
        if not config.exists():
            continue
        slides = json.loads(config.read_text())["slides"]
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)

            def grab(video: Path, last: bool) -> "np.ndarray | None":
                out = tmp / ("last.png" if last else "first.png")
                cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video)]
                if last:
                    cmd += ["-vf", "reverse"]
                cmd += ["-frames:v", "1", "-update", "1", str(out)]
                if subprocess.run(cmd, capture_output=True).returncode or not out.exists():
                    return None
                return np.asarray(Image.open(out).convert("RGB"), dtype=float)

            for index in range(1, len(slides)):
                before = grab(REPO / slides[index - 1]["file"], last=True)
                after = grab(REPO / slides[index]["file"], last=False)
                if before is None or after is None:
                    continue
                diff = float(np.abs(before - after).mean())
                if diff > HANDOFF_TOLERANCE:
                    findings.append(C.Finding(
                        "warn", "",
                        f"{scene} slide {index} -> {index + 1}: the new slide starts "
                        f"{diff:.1f} away from where the last one ended. A slide that "
                        "clears before its video begins flickers on every beat change; "
                        "let the outgoing beat leave inside the new video instead."))
    return findings


# ── driver ───────────────────────────────────────────────────────────────────

def review(screenplay: Path, frames_dir: Path | None,
           scenes: list[str] | None = None) -> Report:
    deck = load(screenplay)
    C.scene_groups(deck)                     # assigns display numbers
    findings = list(C.validate(deck))
    model, slide_counts, boxes = check_model(deck)
    findings += model
    if scenes:
        findings += check_handoffs(scenes)
    if frames_dir:
        findings += check_pixels(deck, frames_dir, slide_counts, boxes)

    skipped = []
    if not T.accent_meanings_assigned():
        skipped.append(
            "accent consistency — a meaning is unassigned in identity/tokens.yaml, "
            "so there is nothing to check 'used for its assigned meaning' against. "
            "Generated beats that use an accent are refused above until it is set.")
    else:
        skipped.append(
            "accent consistency — judgement, not pixels. green: "
            f"{PALETTE.green.meaning.strip()} yellow: "
            f"{PALETTE.yellow.meaning.strip()} Check on the sheets that every "
            "accented mark fits, and that no beat uses yellow without a green.")
    skipped.append(
        "does the frame match its Claim, and does it look right — judgement, not "
        "pixels. Build the contact sheets and LOOK at every one:\n"
        f"      uv run python scripts/contact_sheet.py --frames {frames_dir} "
        f"--deck {screenplay}")
    return Report(findings, skipped)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("screenplay", type=Path)
    parser.add_argument("--frames", type=Path, default=None,
                        help="directory of frames from extract_frames.py")
    parser.add_argument("--scenes", nargs="*", default=None,
                        help="rendered scene names, to check slide hand-offs for flicker")
    args = parser.parse_args()

    report = review(args.screenplay, args.frames, args.scenes)
    for level in ("error", "warn", "note"):
        group = report.by_level(level)
        if group:
            print(f"\n{level.upper()} ({len(group)})")
            for finding in group:
                print(f"  {finding}")
    if report.skipped:
        print("\nNOT CHECKED")
        for reason in report.skipped:
            print(f"  - {reason}")

    errors = len(report.by_level("error"))
    print(f"\n{errors} error(s), {len(report.by_level('warn'))} warning(s)")
    print("A clean run here means nothing is measurably broken. It does not mean "
          "the deck reads well —\nno check above can see a slide that is correct "
          "in every dimension and still badly formatted.")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
