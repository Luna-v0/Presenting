"""Chrome: title, rule, footer, progress dots.

Chrome is a property of the *layout*, not a per-slide decision, so a deck
cannot drift into having a footer on some beats and not others for no reason.
Three tiers:

    full   centered title, green rule beneath, footer
    bare   content only
    none   nothing at all — the full-bleed case

Two consequences the compiler depends on. The footer is *persistent*: one
mobject that survives `next_slide()` and mutates only when the section changes,
never rebuilt per beat. And a `none`-tier beat has to actually clear it, so the
compiler needs the tier per beat in order to animate chrome out and back.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Circle,
    FadeIn,
    FadeOut,
    Line,
    VGroup,
)

from .slots import Slot
from .tokens import GEOMETRY, GROUND, MUTED, PALETTE, TYPE

FULL, BARE, FOOTER, NONE = "full", "bare", "footer", "none"
#: `footer` is `bare` plus the footer: a slide that owns its whole frame but
#: still says where in the deck it sits. A one-sentence claim and a section
#: divider both want that — they are not figures that need the full frame.
TIERS = (FULL, BARE, FOOTER, NONE)

# Bands, in frame coordinates. The content slot each layout gets depends on
# which of these are occupied.
_TOP = GEOMETRY.frame_height / 2 - GEOMETRY.safe_inset          #  3.4
_BOTTOM = -_TOP                                                 # -3.4
_HALF_W = GEOMETRY.frame_width / 2 - GEOMETRY.safe_inset        #  6.51

TITLE_SLOT = Slot("title", 0.0, _TOP - 0.42, 12.0, 0.84, role="text",
                  align="center", style="title")
RULE_Y = TITLE_SLOT.bottom - 0.16

#: Below the safe inset on purpose. That inset protects *content* from
#: projector overscan; the footer is chrome, and pushing it down to the edge
#: keeps it out of the way of the slide and gives the content band the room.
#: Still ~0.5 units clear of the frame edge, so it never actually clips.
FOOTER_Y = -GEOMETRY.frame_height / 2 + 0.48

CONTENT_FULL = Slot(
    "content", 0.0,
    (RULE_Y - 0.28 + FOOTER_Y + 0.28) / 2,
    2 * _HALF_W,
    (RULE_Y - 0.28) - (FOOTER_Y + 0.28),
    role="mixed",
)
CONTENT_BARE = Slot("content", 0.0, 0.0, 2 * _HALF_W, 2 * _TOP, role="mixed")
CONTENT_FOOTER = Slot(
    "content", 0.0, (_TOP + FOOTER_Y + 0.28) / 2,
    2 * _HALF_W, _TOP - (FOOTER_Y + 0.28), role="mixed")
CONTENT_NONE = Slot("content", 0.0, 0.0, GEOMETRY.frame_width, GEOMETRY.frame_height,
                    role="visual")

CONTENT_BY_TIER = {FULL: CONTENT_FULL, BARE: CONTENT_BARE,
                   FOOTER: CONTENT_FOOTER, NONE: CONTENT_NONE}


@dataclass
class DeckMeta:
    """What the chrome needs to know about the deck as a whole."""

    title: str = ""
    sections: list[str] = field(default_factory=list)

    def index_of(self, section: str) -> int:
        return self.sections.index(section) if section in self.sections else 0


def title_block(text: str, *, layout: str | None = None, target: str = "manim") -> VGroup:
    """Centered title with the green rule beneath it.

    The rule tracks the title's width, so a short title gets a short rule and
    the pair reads as one object. The title sits on sand — there is no dark
    band, and no light text anywhere in this identity.
    """
    label = TITLE_SLOT.fit_text(text, style="title", on=GROUND, weight="BOLD",
                                layout=layout, target=target)
    width = min(max(label.width + 0.6, 2.4), 2 * _HALF_W)
    # Under the *rendered* title, not under the slot. A title that wraps to two
    # lines is exactly when a fixed rule y draws a line through the text.
    y = min(RULE_Y, label.get_bottom()[1] - 0.16)
    rule = Line(
        np.array([-width / 2, y, 0.0]),
        np.array([width / 2, y, 0.0]),
        color=PALETTE.green.mid,
        stroke_width=GEOMETRY.stroke_weight,
    )
    return VGroup(label, rule)


def progress_dots(total: int, current: int) -> VGroup:
    """One dot per *section*, not per beat.

    Thirty beats is noise; five sections is a glance. Past dots are filled in
    structure stroke, the current one is filled green and slightly larger,
    future ones are hollow. Position is carried by the slide number next to it.
    """
    dots = VGroup()
    for i in range(max(total, 1)):
        if i < current:
            dot = Circle(radius=0.039, stroke_width=0,
                         fill_color=PALETTE.structure_stroke, fill_opacity=1.0)
        elif i == current:
            dot = Circle(radius=0.056, stroke_width=0,
                         fill_color=PALETTE.green.mid, fill_opacity=1.0)
        else:
            dot = Circle(radius=0.039, stroke_width=1.3,
                         color=PALETTE.structure_stroke, fill_opacity=0.0)
        dots.add(dot)
    dots.arrange(RIGHT, buff=0.095)
    return dots


class Chrome:
    """Owns the persistent chrome mobjects for one manim Scene."""

    def __init__(self, deck: DeckMeta):
        self.deck = deck
        self.footer: VGroup | None = None
        self.title: VGroup | None = None
        self._state: tuple | None = None

    # ── footer ────────────────────────────────────────────────────────────
    def _build_footer(self, section: str, number: int,
                      label: str | None = None) -> VGroup:
        """`label` overrides the text; `section` still drives the dots.

        Used for backup beats, which read "Backup · <section>" while the dot
        stays on the section they were demoted out of.

        The text is *rendered* at the caption step and then scaled down, rather
        than rendered small. Pango quantises a space to a whole pixel, so below
        about size 22 every word space collapses to the same 1px gap as the
        letter spacing and "Where part 1 left off" reads as "Wherepart1 leftoff".
        Scaling a correctly-spaced mobject keeps the proportions intact.
        """
        family = TYPE.family("footer")
        shrink = TYPE.size("footer") / TYPE.size("caption")

        # Laid out in caption-sized space, then scaled; the slots are divided by
        # `shrink` so the finished, scaled text lands on the intended geometry.
        left_slot = Slot("footer_section", 0.0, 0.0, 6.0 / shrink, 0.34 / shrink,
                         align="left", style="caption")
        name = left_slot.fit_text(label or section or " ", on=MUTED, align="left",
                                  family=family, style="caption")
        name.scale(shrink)
        name.move_to(np.array([-_HALF_W, FOOTER_Y, 0.0]), aligned_edge=LEFT)

        dots = progress_dots(len(self.deck.sections) or 1,
                             self.deck.index_of(section))
        num_slot = Slot("footer_number", 0.0, 0.0, 0.8 / shrink, 0.34 / shrink,
                        align="right", style="caption")
        num = num_slot.fit_text(str(number), on=MUTED, align="right",
                                family=family, style="caption")
        num.scale(shrink)
        num.move_to(np.array([_HALF_W, FOOTER_Y, 0.0]), aligned_edge=RIGHT)

        # A deliberate gap between the dots and the number, so the dots do not
        # read as decoration attached to it.
        dots.next_to(num, LEFT, buff=0.4)
        dots.set_y(FOOTER_Y)
        return VGroup(name, dots, num)

    def sync(self, scene, *, tier: str, section: str = "", number: int = 1,
             title: str | None = None, animate: bool = True,
             layout: str | None = None, collect: bool = False,
             label: str | None = None) -> tuple[list, list]:
        """Bring the chrome into the state this beat asks for.

        Called once per beat by the compiler, before the beat draws itself.
        Rebuilds nothing that has not changed.

        With `collect=True` the animations are returned rather than played, as
        `(leaving, arriving)`. They are kept apart on purpose: the outgoing
        title belongs with the outgoing beat and the incoming title with the
        incoming content. Crossfading them instead — two titles in the same
        band at half opacity — is a ghost, not a transition.
        """
        leaving: list = []
        arriving: list = []
        if tier not in TIERS:
            raise ValueError(f"unknown chrome tier {tier!r}; expected one of {TIERS}")

        wants_footer = tier in (FULL, FOOTER)
        wants_title = tier == FULL and bool(title)

        # Title: rebuilt per beat (its text changes), faded rather than snapped.
        if self.title is not None and (not wants_title or self._state and self._state[0] != title):
            self._remove(scene, self.title, animate, leaving, collect)
            self.title = None
        if wants_title and self.title is None:
            self.title = title_block(title, layout=layout)
            self._add(scene, self.title, animate, arriving, collect)

        # Footer: persistent. Only the section label, dot and number change.
        state = (label or section, number, len(self.deck.sections))
        if not wants_footer:
            if self.footer is not None:
                self._remove(scene, self.footer, animate, leaving, collect)
                self.footer = None
        else:
            new = self._build_footer(section, number, label=label)
            if self.footer is None:
                self.footer = new
                self._add(scene, self.footer, animate, arriving, collect)
            else:
                # Mutate in place: the footer mobject survives next_slide().
                self.footer.become(new)
        self._state = (title, *state)
        return leaving, arriving

    @staticmethod
    def _add(scene, mobject, animate: bool, pending: list, collect: bool) -> None:
        if not animate:
            scene.add(mobject)
        elif collect:
            pending.append(FadeIn(mobject, run_time=0.45))
        else:
            scene.play(FadeIn(mobject, run_time=0.45))

    @staticmethod
    def _remove(scene, mobject, animate: bool, pending: list, collect: bool) -> None:
        if not animate:
            scene.remove(mobject)
        elif collect:
            pending.append(FadeOut(mobject, run_time=0.45))
        else:
            scene.play(FadeOut(mobject, run_time=0.45))

    def mobjects(self) -> list:
        return [m for m in (self.title, self.footer) if m is not None]


def footer(deck: DeckMeta, section: str, number: int,
           label: str | None = None) -> VGroup:
    """The footer on its own, for a beat that has no layout.

    A `raw` beat skips the catalog, so it also skips the chrome the catalog
    would have drawn — which is right for the title and the rule, and wrong for
    the footer: a bare canvas still sits somewhere in the deck and the room
    still wants to know where. The compiler hands raw scenes `section_name`,
    `slide_number` and `deck_sections`; this turns them into the same footer
    every other slide carries.
    """
    return Chrome(deck)._build_footer(section, number, label)
