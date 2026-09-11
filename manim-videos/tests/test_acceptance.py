"""The acceptance tests from the plan, §8.

Numbered to match. Tests 2, 8, 10, 13 and 15 are the strict ones: they map onto
the five failure modes this design exists to prevent — silent overflow,
mismatched colour pairs, the agent improving the human's words, a slide that is
correct in code and unreadable on screen, and a revision pass eating the
human's edits.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from presenting_lib import brief as brief_mod
from presenting_lib import compile as C
from presenting_lib import revise, screenplay as sp, shots
from presenting_lib.errors import (
    ColourPairingError,
    LayoutContractError,
    SlotOverflow,
)
from presenting_lib.layouts import Content, catalog, get_layout
from presenting_lib.placeholders import VisualSpec
from presenting_lib.slots import Slot
from presenting_lib.tokens import GREEN, PALETTE, T

REPO = Path(__file__).resolve().parent.parent


# ── 1. ft_v2 port ────────────────────────────────────────────────────────────

def test_01_ft_v2_port_compiles_and_every_beat_builds(ft_v2_deck, tmp_path):
    out, findings = C.compile_deck(REPO / "decks" / "ft-v2" / "screenplay.md",
                                   tmp_path / "scenes.py")
    assert not [f for f in findings if f.level == "error"], findings

    source = out.read_text()
    for banned in (".next_to(", ".shift(", "font_size=", ".to_edge("):
        assert banned not in source, f"generated file does manual positioning: {banned}"

    C.scene_groups(ft_v2_deck)
    for number, beat in enumerate(ft_v2_deck.main_beats(), start=1):
        if beat.is_raw():
            continue
        layout = C.layout_for(beat)
        layout.build(C.content_for(beat, ft_v2_deck, number=number),
                     target=ft_v2_deck.target)


def test_01b_known_good_sample_still_present():
    """BeamerDemoPart1 / BowlDescent3D / BeamerDemoPart2 keep rendering."""
    source = (REPO / "scenes" / "beamer_demo.py").read_text()
    for name in ("BeamerDemoPart1", "BowlDescent3D", "BeamerDemoPart2"):
        assert f"class {name}" in source


# ── 2. Overflow (strict) ─────────────────────────────────────────────────────

def test_02_overflow_names_the_slot_and_the_budget():
    layout = get_layout("claim-above-figure")
    with pytest.raises(SlotOverflow) as excinfo:
        layout.build(Content(claim="x" * 300, title="t"))
    message = str(excinfo.value)
    assert "claim" in message
    assert "300 chars" in message
    assert excinfo.value.slot_name == "claim"
    budget = json.loads((REPO / "identity" / "budgets.json").read_text())
    assert str(budget["manim"]["claim-above-figure"]["claim"]) in message


def test_02b_overflow_is_raised_not_rendered_off_frame():
    tiny = Slot("tiny", 0.0, 0.0, 1.2, 0.4, style="body")
    with pytest.raises(SlotOverflow):
        tiny.fit_text("a sentence that cannot possibly fit in a slot this small")


# ── 3. Empty deck ────────────────────────────────────────────────────────────

def test_03_deck_with_zero_assets_still_builds(tmp_deck):
    deck = tmp_deck(EMPTY_DECK)
    C.scene_groups(deck)
    for number, beat in enumerate(deck.main_beats(), start=1):
        layout = C.layout_for(beat)
        built = layout.build(C.content_for(beat, deck, number=number,
                                           deck_dir=deck.path.parent))
        assert built.steps


# ── 4. Budgets ───────────────────────────────────────────────────────────────

def test_04_every_text_slot_has_a_budget_per_target():
    """Both targets. The slides target has no renderer — its script is written
    per deck by the `render-slides` skill — but it still reads these."""
    budgets = json.loads((REPO / "identity" / "budgets.json").read_text())
    assert set(budgets) == {"manim", "pptx"}
    for name, layout in catalog().items():
        for slot_name in layout.measured_text_slots():
            for target in ("manim", "pptx"):
                value = budgets[target].get(name, {}).get(slot_name)
                assert isinstance(value, int) and value > 0, (target, name, slot_name)


# ── 5. Time ──────────────────────────────────────────────────────────────────

def test_05_overrun_is_flagged_with_demotion_candidates(tmp_deck):
    beats = "\n".join(BEAT_TEMPLATE.format(i=i, time=60) for i in range(30))
    deck = tmp_deck(TIME_DECK.format(beats=beats))
    findings = C.validate(deck)
    time_findings = [f for f in findings if "min slot" in f.message]
    assert time_findings, findings
    message = time_findings[0].message
    assert "Demotion candidates" in message
    assert "Demote, do not delete" in message


# ── 6. Target split ──────────────────────────────────────────────────────────

def test_06_shot_list_is_a_function_of_the_target(tmp_deck):
    deck = tmp_deck(SPLIT_DECK)
    deck.meta["target"] = "manim"
    for_manim = shots.shots_for(deck)
    deck.meta["target"] = "slides"
    for_slides = shots.shots_for(deck)

    assert len(for_manim) == 3, [s.beat_id for s in for_manim]
    assert len(for_slides) > len(for_manim)
    # Constructible visuals are free on manim and an ask on slides.
    assert {s.beat_id for s in for_slides} - {s.beat_id for s in for_manim}


# ── 7. Identity ──────────────────────────────────────────────────────────────

def test_07_changing_a_token_changes_every_export(tmp_path, monkeypatch):
    tokens_path = REPO / "identity" / "tokens.yaml"
    original = tokens_path.read_text()
    new_green = "#0055AA"
    try:
        tokens_path.write_text(original.replace('mid:    "#3D6349"',
                                                f'mid:    "{new_green}"'))
        for script in ("export_beamer.py", "export_matplotlib.py",
                       "export_drawio.py", "export_revealjs.py"):
            result = subprocess.run(
                [".venv/bin/python", f"identity/{script}"],
                cwd=REPO, capture_output=True, text=True)
            assert result.returncode == 0, f"{script}: {result.stderr[-800:]}"

        body = new_green.lstrip("#").upper()
        out = REPO / "identity" / "out"
        # beamer writes bare hex, mplstyle writes it bare inside the cycler (a
        # leading # there is stripped as a comment), drawio writes it with the #.
        assert body in (out / "presenting.sty").read_text().upper()
        assert body in (out / "presenting.mplstyle").read_text().upper()
        assert body in (out / "drawio-styles.md").read_text().upper()

        # The reveal.js template carries only the ground — it exists to paint
        # the page behind the slides, not the palette — so it is checked against
        # the token it is actually responsible for.
        ground = T.palette.ground.lstrip("#").upper()
        assert ground in (out / "revealjs.html").read_text().upper()
    finally:
        tokens_path.write_text(original)
        for script in ("export_beamer.py", "export_matplotlib.py",
                       "export_drawio.py", "export_revealjs.py"):
            subprocess.run([".venv/bin/python", f"identity/{script}"],
                           cwd=REPO, capture_output=True, text=True)


# ── 8. Pairing (strict) ──────────────────────────────────────────────────────

def test_08_green_tint_with_ink_raises():
    with pytest.raises(ColourPairingError):
        GREEN.check_text_colour(PALETTE.ink)


def test_08b_accent_fill_carries_its_own_dark():
    assert GREEN.check_text_colour(None) == PALETTE.green.dark
    assert PALETTE.YELLOW.check_text_colour(None) == PALETTE.yellow.dark
    assert PALETTE.STRUCTURE.check_text_colour(None) == PALETTE.ink


def test_08c_there_is_no_third_accent():
    with pytest.raises(ColourPairingError):
        PALETTE.accent("blue")


def test_08d_slot_refuses_a_mismatched_text_colour():
    slot = Slot("s", 0.0, 0.0, 6.0, 1.0, style="body")
    with pytest.raises(ColourPairingError):
        slot.fit_text("hello", on=GREEN, color=PALETTE.ink)


# ── 9. Whiteboard ────────────────────────────────────────────────────────────

def test_09_brief_skill_separates_transcription_from_interpretation():
    skill = (REPO.parent / "plugins" / "presenting-manim" / "skills"
             / "presentation-brief" / "SKILL.md").read_text().lower()
    transcribe = skill.index("transcribe")
    interpret = skill.index("interpret")
    assert transcribe < interpret, "interpretation must come after transcription"
    assert "unreadable" in skill
    assert "never guess" in skill


# ── 10. Verbatim (strict) ────────────────────────────────────────────────────

def test_10_note_and_cue_survive_a_round_trip_byte_for_byte(ft_v2_deck):
    dumped = sp.dump(ft_v2_deck)
    reparsed = sp.parse(dumped)
    for before, after in zip(ft_v2_deck.beats(), reparsed.beats()):
        assert before.id == after.id
        assert before.note == after.note, before.id
        assert before.cue == after.cue, before.id
    assert sp.dump(reparsed) == dumped


def test_10b_multiline_note_is_not_rewrapped(tmp_deck):
    deck = tmp_deck(VERBATIM_DECK)
    note = deck.beat("verbatim").note
    assert note == "1. first line\n2. second line\n    a. indented sub-item"
    assert deck.beat("verbatim").cue == "x/0 / the pizza thing"
    again = sp.parse(sp.dump(deck)).beat("verbatim")
    assert again.note == note
    assert again.cue == deck.beat("verbatim").cue


# ── 11. Chrome ───────────────────────────────────────────────────────────────

def test_11_full_bleed_figure_has_no_footer_and_no_dots():
    layout = get_layout("full-bleed-figure")
    built = layout.build(Content(visual=VisualSpec(kind="constructible",
                                                   intent="anything")))
    assert built.chrome == "none"
    assert built.title is None


def test_11b_chrome_tier_is_a_property_of_the_layout():
    expected = {"title-card": "bare", "section-break": "bare", "claim-only": "bare",
                "callout": "bare", "discussion": "bare",
                "full-bleed-figure": "none", "claim-above-figure": "full"}
    for name, tier in expected.items():
        assert get_layout(name).chrome == tier, name


def test_11c_dots_count_sections_not_beats():
    from presenting_lib.chrome import progress_dots

    assert len(progress_dots(5, 2)) == 5


# ── 12. Genre gate ───────────────────────────────────────────────────────────

def test_12_showcase_never_gets_a_discussion_beat(tmp_deck):
    deck = tmp_deck(SHOWCASE_DECK, brief=SHOWCASE_BRIEF)
    findings = C.validate(deck)
    errors = [f for f in findings if f.level == "error" and "discussion" in f.message]
    assert errors, findings
    assert "failed showcase" in errors[0].message


def test_12b_genre_rules_match_the_plan():
    assert not brief_mod.RULES["showcase"].discussion
    assert brief_mod.RULES["research-talk"].discussion
    assert brief_mod.RULES["tutorial"].activities
    assert not brief_mod.RULES["defense"].discussion


# ── 13. Review (strict) ──────────────────────────────────────────────────────

def test_13_review_catches_a_planted_overflow(tmp_deck):
    import scripts.review_deck as review

    deck = tmp_deck(OVERFLOW_DECK)
    findings, _, _ = review.check_model(deck)
    errors = [f for f in findings if f.level == "error"]
    assert errors, findings
    assert "SlotOverflow" in errors[0].message


def test_13b_review_catches_a_planted_low_contrast_label(tmp_path):
    import numpy as np
    from PIL import Image

    import scripts.review_deck as review

    ground = tuple(int(PALETTE.ground.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    # Text drawn in a colour a hair off the ground: correct in code, invisible
    # on screen. This is the exact failure that only pixels catch.
    invisible = tuple(min(c + 6, 255) for c in ground)
    readable = tuple(int(PALETTE.ink.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))

    for colour, should_flag in ((invisible, True), (readable, False)):
        pixels = np.full((480, 854, 3), ground, dtype=np.uint8)
        for row in range(200, 240, 6):                 # a few glyph-ish strokes
            pixels[row:row + 3, 300:560] = colour
        path = tmp_path / f"frame-{should_flag}.png"
        Image.fromarray(pixels).save(path)

        box = (-2.0, -0.6, 2.0, 0.6)                   # frame coords over that band
        issues = review.check_frame(path, boxes=[("claim", box)],
                                    allow_offpalette=True)
        flagged = any("light-on-light" in issue for issue in issues)
        assert flagged is should_flag, (should_flag, issues)


def test_13c_accent_check_is_skipped_while_meanings_are_unassigned():
    import scripts.review_deck as review

    report = review.review(REPO / "decks" / "ft-v2" / "screenplay.md", None)
    if not T.accent_meanings_assigned():
        assert any("accent consistency" in s for s in report.skipped)


# ── 14. Reorder ──────────────────────────────────────────────────────────────

def test_14_moving_a_beat_changes_no_id_and_no_asset_path(tmp_deck):
    deck = tmp_deck(SPLIT_DECK)
    before = {s.beat_id: s.save_to for s in shots.shots_for(deck)}
    ids_before = [b.id for b in deck.beats()]

    section = deck.sections[0]
    section.beats.append(section.beats.pop(0))       # move the first beat last

    after = {s.beat_id: s.save_to for s in shots.shots_for(deck)}
    assert before == after
    assert sorted(ids_before) == sorted(b.id for b in deck.beats())
    # Display numbering is derived from position and is expected to move.
    C.scene_groups(deck)
    assert [b.id for b in deck.beats()] != ids_before


# ── 15. Provenance (strict) ──────────────────────────────────────────────────

def test_15_scoped_revision_leaves_human_beats_untouched(tmp_deck):
    deck = tmp_deck(PROVENANCE_DECK)
    human_before = sp.dump(deck).count("origin: human")
    original = deck.beat("mine").claim

    proposed = [
        sp.Beat(id="mine", layout="claim-only", claim="REWRITTEN", origin="generated"),
        sp.Beat(id="fresh", layout="claim-only", claim="new beat", origin="generated"),
    ]
    report = revise.replace_section(deck, "Only section", proposed)

    assert deck.beat("mine").claim == original, "a human beat was overwritten"
    assert deck.beat("mine").origin == "human"
    assert any(c.kind == "kept" for c in report.changes)
    assert report.proposals and report.proposals[0].claim == "REWRITTEN"
    assert deck.beat("fresh").claim == "new beat"
    assert sp.dump(deck).count("origin: human") == human_before


def test_15b_generated_beats_are_replaced_freely(tmp_deck):
    deck = tmp_deck(PROVENANCE_DECK)
    proposed = [sp.Beat(id="theirs", layout="claim-only", claim="REWRITTEN")]
    revise.replace_section(deck, "Only section", proposed)
    assert deck.beat("theirs").claim == "REWRITTEN"


# ── 16. Demotion ─────────────────────────────────────────────────────────────

def test_16_demoted_beat_keeps_its_reason_and_moves_after_the_outro(tmp_deck):
    deck = tmp_deck(PROVENANCE_DECK)
    beat = deck.beat("theirs")
    beat.verdict = "demote"
    beat.demoted_because = "really cool but it broke the run into section 4"

    report = revise.apply_verdicts(deck, None)
    assert [c.kind for c in report.changes] == ["demoted"]
    assert beat.backup is True
    assert beat.demoted_because
    assert beat.verdict == ""

    order = [b.id for b in deck.main_beats() + deck.backup_beats()]
    assert order[-1] == "theirs", order
    assert "demoted_because" in sp.dump(deck)


def test_16b_demotion_without_a_reason_is_refused(tmp_deck):
    deck = tmp_deck(PROVENANCE_DECK)
    with pytest.raises(revise.RevisionError):
        revise.demote(deck.beat("theirs"))


# ── 17. Freeze ───────────────────────────────────────────────────────────────

def test_17_frozen_narrative_blocks_narrative_wrong(tmp_deck):
    deck = tmp_deck(PROVENANCE_DECK, brief=FROZEN_BRIEF)
    brief = brief_mod.load(deck.path.parent / "brief.md")
    assert brief.narrative_frozen

    deck.beat("theirs").verdict = "narrative-wrong"
    report = revise.apply_verdicts(deck, brief)
    refused = report.of_kind("refused")
    assert refused, report.changes
    assert "narrative_frozen" in refused[0].detail
    assert deck.beat("theirs").verdict == "narrative-wrong", "verdict was consumed anyway"


def test_17b_unfrozen_narrative_lets_it_through(tmp_deck):
    deck = tmp_deck(PROVENANCE_DECK, brief=FROZEN_BRIEF.replace(
        "narrative_frozen: true", "narrative_frozen: false"))
    brief = brief_mod.load(deck.path.parent / "brief.md")
    deck.beat("theirs").verdict = "narrative-wrong"
    report = revise.apply_verdicts(deck, brief)
    assert report.of_kind("proposed")


# ── 18. Bridge ───────────────────────────────────────────────────────────────

def test_18_missing_bridge_is_reported(tmp_deck):
    deck = tmp_deck(NO_BRIDGE_DECK)
    findings = C.validate(deck)
    bridge = [f for f in findings if "Bridge" in f.message]
    assert bridge, findings
    assert "the order is wrong" in bridge[0].message


def test_18b_every_ft_v2_section_has_a_bridge(ft_v2_deck):
    missing = [s.name for s in ft_v2_deck.sections if not s.bridge]
    assert not missing, missing


# ── extra contract checks ────────────────────────────────────────────────────

def test_layout_refuses_content_it_has_no_slot_for():
    with pytest.raises(LayoutContractError):
        get_layout("claim-only").build(Content(claim="fine", items=["nope"]))


def test_duplicate_beat_ids_are_refused(tmp_deck):
    with pytest.raises(sp.ScreenplayError):
        tmp_deck(DUPLICATE_DECK)


def test_raw_beats_skip_slot_validation_but_still_participate(ft_v2_deck):
    raw = [b for b in ft_v2_deck.beats() if b.is_raw()]
    assert raw
    for beat in raw:
        assert beat.time_s > 0
        assert beat.section
    groups = C.scene_groups(ft_v2_deck)
    assert any(g.kind == "raw" for g in groups)


def test_accents_have_meanings_and_a_beat_may_use_them(tmp_deck):
    assert T.accent_meanings_assigned(), "the accent gate is still blocking decks"
    assert PALETTE.green.require_meaning()
    assert PALETTE.yellow.require_meaning()

    deck = tmp_deck(ACCENT_DECK)
    errors = [f for f in C.validate(deck) if f.level == "error"]
    assert not errors, errors


def test_the_accent_gate_still_fires_if_a_meaning_is_removed(tmp_deck, monkeypatch):
    """The gate is unblocked, not deleted — clearing a meaning re-arms it."""
    from presenting_lib import tokens as tokens_mod

    # Tokens is frozen, so patch the method on the class rather than the value
    # on the instance.
    monkeypatch.setattr(tokens_mod.Tokens, "accent_meanings_assigned",
                        lambda self: False)
    deck = tmp_deck(ACCENT_DECK)
    errors = [f for f in C.validate(deck) if f.level == "error"]
    assert errors and "unassigned" in errors[0].message


def test_a_hand_edit_is_detected_without_anyone_setting_a_flag(tmp_deck):
    """`origin: human` is what protects the user's edits, and remembering to
    set it is exactly the thing a person forgets mid-thought."""
    deck = tmp_deck(PROVENANCE_DECK)
    beat = deck.beat("theirs")
    beat.stamp()
    assert revise.revisable(beat)

    beat.claim = "edited by hand in an editor, with no flag touched"
    assert beat.origin == "generated"          # the flag was never updated
    assert beat.edited_by_hand()
    assert not revise.revisable(beat)

    proposed = [sp.Beat(id="theirs", layout="claim-only", claim="REWRITTEN")]
    revise.replace_section(deck, "Only section", proposed)
    assert deck.beat("theirs").claim.startswith("edited by hand")


def test_an_unstamped_beat_stays_rewritable(tmp_deck):
    """Beats written before fingerprinting existed must not all freeze."""
    deck = tmp_deck(PROVENANCE_DECK)
    beat = deck.beat("theirs")
    assert not beat.generated_hash
    assert revise.revisable(beat)


def test_moving_a_beat_is_not_an_edit(tmp_deck):
    deck = tmp_deck(PROVENANCE_DECK)
    beat = deck.beat("theirs")
    beat.stamp()
    beat.number = 7
    beat.section = "Somewhere else"
    beat.verdict = "keep"
    assert not beat.edited_by_hand()


# ── fixtures ─────────────────────────────────────────────────────────────────

EMPTY_DECK = """---
slug: empty
title: Nothing sourced yet
target: manim
---

