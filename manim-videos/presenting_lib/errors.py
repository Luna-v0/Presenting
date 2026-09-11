"""Failures the library raises on purpose.

Every one of these exists because the alternative is silence. Manim renders
text off-frame and exits zero; a mismatched colour pair renders light-on-light
and exits zero. Silence is what made those two the top defect classes, so the
library converts each into a compile error, which is the only kind of feedback
an agent reliably acts on.
"""


class PresentingError(Exception):
    """Base for everything this library raises."""


class SlotOverflow(PresentingError):
    """Text does not fit its slot at or above the minimum legible size.

    Carries the slot, the offending text, its length and the measured budget so
    the message alone is enough to fix the screenplay.
    """

    def __init__(self, slot_name, text, *, budget=None, layout=None, target=None,
                 min_size=None, tried_size=None):
        self.slot_name = slot_name
        self.text = text
        self.budget = budget
        self.layout = layout
        self.target = target
        self.min_size = min_size
        self.tried_size = tried_size

        where = f"{layout}.{slot_name}" if layout else slot_name
        parts = [f"slot {where!r} overflows"]
        if target:
            parts.append(f" (target {target})")
        parts.append(f": {len(text)} chars")
        if budget is not None:
            parts.append(f", budget {budget}")
        if min_size is not None:
            parts.append(f", floor {min_size} (shrank to {tried_size})")
        parts.append(f"\n  text: {text!r}")
        if budget is not None and len(text) > budget:
            parts.append(f"\n  cut at least {len(text) - budget} characters.")
        super().__init__("".join(parts))


class ColourPairingError(PresentingError):
    """A fill was paired with text that does not belong on it.

    Accent fills carry their own `dark`; ground and structure carry `ink`.
    Never light text on a dark fill, anywhere.
    """


class UnassignedAccentMeaning(PresentingError):
    """An accent was used semantically before its meaning was decided.

    See identity/tokens.yaml `accents:` and plan §11.1. Fill the meanings in
    before generating decks that encode anything with colour.
    """


class UnknownLayout(PresentingError):
    """No such layout in the catalog."""


class LayoutContractError(PresentingError):
    """A layout was handed content it has no slot for, or is missing required content."""


class DiagramError(PresentingError):
    """A node/edge spec could not be laid out (graphviz missing, cycle in ranks, ...)."""
