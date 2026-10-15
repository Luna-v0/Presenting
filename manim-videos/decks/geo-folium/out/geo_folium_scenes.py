"""Points on a map

Generated from decks/geo-folium/screenplay.md by presenting_lib.compile. Do not hand-edit: change
the screenplay and re-compile. Positioning lives in presenting_lib/layouts —
there is deliberately none here.

Render (2K — this is the deck, not a draft):
    uv run manim-slides render decks/geo-folium/out/geo_folium_scenes.py GeoFolium_01_PointsOnAMapOfRio GeoFolium_02_WhatYouAlreadyKnowPandas GeoFolium_03_OneMoreColumnTheGeoDataFrame GeoFolium_04_MergeByLocation GeoFolium_05_WhatAreaDoThePointsCover GeoFolium_06_AMapPeopleCanClick GeoFolium_07_FromCoordinatesToAMap GeoFolium_08_MergeByLocation GeoFolium_09_WhatAreaDoThePointsCover GeoFolium_10_AMapPeopleCanClick -qp
Present:
    uv run manim-slides present GeoFolium_01_PointsOnAMapOfRio GeoFolium_02_WhatYouAlreadyKnowPandas GeoFolium_03_OneMoreColumnTheGeoDataFrame GeoFolium_04_MergeByLocation GeoFolium_05_WhatAreaDoThePointsCover GeoFolium_06_AMapPeopleCanClick GeoFolium_07_FromCoordinatesToAMap GeoFolium_08_MergeByLocation GeoFolium_09_WhatAreaDoThePointsCover GeoFolium_10_AMapPeopleCanClick
Export a self-contained HTML deck (this is how the deck gets watched back):
    uv run manim-slides convert --one-file --offline \
        --use-template identity/out/revealjs.html \
        GeoFolium_01_PointsOnAMapOfRio GeoFolium_02_WhatYouAlreadyKnowPandas GeoFolium_03_OneMoreColumnTheGeoDataFrame GeoFolium_04_MergeByLocation GeoFolium_05_WhatAreaDoThePointsCover GeoFolium_06_AMapPeopleCanClick GeoFolium_07_FromCoordinatesToAMap GeoFolium_08_MergeByLocation GeoFolium_09_WhatAreaDoThePointsCover GeoFolium_10_AMapPeopleCanClick geo-folium.html
"""

from pathlib import Path

from presenting_lib.compile import make_scene_bases

DECK_PATH = Path(__file__).resolve().parent / "../screenplay.md"

DeckScene, DeckScene3D = make_scene_bases()


class GeoFolium_01_PointsOnAMapOfRio(DeckScene):
    """Points on a map of Rio"""

    deck_path = str(DECK_PATH)
    beat_ids = ('title', 'opening-question', 'todays-path', 'the-data')


class GeoFolium_02_WhatYouAlreadyKnowPandas(DeckScene):
    """What you already know: pandas"""

    deck_path = str(DECK_PATH)
    beat_ids = ('pandas-break', 'pandas-read', 'pandas-filter', 'pandas-groupby', 'pandas-merge', 'missing-key', 'act-pandas-setup', 'act-pandas-parking')


class GeoFolium_03_OneMoreColumnTheGeoDataFrame(DeckScene):
    """One more column: the GeoDataFrame"""

    deck_path = str(DECK_PATH)
    beat_ids = ('geo-break', 'geodataframe-table', 'geo-points', 'geo-read', 'geo-plot', 'geo-pandas-still-works', 'act-geo-setup', 'act-geo-parking', 'break-1')


class GeoFolium_04_MergeByLocation(DeckScene):
    """Merge by location"""

    deck_path = str(DECK_PATH)
    beat_ids = ('sjoin-break', 'sjoin-code', 'sjoin-picture', 'sjoin-count', 'sjoin-choropleth', 'data-warts', 'act-sjoin-setup', 'act-sjoin-parking')


class GeoFolium_05_WhatAreaDoThePointsCover(DeckScene):
    """What area do the points cover?"""

    deck_path = str(DECK_PATH)
    beat_ids = ('area-break', 'cre4-points', 'area-discussion', 'cre4-hull', 'cre4-circle', 'cre4-centroid', 'hull-vs-circle', 'act-area-setup', 'act-area-parking', 'break-2')


class GeoFolium_06_AMapPeopleCanClick(DeckScene):
    """A map people can click"""

    deck_path = str(DECK_PATH)
    beat_ids = ('folium-break', 'folium-map', 'folium-markers', 'folium-markers-shot', 'folium-cluster', 'folium-cluster-shot', 'folium-heatmap', 'folium-heatmap-shot', 'folium-shapes', 'folium-shapes-shot', 'folium-save', 'act-folium-setup', 'act-folium-parking')


class GeoFolium_07_FromCoordinatesToAMap(DeckScene):
    """From coordinates to a map"""

    deck_path = str(DECK_PATH)
    beat_ids = ('path-recap', 'closing-callout', 'closing-discussion')


class GeoFolium_08_MergeByLocation(DeckScene):
    """Merge by location"""

    deck_path = str(DECK_PATH)
    beat_ids = ('per-capita',)


class GeoFolium_09_WhatAreaDoThePointsCover(DeckScene):
    """What area do the points cover?"""

    deck_path = str(DECK_PATH)
    beat_ids = ('crs-degrees',)


class GeoFolium_10_AMapPeopleCanClick(DeckScene):
    """A map people can click"""

    deck_path = str(DECK_PATH)
    beat_ids = ('folium-choropleth', 'folium-layers')