# Section 1 — Opening

> **Bridge.** Opening frame.

## 1.1 — A figure we have not found

```yaml
id: unsourced-photo
layout: claim-above-figure
time_s: 60
visual:
  kind: referential
  sub: photo
  intent: a real robot arm being corrected by a person
  asset: does-not-exist.png
```

**Claim.** The correction is physical, not textual.

## 1.2 — A diagram we have not built

```yaml
id: unbuilt-diagram
layout: claim-above-figure
time_s: 60
visual:
  kind: constructible
  sub: process
  intent: the three-stage pipeline, stage two marked
```

**Claim.** Three stages, and only the middle one is contested.

## 1.3 — A chart with no numbers

```yaml
id: no-numbers
layout: claim-above-figure
time_s: 60
visual:
  kind: chart
  intent: proxy reward against gold reward
  source: Gao et al. 2023, figure 3
```

**Claim.** The gap widens with optimisation pressure.
"""

TIME_DECK = """---
slug: overrun
title: Too much
target: manim
duration_min: 20
---

# Section 1 — Everything

> **Bridge.** Opening frame.

{beats}
"""

BEAT_TEMPLATE = """## 1.{i} — Beat {i}

```yaml
id: beat-{i}
layout: claim-only
time_s: {time}
```

**Claim.** A short claim for beat {i}.
"""

SPLIT_DECK = """---
slug: split
title: Target split
target: manim
---

