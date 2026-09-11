#!/usr/bin/env python3
"""Measure the character budget of every text slot in every layout.

    uv run python scripts/measure_slots.py              # write identity/budgets.json
    uv run python scripts/measure_slots.py --calibrate  # render the legibility ladder

**Budgets.** For each (target, layout, slot), binary-search the longest string
that still fits at or above the legibility floor. `Slot.fit_text` is the oracle
for the manim target, so the numbers describe exactly what will and will not
raise at compile time rather than an independent guess that could disagree with
it. Strings are built from realistic English word lengths, not lorem — lorem's
words are short and even, which makes every budget optimistic.

The file is keyed by target as well as layout, because manim (Pango, hinted
glyph advances) and pptx (PowerPoint's own metrics) do not measure the same
string the same way, and one set of numbers would be wrong for one of them.

**Calibration.** `--calibrate` renders a descending ladder of font sizes to a
1080p frame. Look at it at arm's length on a laptop — that approximates the
back of a room — and pick the smallest comfortable step. That number goes in
identity/tokens.yaml as `min_legible_body`, with the reasoning, and this script
is how it gets re-derived if the type families change.
"""

from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from presenting_lib.errors import SlotOverflow  # noqa: E402
from presenting_lib.layouts import catalog, get_layout  # noqa: E402
from presenting_lib.measure import metrics, wrap  # noqa: E402
from presenting_lib.slots import floor_size  # noqa: E402
from presenting_lib.tokens import GROUND, TYPE  # noqa: E402

BUDGETS_PATH = REPO / "identity" / "budgets.json"

#: A pool with an English-like length distribution (mean ~4.9 characters,
#: a long tail). Lorem is shorter and flatter and would inflate every budget.
WORDS = (
    "the of and to in a is that for it as with was on be at by this have from "
    "or an they which one you were her all she there would their we him been "
    "has when who will more no if out so said what up its about into than them "
    "can only other new some could time these two may then do first any my now "
    "such like our over man me even most made after also did many before must "
    "through back years where much your way well down should because each just "
    "those people how too little state good very make world still own see men "
    "work long here between both life being under never same another know while "
    "preference transitive assumption reward model policy gradient baseline "
    "distribution annotator classifier objective regularisation evaluation "
    "throughput generalisation approximation representation optimisation"
).split()

#: The pptx target gets a small haircut: PowerPoint autofits rather than
#: failing, so a budget that is slightly tight there costs nothing, while one
#: that is slightly loose shows up as shrunken text nobody asked for.
PPTX_MARGIN = 0.97


def sample_text(length: int, seed: int = 7) -> str:
    rng = random.Random(seed)
    out: list[str] = []
    total = 0
    while total < length:
        word = rng.choice(WORDS)
        out.append(word)
        total += len(word) + 1
    text = " ".join(out)
    return text[:length].rstrip()


def fits_manim(slot, style: str, layout_name: str, text: str) -> bool:
    try:
        slot.fit_text(text, style=style, on=GROUND, layout=layout_name, target="manim")
        return True
    except SlotOverflow:
        return False


def fits_pptx(slot, style: str, text: str) -> bool:
    """Unhinted metrics, same geometry, a conservative margin."""
    floor = floor_size(style)
    size = TYPE.size(style)
    while size >= floor - 1e-9:
        m = metrics(TYPE.family(style), size)
        lines = wrap(text, m, slot.w * PPTX_MARGIN)
        if lines is not None:
            _, height = m.block_size(lines)
            if height <= slot.h:
                return True
        size -= 1.0
    return False


CEILING = 2000


def largest_fitting(predicate, *, high: int = CEILING) -> int:
    lo, hi = 0, high
    if predicate(sample_text(1)) is False:
        return 0
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if predicate(sample_text(mid)):
            lo = mid
        else:
            hi = mid - 1
    return lo


