"""Bridging the safety gap between simulation and reality

Generated from decks/safety-gap-sim2real/screenplay.md by presenting_lib.compile. Do not hand-edit: change
the screenplay and re-compile. Positioning lives in presenting_lib/layouts —
there is deliberately none here.

Render (2K — this is the deck, not a draft):
    uv run manim-slides render decks/safety-gap-sim2real/out/safety_gap_scenes.py SafetyGapSim2real_01_TheCarAndTheInstinctItProduces Safety_SimWorks Safety_RealByHand SafetyGapSim2real_04_TheCarAndTheInstinctItProduces Safety_RealByPolicy SafetyGapSim2real_06_TheCarAndTheInstinctItProduces Safety_MdpToCmdp SafetyGapSim2real_08_Sim2real Safety_OnboardPair Safety_GapPass SafetyGapSim2real_11_SimilarPlatforms Safety_DriftWheeled SafetyGapSim2real_13_DomainRandomization Safety_AceVideo SafetyGapSim2real_15_DomainRandomization Safety_CubeVideo SafetyGapSim2real_17_DomainRandomization SafetyGapSim2real_18_ThreeQuestionsAboutTheConstraint SafetyGapSim2real_19_Methodology Safety_Observation Safety_SimPipeline Safety_EncoderPipeline SafetyGapSim2real_23_HowEachGapIsClosed SafetyGapSim2real_24_Results Safety_GeneralizationVideo Safety_OnnxInference SafetyGapSim2real_27_Results SafetyGapSim2real_28_Backup -qp
Present:
    uv run manim-slides present SafetyGapSim2real_01_TheCarAndTheInstinctItProduces Safety_SimWorks Safety_RealByHand SafetyGapSim2real_04_TheCarAndTheInstinctItProduces Safety_RealByPolicy SafetyGapSim2real_06_TheCarAndTheInstinctItProduces Safety_MdpToCmdp SafetyGapSim2real_08_Sim2real Safety_OnboardPair Safety_GapPass SafetyGapSim2real_11_SimilarPlatforms Safety_DriftWheeled SafetyGapSim2real_13_DomainRandomization Safety_AceVideo SafetyGapSim2real_15_DomainRandomization Safety_CubeVideo SafetyGapSim2real_17_DomainRandomization SafetyGapSim2real_18_ThreeQuestionsAboutTheConstraint SafetyGapSim2real_19_Methodology Safety_Observation Safety_SimPipeline Safety_EncoderPipeline SafetyGapSim2real_23_HowEachGapIsClosed SafetyGapSim2real_24_Results Safety_GeneralizationVideo Safety_OnnxInference SafetyGapSim2real_27_Results SafetyGapSim2real_28_Backup
Export a self-contained HTML deck (this is how the deck gets watched back):
    uv run manim-slides convert --one-file --offline \
        --use-template identity/out/revealjs.html \
        SafetyGapSim2real_01_TheCarAndTheInstinctItProduces Safety_SimWorks Safety_RealByHand SafetyGapSim2real_04_TheCarAndTheInstinctItProduces Safety_RealByPolicy SafetyGapSim2real_06_TheCarAndTheInstinctItProduces Safety_MdpToCmdp SafetyGapSim2real_08_Sim2real Safety_OnboardPair Safety_GapPass SafetyGapSim2real_11_SimilarPlatforms Safety_DriftWheeled SafetyGapSim2real_13_DomainRandomization Safety_AceVideo SafetyGapSim2real_15_DomainRandomization Safety_CubeVideo SafetyGapSim2real_17_DomainRandomization SafetyGapSim2real_18_ThreeQuestionsAboutTheConstraint SafetyGapSim2real_19_Methodology Safety_Observation Safety_SimPipeline Safety_EncoderPipeline SafetyGapSim2real_23_HowEachGapIsClosed SafetyGapSim2real_24_Results Safety_GeneralizationVideo Safety_OnnxInference SafetyGapSim2real_27_Results SafetyGapSim2real_28_Backup safety-gap-sim2real.html
"""

from pathlib import Path

from presenting_lib.compile import make_scene_bases

DECK_PATH = Path(__file__).resolve().parent / "../screenplay.md"

DeckScene, DeckScene3D = make_scene_bases()

from scenes.clips import AceVideo
from scenes.clips import CubeVideo
from scenes.clips import DriftWheeled
from scenes.clips import GeneralizationVideo
from scenes.clips import OnboardPair
from scenes.clips import OnnxInference
from scenes.clips import RealByHand
from scenes.clips import RealByPolicy
from scenes.clips import SimWorks
from scenes.encoder_pipeline import EncoderPipeline
from scenes.encoder_pipeline import SimPipeline
from scenes.rl_loop import GapPass
from scenes.rl_loop import MdpToCmdp
from scenes.rl_loop import Observation


class SafetyGapSim2real_01_TheCarAndTheInstinctItProduces(DeckScene):
    """The car, and the instinct it produces"""

    deck_path = str(DECK_PATH)
    beat_ids = ('title',)


class Safety_SimWorks(SimWorks):
    """raw beat 'sim-works' — reuses an existing scene, untouched."""

    section_name = 'The car, and the instinct it produces'
    slide_number = 2
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class Safety_RealByHand(RealByHand):
    """raw beat 'real-by-hand' — reuses an existing scene, untouched."""

    section_name = 'The car, and the instinct it produces'
    slide_number = 3
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class SafetyGapSim2real_04_TheCarAndTheInstinctItProduces(DeckScene):
    """The car, and the instinct it produces"""

    deck_path = str(DECK_PATH)
    beat_ids = ('manual-reveal',)


