#!/usr/bin/env python3
"""Pull one settled frame per slide out of a rendered deck.

    uv run python scripts/extract_frames.py FtV2_01_WherePart1LeftOff ...
    uv run python scripts/extract_frames.py --all --out media/review

This is the input to the mechanical half of `deck-review`. It takes the *last*
frame of each slide's video, not the first, because that is the state the
audience actually sits in front of while the presenter talks — the frame where
text being off-frame, unreadable, or colliding actually costs something.

Some defects only exist in pixels. During the identity work a colour was
silently overridden downstream and every label rendered light-on-light: the code
was correct, the slide was unreadable, and nothing but looking at it would have
caught it.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SLIDES_DIR = REPO / "slides"
DEFAULT_OUT = REPO / "media" / "review"


def scene_config(scene: str) -> dict:
    path = SLIDES_DIR / f"{scene}.json"
    if not path.exists():
        raise SystemExit(
            f"no rendered slides for {scene!r} ({path} missing). "
            "Render it first: uv run manim-slides render <module> <Scene> -ql"
        )
    return json.loads(path.read_text())


#: Seek offsets tried in order, seconds before the end. The compiler holds each
#: slide for SETTLE_S after its last animation, so anything inside that window
#: is the state the audience actually sits in front of.
_SEEK_OFFSETS = (0.1, 0.25, 0.5)


def last_frame(video: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    for offset in _SEEK_OFFSETS:
        out.unlink(missing_ok=True)
        result = subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-sseof", f"-{offset}",
             "-i", str(video), "-frames:v", "1", "-update", "1", str(out)],
            capture_output=True, text=True,
        )
        if result.returncode == 0 and out.exists():
            return
    # Nothing near the end decoded — a one-frame clip. Take what there is.
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video),
         "-frames:v", "1", "-update", "1", str(out)],
        check=True, capture_output=True, text=True,
    )


def extract(scene: str, out_dir: Path) -> list[Path]:
    config = scene_config(scene)
    written = []
    for index, slide in enumerate(config["slides"], start=1):
        video = REPO / slide["file"]
        if not video.exists():
            print(f"  missing video for slide {index}: {video}", file=sys.stderr)
            continue
        target = out_dir / f"{scene}-{index:02d}.png"
        last_frame(video, target)
        written.append(target)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenes", nargs="*")
    parser.add_argument("--all", action="store_true",
                        help="every scene with a rendered config in slides/")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    scenes = args.scenes
    if args.all:
        scenes = sorted(p.stem for p in SLIDES_DIR.glob("*.json"))
    if not scenes:
        raise SystemExit("name at least one scene, or pass --all")

    total = 0
    for scene in scenes:
        frames = extract(scene, args.out)
        total += len(frames)
        print(f"{scene}: {len(frames)} frames")
    print(f"\n{total} frames in {args.out.resolve()}")


if __name__ == "__main__":
    main()
