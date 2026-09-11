"""Build every beat through its layout, without rendering a frame.

`compile.validate` measures text against the character budgets in
identity/budgets.json, which are a proxy. This runs the real thing —
`Slot.fit_text` and the diagram builder — so a slot that overflows shows up in
a second here instead of forty minutes into a render.
"""

from __future__ import annotations

import sys

from presenting_lib import compile as C, screenplay as sp
from presenting_lib.layouts import get_layout


def check(path: str) -> int:
    deck = sp.load(path)
    failures = 0
    for beat in deck.beats():
        if beat.is_raw():
            print(f"skip  {beat.id} (raw)")
            continue
        layout = C.layout_for(beat)
        try:
            content = C.content_for(beat, deck, number=beat.number or 1)
            layout.build(content, target=deck.target)
        except Exception as exc:                     # noqa: BLE001 — report them all
            failures += 1
            print(f"FAIL  {beat.id} [{layout.name}] {type(exc).__name__}: "
                  f"{str(exc).splitlines()[0]}")
        else:
            print(f"ok    {beat.id}")
    print(f"\n{failures} failure(s) of {len(deck.beats())} beats")
    return failures


if __name__ == "__main__":
    sys.exit(1 if check(sys.argv[1]) else 0)
