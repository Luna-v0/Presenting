"""Identity tokens, loaded from identity/tokens.yaml.

Colour is exposed as *ramps* and *surfaces*, never as loose hex strings. A
surface is a fill plus the only text colour permitted on it, so a call site
cannot hand a green tint to a text function and get ink back — that raises.
This is the whole point of the module: the wrong pairing has to be impossible
to express, not merely discouraged. (plan §2.2)
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence

import yaml

from .errors import ColourPairingError, UnassignedAccentMeaning

REPO_ROOT = Path(__file__).resolve().parent.parent
IDENTITY_DIR = REPO_ROOT / "identity"
TOKENS_PATH = IDENTITY_DIR / "tokens.yaml"


# ─────────────────────────────────────────────────────────────────────────────
# Colour
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Ramp:
    """An accent. Three values, never one.

    `tint` is a fill. `mid` is a stroke, rule or dot. `dark` is the only text
    colour that may sit on `tint`. Handing `tint` around on its own is how the
    pairing rule gets broken, so the ramp travels as a unit.
    """

    name: str
    tint: str
    mid: str
    dark: str
    meaning: str | None = None

    @property
    def surface(self) -> "Surface":
        return Surface(name=self.name, fill=self.tint, stroke=self.mid, text=self.dark)

    def require_meaning(self) -> str:
        """The accent's fixed, deck-wide meaning — or raise.

        Call this before using an accent to *encode* something. Structural
        chrome (the title rule, the active progress dot) is decided identity
        and does not go through here.
        """
        if not self.meaning:
            raise UnassignedAccentMeaning(
                f"accent {self.name!r} has no meaning assigned.\n"
                f"  Set accents.{self.name}.meaning in {TOKENS_PATH}.\n"
                "  Until then an accent may not encode content — it would mean a\n"
                "  different thing in every deck, which is worse than no accent."
            )
        return self.meaning


@dataclass(frozen=True)
class Surface:
    """A fill and the only text colour that may sit on it.

    Text functions take a Surface, not a colour. That is what makes the wrong
    pairing unrepresentable rather than merely wrong.
    """

    name: str
    fill: str | None      # None = the slide ground shows through
    stroke: str | None
    text: str

    def check_text_colour(self, colour: str | None) -> str:
        if colour is None:
            return self.text
        if _norm(colour) != _norm(self.text):
            raise ColourPairingError(
                f"text colour {colour} is not permitted on surface {self.name!r}.\n"
                f"  {self.name!r} carries {self.text}.\n"
                "  Accent fills carry their own `dark`; ground and structure carry `ink`.\n"
                "  There is no light-on-dark anywhere in this identity."
            )
        return self.text


def _norm(colour: str) -> str:
    return str(colour).strip().upper().lstrip("#")


@dataclass(frozen=True)
class Palette:
    ground: str
    ink: str
    muted: str
    structure_fill: str
    structure_stroke: str
    green: Ramp
    yellow: Ramp

    # Surfaces — the only legal (fill, text) pairs in the identity.
    @property
    def GROUND(self) -> Surface:
        return Surface("ground", None, None, self.ink)

    @property
    def MUTED(self) -> Surface:
        """Ground, but for the text that must recede: captions, footer, page number."""
        return Surface("muted", None, None, self.muted)

    @property
    def STRUCTURE(self) -> Surface:
        return Surface("structure", self.structure_fill, self.structure_stroke, self.ink)

    @property
    def GREEN(self) -> Surface:
        return self.green.surface

    @property
    def YELLOW(self) -> Surface:
        return self.yellow.surface

    def surface(self, name: str) -> Surface:
        try:
            return {
                "ground": self.GROUND,
                "muted": self.MUTED,
                "structure": self.STRUCTURE,
                "green": self.GREEN,
                "yellow": self.YELLOW,
            }[name]
        except KeyError:
            raise ColourPairingError(
                f"no surface {name!r}. There are five: ground, muted, structure, "
                "green, yellow. A sixth would be a third accent."
            ) from None

    def accent(self, name: str) -> Ramp:
        if name == "green":
            return self.green
        if name == "yellow":
            return self.yellow
        raise ColourPairingError(
            f"no accent {name!r}. There are exactly two — green and yellow — and "
            "introducing a third breaks the encoding for every deck at once."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Type
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _installed_families() -> frozenset[str]:
    try:
        import manimpango

        return frozenset(manimpango.list_fonts())
    except Exception:  # pragma: no cover - pango unavailable
        return frozenset()


def resolve_family(candidates: Sequence[str]) -> str:
    """First installed family in the candidate list.

    Pango falls back silently when a family is missing, which is how a deck ends
    up previewed in a font nobody chose. Resolving here means the substitution
    is at least named and inspectable.
    """
    installed = _installed_families()
    for name in candidates:
        if not installed or name in installed:
            return name
    return candidates[-1]


@dataclass(frozen=True)
class Type:
    family_display: str
    family_body: str
    family_mono: str
    base_font_size: float
    scale: dict[str, float]
    min_legible_body: float
    requested: dict[str, list[str]]

    STYLES = ("display", "title", "claim", "body", "caption", "footer")

    def size(self, style: str) -> float:
        try:
            return self.base_font_size * self.scale[style]
        except KeyError:
            raise KeyError(
                f"no type step {style!r}. The scale is {sorted(self.scale)}. "
                "A size outside it is a missing scale step, not a local override."
            ) from None

    def family(self, style: str) -> str:
        if style == "mono":
            return self.family_mono
        return self.family_display if style in ("display", "title") else self.family_body

    #: Chrome, not content. Exempt from the legibility floor.
    CHROME_STYLES = frozenset({"footer"})

    def substitutions(self) -> dict[str, tuple[str, str]]:
        """Roles where the requested family was not installed: role -> (asked, got)."""
        out = {}
        for role, got in (
            ("family_display", self.family_display),
            ("family_body", self.family_body),
            ("family_mono", self.family_mono),
        ):
            asked = self.requested[role][0]
            if asked != got:
                out[role] = (asked, got)
        return out


@dataclass(frozen=True)
class Geometry:
    safe_inset: float
    gutter: float
    stroke_weight: float
    corner_radius: float

    # Manim's 16:9 frame. Fixed — the slot model needs a fixed camera, so
    # nothing in this library moves or fits the camera.
    frame_width: float = 14.222222222222221
    frame_height: float = 8.0

    @property
    def safe_width(self) -> float:
        return self.frame_width - 2 * self.safe_inset

    @property
    def safe_height(self) -> float:
        return self.frame_height - 2 * self.safe_inset


@dataclass(frozen=True)
class Tokens:
    palette: Palette
    type: Type
    geometry: Geometry
    source: Path

    def accent_meanings_assigned(self) -> bool:
        return bool(self.palette.green.meaning) and bool(self.palette.yellow.meaning)


def load_tokens(path: Path | str | None = None) -> Tokens:
    path = Path(path) if path else TOKENS_PATH
    raw = yaml.safe_load(path.read_text())

    p = raw["palette"]
    meanings = raw.get("accents") or {}

    def ramp(name: str) -> Ramp:
        block = p[name]
        m = (meanings.get(name) or {}).get("meaning")
        return Ramp(name=name, tint=block["tint"], mid=block["mid"], dark=block["dark"],
                    meaning=m or None)

    palette = Palette(
        ground=p["ground"],
        ink=p["ink"],
        muted=p["muted"],
        structure_fill=p["structure"]["fill"],
        structure_stroke=p["structure"]["stroke"],
        green=ramp("green"),
        yellow=ramp("yellow"),
    )

    t = raw["type"]
    requested = {
        "family_display": list(_as_list(t["family_display"])),
        "family_body": list(_as_list(t["family_body"])),
        "family_mono": list(_as_list(t["family_mono"])),
    }
    type_ = Type(
        family_display=resolve_family(requested["family_display"]),
        family_body=resolve_family(requested["family_body"]),
        family_mono=resolve_family(requested["family_mono"]),
        base_font_size=float(t["base_font_size"]),
        scale={k: float(v) for k, v in t["scale"].items()},
        min_legible_body=float(t["min_legible_body"]),
        requested=requested,
    )

    g = raw["geometry"]
    geometry = Geometry(
        safe_inset=float(g["safe_inset"]),
        gutter=float(g["gutter"]),
        stroke_weight=float(g["stroke_weight"]),
        corner_radius=float(g["corner_radius"]),
    )

    return Tokens(palette=palette, type=type_, geometry=geometry, source=path)


def _as_list(value: str | Iterable[str]) -> list[str]:
    if isinstance(value, str):
        return [value]
    return list(value)


T = load_tokens()
PALETTE = T.palette
TYPE = T.type
GEOMETRY = T.geometry

GROUND = PALETTE.GROUND
MUTED = PALETTE.MUTED
STRUCTURE = PALETTE.STRUCTURE
GREEN = PALETTE.GREEN
YELLOW = PALETTE.YELLOW
