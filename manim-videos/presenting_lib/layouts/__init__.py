"""The layout catalog.

Importing this module registers every layout. This catalog is the manim
target's; the slides target is written per deck and treats these names as a
description of intent rather than a spec, because a slide deck and a manim video
are different media and should look different.

`raw` is in the catalog as a name but has no class: it is the escape hatch,
where a beat supplies scene code directly and the library gets out of the way.
Raw beats still participate in timing, sections and review; they only skip slot
validation. A library that cannot be stepped around gets abandoned.
"""

from .base import (  # noqa: F401
    Built,
    Content,
    Element,
    Layout,
    Step,
    catalog,
    get_layout,
    register,
)

from . import (  # noqa: F401  — import for the side effect of registering
    activity_parking,
    activity_setup,
    backup,
    build_list,
    callout,
    claim_above_figure,
    claim_only,
    discussion,
    equation_annotated,
    figure_with_callouts,
    full_bleed_figure,
    section_break,
    table_accented,
    term_reveal,
    title_card,
    two_up_compare,
)

RAW = "raw"
CATALOG_NAMES = tuple(sorted(catalog())) + (RAW,)

__all__ = ["Built", "Content", "Element", "Layout", "Step", "catalog",
           "get_layout", "register", "RAW", "CATALOG_NAMES"]