class Safety_RealByPolicy(RealByPolicy):
    """raw beat 'real-by-policy' — reuses an existing scene, untouched."""

    section_name = 'The car, and the instinct it produces'
    slide_number = 5
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class SafetyGapSim2real_06_TheCarAndTheInstinctItProduces(DeckScene):
    """The car, and the instinct it produces"""

    deck_path = str(DECK_PATH)
    beat_ids = ('why-bother', 'not-catastrophic')


class Safety_MdpToCmdp(MdpToCmdp):
    """raw beat 'mdp-to-cmdp' — reuses an existing scene, untouched."""

    section_name = 'The object being transferred'
    slide_number = 8
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class SafetyGapSim2real_08_Sim2real(DeckScene):
    """Sim2real"""

    deck_path = str(DECK_PATH)
    beat_ids = ('s2r-break', 'fidelity-instinct')


class Safety_OnboardPair(OnboardPair):
    """raw beat 'pov-difference' — reuses an existing scene, untouched."""

    section_name = 'Sim2real'
    slide_number = 11
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class Safety_GapPass(GapPass):
    """raw beat 'gap-pass' — reuses an existing scene, untouched."""

    section_name = 'Sim2real'
    slide_number = 12
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class SafetyGapSim2real_11_SimilarPlatforms(DeckScene):
    """Similar platforms"""

    deck_path = str(DECK_PATH)
    beat_ids = ('lit-break', 'platform', 'dr-example', 'wheeled-lab')


class Safety_DriftWheeled(DriftWheeled):
    """raw beat 'drift-wheeled' — reuses an existing scene, untouched."""

    section_name = 'Similar platforms'
    slide_number = 17
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class SafetyGapSim2real_13_DomainRandomization(DeckScene):
    """Domain randomization"""

    deck_path = str(DECK_PATH)
    beat_ids = ('dr-break',)


class Safety_AceVideo(AceVideo):
    """raw beat 'ace-video' — reuses an existing scene, untouched."""

    section_name = 'Domain randomization'
    slide_number = 19
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class SafetyGapSim2real_15_DomainRandomization(DeckScene):
    """Domain randomization"""

    deck_path = str(DECK_PATH)
    beat_ids = ('project-ace', 'ace-architecture')


class Safety_CubeVideo(CubeVideo):
    """raw beat 'cube-video' — reuses an existing scene, untouched."""

    section_name = 'Domain randomization'
    slide_number = 22
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class SafetyGapSim2real_17_DomainRandomization(DeckScene):
    """Domain randomization"""

    deck_path = str(DECK_PATH)
    beat_ids = ('openai-cube', 'cube-transfer')


class SafetyGapSim2real_18_ThreeQuestionsAboutTheConstraint(DeckScene):
    """Three questions about the constraint"""

    deck_path = str(DECK_PATH)
    beat_ids = ('rq-break', 'rq1-question', 'rq1', 'rq2-question', 'rq2', 'rq3-question', 'rq3')


class SafetyGapSim2real_19_Methodology(DeckScene):
    """Methodology"""

    deck_path = str(DECK_PATH)
    beat_ids = ('method-break', 'the-instrument', 'throughput', 'renderer-nyx', 'renderer-madrona', 'renderer-rasterizer')


class Safety_Observation(Observation):
    """raw beat 'observation-paths' — reuses an existing scene, untouched."""

    section_name = 'Methodology'
    slide_number = 38
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class Safety_SimPipeline(SimPipeline):
    """raw beat 'sim-observation' — reuses an existing scene, untouched."""

    section_name = 'Methodology'
    slide_number = 39
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class Safety_EncoderPipeline(EncoderPipeline):
    """raw beat 'encoder-example' — reuses an existing scene, untouched."""

    section_name = 'Methodology'
    slide_number = 40
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class SafetyGapSim2real_23_HowEachGapIsClosed(DeckScene):
    """How each gap is closed"""

    deck_path = str(DECK_PATH)
    beat_ids = ('solve-break', 'dr-layers', 'solve-action', 'solve-transition', 'solve-reward')


class SafetyGapSim2real_24_Results(DeckScene):
    """Results"""

    deck_path = str(DECK_PATH)
    beat_ids = ('results-break',)


class Safety_GeneralizationVideo(GeneralizationVideo):
    """raw beat 'generalisation' — reuses an existing scene, untouched."""

    section_name = 'Results'
    slide_number = 47
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class Safety_OnnxInference(OnnxInference):
    """raw beat 'onnx-inference' — reuses an existing scene, untouched."""

    section_name = 'Results'
    slide_number = 48
    deck_sections = ('The car, and the instinct it produces', 'The object being transferred', 'Sim2real', 'Similar platforms', 'Domain randomization', 'Three questions about the constraint', 'Methodology', 'How each gap is closed', 'Results', 'Backup')


class SafetyGapSim2real_27_Results(DeckScene):
    """Results"""

    deck_path = str(DECK_PATH)
    beat_ids = ('next-steps',)


class SafetyGapSim2real_28_Backup(DeckScene):
    """Backup"""

    deck_path = str(DECK_PATH)
    beat_ids = ('rq2-limit', 'discussion-slide', 'close', 'takeoff-lottery', 'rq3-limits', 'the-goal', 'what-is-dr', 'the-turn', 'the-predicate', 'algorithm', 'renderer-cost', 'expectation-form', 'solve-cost', 'b-throughput', 'b-annotation', 'b-rq1-fallback')
