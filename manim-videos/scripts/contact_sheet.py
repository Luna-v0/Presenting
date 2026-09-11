#!/usr/bin/env python3
"""Tile extracted frames into labelled sheets, so a deck can be *looked at*.

    uv run python scripts/contact_sheet.py --frames media/review --out media/sheets
    uv run python scripts/contact_sheet.py --frames media/review --deck decks/ft-v2/screenplay.md

The mechanical review pass cannot answer "does this frame match its Claim", or
"is this well formatted" — those need eyes. Opening 54 frames one at a time is
enough friction that nobody does it, so this puts six to a sheet with the beat
id and slide number burned into each tile.

Whoever is reviewing — a person or an agent — should look at every sheet. It is
the only pass that catches a slide which is correct in code, passes every
geometric check, and still reads badly.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

GUTTER = 14
LABEL_H = 26
COLS, ROWS = 3, 2


def _font(size: int):
    from matplotlib import font_manager as fm

    try:
        return ImageFont.truetype(
            fm.findfont(fm.FontProperties(family="DejaVu Sans")), size)
    except Exception:                                   # pragma: no cover
        return ImageFont.load_default()


def labels_for(deck_path: Path | None, frames: list[Path]) -> dict[str, str]:
    """frame stem -> "beat-id · Claim", when a screenplay is available."""
    if deck_path is None:
        return {}
    from presenting_lib import compile as C
    from presenting_lib.screenplay import load

    deck = load(deck_path)
    C.scene_groups(deck)
    import scripts.review_deck as review

    _, slide_counts, _ = review.check_model(deck)
    per_scene = review.frame_beat_map(deck, slide_counts)

    by_scene: dict[str, list[Path]] = {}
    for path in frames:
        by_scene.setdefault(path.stem.rsplit("-", 1)[0], []).append(path)

    out: dict[str, str] = {}
    for scene, scene_frames in by_scene.items():
        entries = per_scene.get(scene) or []
        if len(entries) != len(scene_frames):
            continue
        for path, (beat_id, _) in zip(sorted(scene_frames), entries):
            beat = deck.beat(beat_id)
            claim = (beat.claim or " / ".join(beat.on_slide) or "").strip()
            out[path.stem] = f"{beat_id} · {claim}" if claim else beat_id
    return out


def build(frames: list[Path], out_dir: Path, labels: dict[str, str],
          *, tile_w: int = 640) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    font = _font(13)
    small = _font(11)
    written = []

    per_sheet = COLS * ROWS
    for index in range(0, len(frames), per_sheet):
        batch = frames[index:index + per_sheet]
        sample = Image.open(batch[0])
        tile_h = int(tile_w * sample.height / sample.width)
        cell_h = tile_h + LABEL_H

        sheet = Image.new(
            "RGB",
            (COLS * tile_w + (COLS + 1) * GUTTER,
             ROWS * cell_h + (ROWS + 1) * GUTTER),
            (245, 243, 236),
        )
        draw = ImageDraw.Draw(sheet)

        for position, path in enumerate(batch):
            col, row = position % COLS, position // COLS
            x = GUTTER + col * (tile_w + GUTTER)
            y = GUTTER + row * (cell_h + GUTTER)
            tile = Image.open(path).convert("RGB").resize((tile_w, tile_h))
            sheet.paste(tile, (x, y))
            draw.rectangle([x, y, x + tile_w - 1, y + tile_h - 1],
                           outline=(190, 185, 170))
            draw.text((x + 2, y + tile_h + 3), path.stem, font=small,
                      fill=(110, 105, 90))
            caption = labels.get(path.stem, "")
            if caption:
                draw.text((x + 2, y + tile_h + 14), caption[:96], font=font,
                          fill=(35, 42, 36))

        target = out_dir / f"sheet-{index // per_sheet + 1:02d}.png"
        sheet.save(target)
        written.append(target)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--deck", type=Path, default=None,
                        help="screenplay, to label each tile with its beat id and Claim")
    args = parser.parse_args()

    frames = sorted(args.frames.glob("*.png"))
    if not frames:
        raise SystemExit(f"no frames in {args.frames}")

    out_dir = args.out or (args.frames.parent / f"{args.frames.name}-sheets")
    sheets = build(frames, out_dir, labels_for(args.deck, frames))
    for sheet in sheets:
        print(sheet)
    print(f"\n{len(frames)} frames on {len(sheets)} sheet(s). Look at every one.")


if __name__ == "__main__":
    main()
