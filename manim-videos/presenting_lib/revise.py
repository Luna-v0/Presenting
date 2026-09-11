"""The revision loop: verdicts, demotion, scoped revision, and the freeze.

The human forms judgement about whether a talk works by watching it back, not
by reading a plan. This module is the return path for that judgement — the
mechanics only. Deciding *what* a revised section should say is the screenplay
skill's job; deciding what may be touched is this module's.

Three rules do the load-bearing work:

* **Demotion, not deletion.** The most common review reaction is "this part is
  really cool but it didn't fit the narrative" — a conflict, not a defect.
  Deleting means killing something the human likes, which they resist, and the
  usual result is bending the story to keep the beat. A demoted beat is still
  there, still theirs, and available next talk.
* **`origin: human` is never overwritten silently.** Without that, the second
  revision pass eats the fixes from the first and the loop is unusable after
  one round.
* **`narrative_frozen` blocks `narrative-wrong`.** A loop that always invites
  another pass is one you never ship from.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .brief import Brief
from .errors import PresentingError
from .screenplay import Beat, Deck, Section


class RevisionError(PresentingError):
    """A revision was refused, and the message says what would unblock it."""


@dataclass
class Change:
    kind: str            # demoted | kept | replaced | inserted | dropped | proposed | refused
    beat_id: str
    detail: str = ""

    def __str__(self) -> str:
        return f"{self.kind:9} {self.beat_id:24} {self.detail}"


@dataclass
class RevisionReport:
    changes: list[Change] = field(default_factory=list)
    proposals: list[Beat] = field(default_factory=list)

    def add(self, kind: str, beat_id: str, detail: str = "") -> None:
        self.changes.append(Change(kind, beat_id, detail))

    def of_kind(self, kind: str) -> list[Change]:
        return [c for c in self.changes if c.kind == kind]


# ── verdicts ─────────────────────────────────────────────────────────────────

def apply_verdicts(deck: Deck, brief: Brief | None = None) -> RevisionReport:
    """Consume the verdicts a review wrote onto beats.

    `keep` clears. `demote` moves the beat to backup. `narrative-wrong` is the
    only verdict that reopens the brief, and it is refused outright while the
    narrative is frozen — unfreezing has to be a deliberate act, not a drift.
    """
    report = RevisionReport()
    frozen = bool(brief and brief.narrative_frozen)

    for beat in deck.beats():
        verdict = beat.verdict
        if not verdict:
            continue
        if verdict == "keep":
            beat.verdict = ""
            report.add("kept", beat.id)
        elif verdict == "demote":
            demote(beat, beat.demoted_because)
            report.add("demoted", beat.id, beat.demoted_because or "(no reason recorded)")
        elif verdict == "narrative-wrong":
            if frozen:
                report.add(
                    "refused", beat.id,
                    "narrative-wrong, but narrative_frozen: true. The beat is right "
                    "and the story is wrong — that reopens the brief, which is a "
                    "deliberate act. Set narrative_frozen: false to act on it.")
            else:
                report.add(
                    "proposed", beat.id,
                    "narrative-wrong — reopen the brief's Narrative before touching "
                    "any more beats. Everything downstream of the story is stale.")
    return report


def demote(beat: Beat, because: str = "") -> Beat:
    """Mark a beat as backup, keeping it where it is in the file.

    It stays in its own section so the screenplay still reads in narrative
    order; only the render order moves it after the outro. `demoted_because` is
    recorded in the human's framing, because that sentence is what makes the
    beat retrievable next talk.
    """
    beat.backup = True
    beat.verdict = ""
    if because:
        beat.demoted_because = because
    if not beat.demoted_because:
        raise RevisionError(
            f"beat {beat.id!r} demoted with no reason. Record why, in the human's "
            "own words — 'cool but it broke the flow into section 4' — or the beat "
            "is unfindable when there is room for it next time.")
    return beat


def promote(beat: Beat) -> Beat:
    """Bring a backup beat back into the deck."""
    beat.backup = False
    beat.demoted_because = ""
    return beat


# ── scoped revision ──────────────────────────────────────────────────────────

def revisable(beat: Beat) -> bool:
    """May a revision pass rewrite this beat outright?

    Not just the `origin` flag. A beat generated and then edited in an editor
    still *says* `generated`, and rewriting it would eat the edit — which is
    the failure this whole distinction exists to prevent. So the content is
    fingerprinted when generated, and anything that no longer matches has been
    touched by a person whether or not they remembered to say so.
    """
    return not beat.edited_by_hand()


def section_scope(deck: Deck, section_name: str) -> Section:
    for section in deck.sections:
        if section.name == section_name:
            return section
    raise RevisionError(
        f"no section {section_name!r}. Sections are {deck.section_names()}. "
        "Revision is section-scoped because sections are the narrative's joints.")


def replace_section(deck: Deck, section_name: str, proposed: list[Beat], *,
                    bridge: str | None = None) -> RevisionReport:
    """Rewrite one section's generated beats, leaving human beats alone.

    Human beats keep their position and their content. A proposal that collides
    with one is recorded rather than applied — the skill shows it to the human
    and they decide.
    """
    section = section_scope(deck, section_name)
    report = RevisionReport()
    existing = {b.id: b for b in section.beats}
    human_ids = {b.id for b in section.beats if not revisable(b)}
    edited = {b.id for b in section.beats
              if b.origin == "generated" and b.edited_by_hand()}
    proposed_ids = {b.id for b in proposed}

    merged: list[Beat] = []
    for beat in proposed:
        if beat.id in human_ids:
            why = ("edited by hand since it was generated"
                   if beat.id in edited else "origin: human")
            report.add("kept", beat.id, f"{why} — proposal recorded, not applied")
            report.proposals.append(beat)
            merged.append(existing[beat.id])
            continue
        beat.section = section_name
        beat.stamp()
        if beat.id in existing:
            report.add("replaced", beat.id)
        else:
            report.add("inserted", beat.id)
        merged.append(beat)

    for beat in section.beats:
        if beat.id in proposed_ids:
            continue
        if beat.id in human_ids:
            report.add("kept", beat.id,
                       "not in the proposal and not ours to drop — kept")
            merged.append(beat)
        else:
            report.add("dropped", beat.id)

    section.beats = merged
    if bridge is not None:
        section.bridge = bridge
    return report


def mark_human(beat: Beat) -> Beat:
    """Flip a beat to `origin: human`.

    Called whenever the human dictates content for a beat. It is not
    auto-detected — see plan §11.6, which is honest that this is the weakest
    part of the design and worth revisiting once the loop has been used.
    """
    beat.origin = "human"
    return beat