def measure() -> dict:
    budgets: dict[str, dict[str, dict[str, int]]] = {"manim": {}, "pptx": {}}
    for name in sorted(catalog()):
        layout = get_layout(name)
        slot_names = layout.measured_text_slots()
        if not slot_names:
            continue
        for target in ("manim", "pptx"):
            budgets[target].setdefault(name, {})
        for slot_name in slot_names:
            slot = layout.slots[slot_name]
            style = slot.style
            manim_cap = largest_fitting(
                lambda t: fits_manim(slot, style, name, t))
            pptx_cap = largest_fitting(lambda t: fits_pptx(slot, style, t))
            budgets["manim"][name][slot_name] = manim_cap
            budgets["pptx"][name][slot_name] = pptx_cap
            # A budget that lands exactly on the ceiling was not measured, it
            # was truncated — say so rather than shipping the ceiling as a fact.
            saturated = " SATURATED (raise CEILING)" if CEILING in (manim_cap, pptx_cap) else ""
            print(f"  {name:22} {slot_name:14} manim {manim_cap:4}   "
                  f"pptx {pptx_cap:4}{saturated}")
    return budgets


CALIBRATION_SCENE = '''
import sys
sys.path.insert(0, {repo!r})

from manim import Scene, VGroup, Text, config
from presenting_lib.tokens import PALETTE, TYPE

SIZES = {sizes!r}
SAMPLE = "the reward model assumes preferences are transitive"


class LegibilityLadder(Scene):
    def construct(self):
        config.background_color = PALETTE.ground
        self.camera.background_color = PALETTE.ground
        rows = VGroup()
        for size in SIZES:
            label = Text(f"{{size:>3}}  ", font=TYPE.family_mono,
                         font_size=18, color=PALETTE.muted)
            body = Text(SAMPLE, font=TYPE.family_body, font_size=size,
                        color=PALETTE.ink)
            row = VGroup(label, body).arrange(buff=0.25)
            rows.add(row)
        rows.arrange(direction=[0, -1, 0], buff=0.22, aligned_edge=[-1, 0, 0])
        # Never scale: the whole point is that the rendered size matches the
        # number printed beside it. A ladder that quietly shrinks is a ladder
        # that lies about the thing it is being used to decide.
        if rows.height > 7.4:
            raise SystemExit("too many sizes to show at true scale; pass fewer --sizes")
        rows.move_to([0, 0, 0])
        self.add(rows)
'''


def calibrate(sizes: list[int]) -> None:
    scene_path = REPO / "media" / "legibility_ladder.py"
    scene_path.parent.mkdir(parents=True, exist_ok=True)
    scene_path.write_text(CALIBRATION_SCENE.format(repo=str(REPO), sizes=sizes))
    print(f"rendering the ladder for sizes {sizes} ...")
    result = subprocess.run(
        ["uv", "run", "manim", "-s", "-qh", str(scene_path), "LegibilityLadder"],
        cwd=REPO, capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(result.stdout[-2000:])
        print(result.stderr[-2000:])
        raise SystemExit("manim failed to render the calibration frame")
    frames = sorted((REPO / "media" / "images").rglob("LegibilityLadder*.png"))
    print("frame:", frames[-1] if frames else "(not found)")
    print("\nLook at it at arm's length on a laptop. The smallest step still")
    print("comfortable is min_legible_body; record it and the reasoning in")
    print("identity/tokens.yaml and identity/legibility.md.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibrate", action="store_true",
                        help="render the legibility ladder instead of measuring")
    parser.add_argument("--sizes", type=int, nargs="*",
                        default=[34, 30, 28, 26, 24, 22, 20, 18, 16])
    args = parser.parse_args()

    if args.calibrate:
        calibrate(args.sizes)
        return

    print(f"measuring against min_legible_body={TYPE.min_legible_body} "
          f"({TYPE.family_body})")
    budgets = measure()
    BUDGETS_PATH.write_text(json.dumps(budgets, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {BUDGETS_PATH.relative_to(REPO)}")


if __name__ == "__main__":
    main()
