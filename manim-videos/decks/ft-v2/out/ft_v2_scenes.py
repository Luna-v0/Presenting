"""Fine-tuning & Postprocessing LLMs

Generated from decks/ft-v2/screenplay.md by presenting_lib.compile. Do not hand-edit: change
the screenplay and re-compile. Positioning lives in presenting_lib/layouts —
there is deliberately none here.

Render (2K — this is the deck, not a draft):
    uv run manim-slides render decks/ft-v2/out/ft_v2_scenes.py FtV2_01_WherePart1LeftOff FtV2_BTAnim FtV2_03_WherePart1LeftOff FtV2_04_AfterPPO FtV2_05_FeedbackWithoutHumans FtV2_06_WhatBradleyTerryActuallyAssumes FtV2_07_AnAlternative FtV2_NLHFAnim FtV2_09_AnAlternative FtV2_10_WhenBradleyTerryIsStillRight FtV2_11_IfYouWantToPlayWithIt -qp
Present:
    uv run manim-slides present FtV2_01_WherePart1LeftOff FtV2_BTAnim FtV2_03_WherePart1LeftOff FtV2_04_AfterPPO FtV2_05_FeedbackWithoutHumans FtV2_06_WhatBradleyTerryActuallyAssumes FtV2_07_AnAlternative FtV2_NLHFAnim FtV2_09_AnAlternative FtV2_10_WhenBradleyTerryIsStillRight FtV2_11_IfYouWantToPlayWithIt
Export a self-contained HTML deck (this is how the deck gets watched back):
    uv run manim-slides convert --one-file --offline \
        --use-template identity/out/revealjs.html \
        FtV2_01_WherePart1LeftOff FtV2_BTAnim FtV2_03_WherePart1LeftOff FtV2_04_AfterPPO FtV2_05_FeedbackWithoutHumans FtV2_06_WhatBradleyTerryActuallyAssumes FtV2_07_AnAlternative FtV2_NLHFAnim FtV2_09_AnAlternative FtV2_10_WhenBradleyTerryIsStillRight FtV2_11_IfYouWantToPlayWithIt ft-v2.html
"""

from pathlib import Path

from presenting_lib.compile import make_scene_bases

DECK_PATH = Path(__file__).resolve().parent / "../screenplay.md"

DeckScene, DeckScene3D = make_scene_bases()

from scenes.bradley_terry_elo import BradleyTerryToElo
from scenes.nlhf import NLHF


class FtV2_01_WherePart1LeftOff(DeckScene):
    """Where part 1 left off"""

    deck_path = str(DECK_PATH)
    beat_ids = ('title', 'recap-adapters', 'recap-bt-lead')


class FtV2_BTAnim(BradleyTerryToElo):
    """raw beat 'bt-elo-anim' — reuses an existing scene, untouched."""


class FtV2_03_WherePart1LeftOff(DeckScene):
    """Where part 1 left off"""

    deck_path = str(DECK_PATH)
    beat_ids = ('recap-rl-robot', 'recap-ppo', 'recap-rlhf-loop')


class FtV2_04_AfterPPO(DeckScene):
    """After PPO"""

    deck_path = str(DECK_PATH)
    beat_ids = ('after-ppo-break', 'ppo-family')


class FtV2_05_FeedbackWithoutHumans(DeckScene):
    """Feedback without humans"""

    deck_path = str(DECK_PATH)
    beat_ids = ('no-humans-break', 'rlvr-intro', 'rlvr-math', 'rlaif')


class FtV2_06_WhatBradleyTerryActuallyAssumes(DeckScene):
    """What Bradley-Terry actually assumes"""

    deck_path = str(DECK_PATH)
    beat_ids = ('bt-assumes-break', 'bt-drops', 'bt-not-transitive', 'bt-biased')


class FtV2_07_AnAlternative(DeckScene):
    """An alternative"""

    deck_path = str(DECK_PATH)
    beat_ids = ('alternative-break', 'nlhf-idea')


class FtV2_NLHFAnim(NLHF):
    """raw beat 'nlhf-anim' — reuses an existing scene, untouched."""


class FtV2_09_AnAlternative(DeckScene):
    """An alternative"""

    deck_path = str(DECK_PATH)
    beat_ids = ('nlhf-results',)


class FtV2_10_WhenBradleyTerryIsStillRight(DeckScene):
    """When Bradley-Terry is still right"""

    deck_path = str(DECK_PATH)
    beat_ids = ('still-right-break', 'bt-still-works')


class FtV2_11_IfYouWantToPlayWithIt(DeckScene):
    """If you want to play with it"""

    deck_path = str(DECK_PATH)
    beat_ids = ('outro-break', 'libraries', 'harness', 'thesis-ideas')
