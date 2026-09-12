"""Keep deck photos at a renderable size, automatically.

manim resamples every source pixel of an ImageMobject on every frame and
ignores the size the image is finally drawn at, so one oversized photo inside
a FadeIn can cost more than a whole section of text slides. Measured on this
machine: a 2551px-wide PNG ran at 8.8 seconds per frame; the same photo at
1600px ran at 18.8 frames per second. Nothing above ~1600px on the long edge
buys anything visible at presentation size.

`normalize_images` runs on every compile. An oversized image in `assets/raw/`
is moved to `assets/raw/_full/` untouched and a downscaled copy takes its
place, so screenplay paths keep working and the original is never lost.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

LONG_EDGE_LIMIT = 1600
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg")


@dataclass
class Downscaled:
    name: str
    old_size: tuple[int, int]
    new_size: tuple[int, int]

    def __str__(self) -> str:
        return (f"{self.name}: {self.old_size[0]}x{self.old_size[1]} -> "
                f"{self.new_size[0]}x{self.new_size[1]} (original in _full/)")


def normalize_images(deck_dir: Path | str, limit: int = LONG_EDGE_LIMIT) -> list[Downscaled]:
    """Downscale every image in `<deck_dir>/assets/raw` whose long edge exceeds `limit`.

    The full-size file moves to `assets/raw/_full/<name>` first; if a backup of
    that name already exists it is replaced, because the oversized file in raw/
    is the current version of the image and a stale backup would not match it.
    """
    from PIL import Image

    raw = Path(deck_dir) / "assets" / "raw"
    if not raw.is_dir():
        return []
    done: list[Downscaled] = []
    for path in sorted(raw.iterdir()):
        if path.is_dir() or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        try:
            with Image.open(path) as image:
                width, height = image.size
                if max(width, height) <= limit:
                    continue
                scale = limit / max(width, height)
                new_size = (max(1, round(width * scale)), max(1, round(height * scale)))
                resized = image.resize(new_size, Image.LANCZOS)
        except OSError:
            continue                       # not actually an image; leave it alone
        full = raw / "_full"
        full.mkdir(exist_ok=True)
        path.replace(full / path.name)
        resized.save(path)
        done.append(Downscaled(path.name, (width, height), new_size))
    return done
