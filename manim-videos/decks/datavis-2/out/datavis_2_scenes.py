"""Honest charts

Generated from decks/datavis-2/screenplay.md by presenting_lib.compile. Do not hand-edit: change
the screenplay and re-compile. Positioning lives in presenting_lib/layouts —
there is deliberately none here.

Render (2K — this is the deck, not a draft):
    uv run manim-slides render decks/datavis-2/out/datavis_2_scenes.py Datavis2_01_AChartThatFoolsYou Datavis2_02_EightHabitsOfAnHonestChart Datavis2_03_NotebookPart1 Datavis2_04_ASmallToolbox Datavis2_05_NotebookPart2 Datavis2_06_HowChartsLie Datavis2_07_FixThisChart Datavis2_08_AChecklistToKeep Datavis2_09_HowChartsLie -qp
Present:
    uv run manim-slides present Datavis2_01_AChartThatFoolsYou Datavis2_02_EightHabitsOfAnHonestChart Datavis2_03_NotebookPart1 Datavis2_04_ASmallToolbox Datavis2_05_NotebookPart2 Datavis2_06_HowChartsLie Datavis2_07_FixThisChart Datavis2_08_AChecklistToKeep Datavis2_09_HowChartsLie
Export a self-contained HTML deck (this is how the deck gets watched back):
    uv run manim-slides convert --one-file --offline \
        --use-template identity/out/revealjs.html \
        Datavis2_01_AChartThatFoolsYou Datavis2_02_EightHabitsOfAnHonestChart Datavis2_03_NotebookPart1 Datavis2_04_ASmallToolbox Datavis2_05_NotebookPart2 Datavis2_06_HowChartsLie Datavis2_07_FixThisChart Datavis2_08_AChecklistToKeep Datavis2_09_HowChartsLie datavis-2.html
"""

from pathlib import Path

from presenting_lib.compile import make_scene_bases

DECK_PATH = Path(__file__).resolve().parent / "../screenplay.md"

DeckScene, DeckScene3D = make_scene_bases()


class Datavis2_01_AChartThatFoolsYou(DeckScene):
    """A chart that fools you"""

    deck_path = str(DECK_PATH)
    beat_ids = ('title', 'opening-chart', 'opening-vote', 'opening-split', 'opening-why', 'opening-turn', 'todays-path')


class Datavis2_02_EightHabitsOfAnHonestChart(DeckScene):
    """Eight habits of an honest chart"""

    deck_path = str(DECK_PATH)
    beat_ids = ('habits-break', 'b1-question', 'b2-position', 'b3-data-ink', 'b4-colour', 'b5-annotate', 'b6-title', 'b7-sort', 'b8-aspect', 'b-fixes-code')


class Datavis2_03_NotebookPart1(DeckScene):
    """Notebook, part 1"""

    deck_path = str(DECK_PATH)
    beat_ids = ('practice1-break', 'act-habits-setup', 'act-habits-parking', 'break-1')


class Datavis2_04_ASmallToolbox(DeckScene):
    """A small toolbox"""

    deck_path = str(DECK_PATH)
    beat_ids = ('toolbox-break', 'toolbox-nuance', 'toolbox-map', 'toolbox-data', 'd-spread', 'd-raincloud', 'd-errorbars', 'd-countplot', 'd-groupedbar', 'd-stacked', 'd-pie', 'd-area', 'd-bubble', 'd-pairplot', 'd-corr', 'd-facets', 'd-confusion', 'toolbox-enough')


class Datavis2_05_NotebookPart2(DeckScene):
    """Notebook, part 2"""

    deck_path = str(DECK_PATH)
    beat_ids = ('practice2-break', 'act-toolbox-setup', 'act-toolbox-parking', 'break-2')


class Datavis2_06_HowChartsLie(DeckScene):
    """How charts lie"""

    deck_path = str(DECK_PATH)
    beat_ids = ('lie-break', 'lie-intro', 'c1-truncated', 'c2-dual-axes', 'c4-window', 'c7-mean-median', 'c9-spurious', 'c10-survivors')


class Datavis2_07_FixThisChart(DeckScene):
    """Fix this chart"""

    deck_path = str(DECK_PATH)
    beat_ids = ('fix-break', 'fix-bad', 'act-fix-setup', 'act-fix-parking', 'fix-debrief', 'fix-one-answer', 'fix-per-mile')


class Datavis2_08_AChecklistToKeep(DeckScene):
    """A checklist to keep"""

    deck_path = str(DECK_PATH)
    beat_ids = ('checklist', 'close-callout', 'close-discussion')


class Datavis2_09_HowChartsLie(DeckScene):
    """How charts lie"""

    deck_path = str(DECK_PATH)
    beat_ids = ('c11-base-rate', 'c12-colour-scale', 'c13-log-scale')