# Section 1 — Only section

> **Bridge.** Opening frame.

## 1.1 — Photo

```yaml
id: a-photo
layout: claim-above-figure
time_s: 60
visual:
  kind: referential
  sub: photo
  intent: a person labelling preferences at a desk
```

**Claim.** Somebody actually sits and does this.

## 1.2 — Paper figure

```yaml
id: a-paper-figure
layout: claim-above-figure
time_s: 60
visual:
  kind: referential
  sub: paper-figure
  intent: figure 3 from the overoptimisation paper
```

**Claim.** The effect is empirical, not asserted.

## 1.3 — Screenshot

```yaml
id: a-screenshot
layout: claim-above-figure
time_s: 60
visual:
  kind: referential
  sub: screenshot
  intent: the annotation tool as the labeller sees it
```

**Claim.** The interface shapes the data.

## 1.4 — A diagram

```yaml
id: a-diagram
layout: claim-above-figure
time_s: 60
visual:
  kind: constructible
  sub: graph
  intent: three items in a preference cycle
```

**Claim.** Preferences can form a cycle.

## 1.5 — Another diagram

```yaml
id: another-diagram
layout: claim-above-figure
time_s: 60
visual:
  kind: constructible
  sub: process
  intent: the three-stage pipeline
```

**Claim.** Three stages, one contested.
"""

VERBATIM_DECK = """---
slug: verbatim
title: Verbatim
target: manim
---

