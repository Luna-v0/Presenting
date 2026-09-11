"""The layout catalog

Generated from decks/catalog-demo/screenplay.md by presenting_lib.compile. Do not hand-edit: change
the screenplay and re-compile. Positioning lives in presenting_lib/layouts —
there is deliberately none here.

Render (2K — this is the deck, not a draft):
    uv run manim-slides render decks/catalog-demo/out/catalog_demo_scenes.py CatalogDemo_01_OpeningTheDeck CatalogDemo_02_ShowingAFigure CatalogDemo_03_TextThatHasToBeExact CatalogDemo_04_BeatsThatAreNotSlides CatalogDemo_05_WhereTheCatalogStops CatalogDemo_06_WhereTheCatalogStops3D CatalogDemo_Raw CatalogDemo_08_WhereTheCatalogStops -qp
Present:
    uv run manim-slides present CatalogDemo_01_OpeningTheDeck CatalogDemo_02_ShowingAFigure CatalogDemo_03_TextThatHasToBeExact CatalogDemo_04_BeatsThatAreNotSlides CatalogDemo_05_WhereTheCatalogStops CatalogDemo_06_WhereTheCatalogStops3D CatalogDemo_Raw CatalogDemo_08_WhereTheCatalogStops
Export a self-contained HTML deck (this is how the deck gets watched back):
    uv run manim-slides convert --one-file --offline \
        --use-template identity/out/revealjs.html \
        CatalogDemo_01_OpeningTheDeck CatalogDemo_02_ShowingAFigure CatalogDemo_03_TextThatHasToBeExact CatalogDemo_04_BeatsThatAreNotSlides CatalogDemo_05_WhereTheCatalogStops CatalogDemo_06_WhereTheCatalogStops3D CatalogDemo_Raw CatalogDemo_08_WhereTheCatalogStops catalog-demo.html
"""

from pathlib import Path

from presenting_lib.compile import make_scene_bases

DECK_PATH = Path(__file__).resolve().parent / "../screenplay.md"

DeckScene, DeckScene3D = make_scene_bases()


class CatalogDemo_01_OpeningTheDeck(DeckScene):
    """Opening the deck"""

    deck_path = str(DECK_PATH)
    beat_ids = ('title', 'the-claim-only', 'the-workhorse', 'the-build-transition')


class CatalogDemo_02_ShowingAFigure(DeckScene):
    """Showing a figure"""

    deck_path = str(DECK_PATH)
    beat_ids = ('figures-break', 'the-callouts', 'the-two-up', 'the-full-bleed')


class CatalogDemo_03_TextThatHasToBeExact(DeckScene):
    """Text that has to be exact"""

    deck_path = str(DECK_PATH)
    beat_ids = ('exact-break', 'the-term', 'the-equation', 'the-table', 'the-callout')


class CatalogDemo_04_BeatsThatAreNotSlides(DeckScene):
    """Beats that are not slides"""

    deck_path = str(DECK_PATH)
    beat_ids = ('room-break', 'the-discussion', 'the-activity-setup', 'the-activity-parking')


class CatalogDemo_05_WhereTheCatalogStops(DeckScene):
    """Where the catalog stops"""

    deck_path = str(DECK_PATH)
    beat_ids = ('edges-break', 'the-placeholder')


class CatalogDemo_06_WhereTheCatalogStops3D(DeckScene3D):
    """Where the catalog stops"""

    deck_path = str(DECK_PATH)
    beat_ids = ('the-3d-split',)


# raw beat 'the-raw-beat' — supplied verbatim by the screenplay
class CatalogDemo_Raw(DeckScene):
    """raw beat: scene code the library never touches."""

    deck_path = str(DECK_PATH)
    beat_ids = ()

    def construct(self):
        from manim import Circle, Create, ManimColor, Text, VGroup

        from presenting_lib.tokens import PALETTE, TYPE

        self.camera.background_color = ManimColor(PALETTE.ground)
        self.camera.init_background()

        ring = Circle(radius=1.6, color=PALETTE.green.mid, stroke_width=6)
        label = Text("raw", font=TYPE.family_body, font_size=48,
                     color=PALETTE.ink)
        self.play(Create(ring))
        self.play(Create(label))
        self.wait(0.4)
        self.next_slide()
        self.play(VGroup(ring, label).animate.scale(0.6))
        self.wait(0.5)


class CatalogDemo_08_WhereTheCatalogStops(DeckScene):
    """Where the catalog stops"""

    deck_path = str(DECK_PATH)
    beat_ids = ('the-backup',)