# Section 1 — Only section

> **Bridge.** Opening frame.

## 1.1 — Verbatim

```yaml
id: verbatim
layout: claim-only
time_s: 60
```

**Note.** 1. first line
2. second line
    a. indented sub-item

**Claim.** The human's own words are never rewritten.

**Cue.** x/0 / the pizza thing
"""

SHOWCASE_BRIEF = """---
slug: showcase
target: manim
genre: showcase
technicality: 2
interaction: organic
duration_min: 15
---

## Narrative
They arrive curious. They see the thing work. They leave wanting to try it.
"""

SHOWCASE_DECK = """---
slug: showcase
title: A showcase
target: manim
brief: ./brief.md
---

# Section 1 — Only section

> **Bridge.** Opening frame.

## 1.1 — A prompt

```yaml
id: a-prompt
layout: discussion
time_s: 60
```

**Claim.** Where would this break for you?
"""

OVERFLOW_DECK = """---
slug: overflow
title: Planted overflow
target: manim
---

# Section 1 — Only section

> **Bridge.** Opening frame.

## 1.1 — Too much text

```yaml
id: too-much
layout: claim-above-figure
time_s: 60
content:
  claim: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
```

**Claim.** Planted.
"""

PROVENANCE_DECK = """---
slug: provenance
title: Provenance
target: manim
brief: ./brief.md
---

# Section 1 — Only section

> **Bridge.** Opening frame.

## 1.1 — Theirs

```yaml
id: theirs
origin: generated
layout: claim-only
time_s: 60
```

**Claim.** The agent wrote this one.

## 1.2 — Mine

```yaml
id: mine
origin: human
layout: claim-only
time_s: 60
```

**Claim.** The human wrote this one and it must survive.
"""

FROZEN_BRIEF = """---
slug: provenance
target: manim
genre: research-talk
technicality: 3
interaction: organic
duration_min: 20
narrative_frozen: true
---

## Narrative
Setup, turn, landing.
"""

NO_BRIDGE_DECK = """---
slug: no-bridge
title: No bridge
target: manim
---

# Section 1 — Only section

## 1.1 — A beat

```yaml
id: a-beat
layout: claim-only
time_s: 60
```

**Claim.** Something.
"""

DUPLICATE_DECK = """---
slug: dupes
title: Duplicates
target: manim
---

# Section 1 — One

> **Bridge.** Opening frame.

## 1.1 — First

```yaml
id: same-id
layout: claim-only
time_s: 60
```

**Claim.** First.

# Section 2 — Two

> **Bridge.** And then.

## 2.1 — Second

```yaml
id: same-id
layout: claim-only
time_s: 60
```

**Claim.** Second.
"""

ACCENT_DECK = """---
slug: accents
title: Accents
target: manim
---

# Section 1 — Only section

> **Bridge.** Opening frame.

## 1.1 — Two accents

```yaml
id: two-accents
origin: generated
layout: equation-annotated
time_s: 60
content:
  equation: a + b
  annotations:
    - [the first term, green]
    - [the second term, yellow]
```

**Claim.** Two terms, two accents.
"""
