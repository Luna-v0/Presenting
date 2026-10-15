"""Reproducible gallery generator for the datavis-2 class.

Draws one sample per chart type (section A, trimmed to the user's picks —
see PICKED_SO_FAR below), one before/after pair per charting principle
(section B), one misleading/honest pair per "how to lie with charts" trick
(section C, also trimmed), one sample each of the standard "well-known"
charts part 1 didn't cover (section D), and one sample each of charts the
audience already meets in ML work (section E, needs a small sklearn model).
Also writes one contact-sheet PNG per section and the `gallery.md` text
that describes every sample.

Run it with an ephemeral environment (no project dependency on seaborn,
pandas, scipy, squarify, pywaffle or scikit-learn is added anywhere else in
the repo):

    uv run --no-project \
        --with seaborn --with matplotlib --with pandas --with scipy \
        --with squarify --with pywaffle --with scikit-learn \
        python make_gallery.py

Needs network access: several datasets are fetched on the fly via
`seaborn.load_dataset`, which pulls small CSVs from the public
mwaskom/seaborn-data GitHub repo. Nothing is cached under gallery/data/ —
every dataset used here is a handful of KB to a few MB and loads in
under a second, so re-downloading on every run is simpler than caching
and keeping a cache in sync (see brief: cache only if it keeps the total
under 2 MB).

Extra libraries beyond seaborn/matplotlib/pandas/scipy, and why:
  - squarify     — treemap (A, item 10). No treemap in seaborn/matplotlib.
  - pywaffle     — waffle chart (A, item 9). No waffle chart in seaborn/matplotlib.
  - scikit-learn — every chart in section E (confusion matrix, ROC/PR,
    feature importance, learning curve, residuals) needs a fitted model;
    nothing in seaborn/matplotlib/pandas/scipy fits one.
No other chart needed anything beyond seaborn/matplotlib/pandas/scipy
(sankey uses matplotlib's own `matplotlib.sankey.Sankey`; parallel
coordinates uses `pandas.plotting.parallel_coordinates`).
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.sankey import Sankey
from scipy import stats as sp_stats

HERE = Path(__file__).resolve().parent
IMG_DIR = HERE / "images"
IMG_DIR.mkdir(exist_ok=True)

FIGSIZE = (8.0, 5.0)  # inches
DPI = 200  # -> 1600x1000 px exactly, for every single-panel and pair image

STYLE_PATH = HERE.parents[2] / "identity" / "out" / "presenting.mplstyle"
if STYLE_PATH.exists():
    plt.style.use(str(STYLE_PATH))
    STYLE_NOTE = f"`{STYLE_PATH.relative_to(HERE.parents[2])}`"
else:
    STYLE_NOTE = "matplotlib defaults (no identity/out/presenting.mplstyle found)"

# Bump the deck's own type sizes up further: the identity style is tuned for
# a composited slide, this gallery is a stand-alone contact sheet meant to be
# read at arm's length on a screen.
plt.rcParams.update(
    {
        "font.size": 14,
        "axes.titlesize": 17,
        "axes.labelsize": 14,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 11,
        "figure.titlesize": 18,
    }
)

ACCENT_GREEN = "#3D6349"
ACCENT_YELLOW = "#A87F20"
MUTED = "#5F5A4B"
INK = "#232A24"
BAD_RED = "#8C3B2E"  # used only in section C to mark the misleading panel

rng = np.random.default_rng(20261015)


def save(fig: plt.Figure, name: str) -> Path:
    path = IMG_DIR / f"{name}.png"
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    return path


def pair_fig(title: str) -> tuple[plt.Figure, plt.Axes, plt.Axes]:
    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, dpi=DPI)
    fig.suptitle(title, fontsize=15)
    for ax in axes:
        ax.tick_params(labelsize=10)
        ax.xaxis.label.set_size(11)
        ax.yaxis.label.set_size(11)
        ax.title.set_size(12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    return fig, axes[0], axes[1]


# --------------------------------------------------------------------------
# Datasets (loaded once)
# --------------------------------------------------------------------------

penguins = sns.load_dataset("penguins").dropna(subset=["bill_length_mm", "flipper_length_mm", "species", "island"])
diamonds = sns.load_dataset("diamonds")
diamonds_sample = diamonds.sample(4000, random_state=0)
healthexp = sns.load_dataset("healthexp")
car_crashes = sns.load_dataset("car_crashes")
geyser = sns.load_dataset("geyser")
titanic = sns.load_dataset("titanic")
flights = sns.load_dataset("flights")
dowjones = sns.load_dataset("dowjones")
taxis = sns.load_dataset("taxis")

DATASET_SOURCES = {
    "penguins": "seaborn built-in `penguins` (palmerpenguins, via mwaskom/seaborn-data)",
    "diamonds": "seaborn built-in `diamonds` (ggplot2 diamonds dataset, via mwaskom/seaborn-data)",
    "healthexp": "seaborn built-in `healthexp` (OECD health spending vs. life expectancy, via mwaskom/seaborn-data)",
    "car_crashes": "seaborn built-in `car_crashes` (US state traffic-crash summary, via mwaskom/seaborn-data)",
    "geyser": "seaborn built-in `geyser` (Old Faithful eruption durations, via mwaskom/seaborn-data)",
    "titanic": "seaborn built-in `titanic` (passenger manifest, via mwaskom/seaborn-data)",
    "flights": "seaborn built-in `flights` (monthly airline passenger totals 1949-1960, via mwaskom/seaborn-data)",
    "dowjones": "seaborn built-in `dowjones` (monthly Dow Jones Industrial Average 1914-1968, via mwaskom/seaborn-data)",
    "taxis": "seaborn built-in `taxis` (NYC yellow-taxi trips, Feb-Mar 2019, via mwaskom/seaborn-data)",
    "iphone_sales": (
        "Apple quarterly iPhone unit sales, 2008-2018 (Apple no longer discloses unit sales after FY2018); "
        "figures compiled from Apple's quarterly earnings reports via public trackers "
        "(Statista / Wikimedia Commons 'iPhone sales per quarter')"
    ),
    "kidney_stones": (
        "Charig CR, Webb DR, Payne SR, Wickham JE (1986), 'Comparison of treatment of renal calculi by open "
        "surgery, percutaneous nephrolithotomy, and extracorporeal shock wave lithotripsy', BMJ 292:879-882 "
        "— the textbook Simpson's-paradox table, as reproduced in standard stats references"
    ),
    "wald_aircraft": (
        "illustrative reconstruction of Abraham Wald's WWII aircraft-survivorship account "
        "(no original tabulated dataset survives; schematic follows the account as retold in "
        "Mangel & Samaniego, 'Abraham Wald's Work on Aircraft Survivability', JASA 1984) — "
        "point positions are illustrative, not measured"
    ),
    "budget_walk": (
        "synthetic, illustrative only — a generic small-project budget walk "
        "(start, a grant, two cost lines, remaining balance), used purely to "
        "show the shape of a waterfall chart; no real budget exists behind it"
    ),
}

# Round 3: the user picked from sections A and C after seeing the first two
# rounds. This is a one-time editorial record, not derived from the chart
# functions below — kept as plain text so "Picked so far" in gallery.md
# always matches what was actually decided, not just what still renders.
PICKED_SO_FAR = """\
**The user's picks, verbatim:**
> For c: we can ignore the area one, the cumulative, the 3d, binning tricks, and what
> else gets too much. for a: I prefer to show just the violin. ignore the ECDF, slope,
> dumbell, hexbin, bump chart, waffle, sankey, calendar heatmap, lolipop, I was expecting
> some other more well known charts, like you didnt even actually put the more normal
> charts (other then the basics)

> Except pareto, waterfall and radar we are fine for D. Except the confusion matrix lets
> ignore the ones from E.

**Final picks, as of round 3:**
- **A (chart toolbox):** only A2 (violin/raincloud). Everything else in A is
  dropped — still rendered below and marked **(dropped)**, not deleted.
- **B (principles):** all 8 — B1 through B8.
- **C (how to lie), main (7):** C1 truncated y-axis, C2 dual axes, C4
  cherry-picked window, C7 mean vs. median, C8 Simpson's paradox, C9 spurious
  correlation, C10 survivorship bias.
- **C, backup (3):** C11 base-rate neglect, C12 colour scale, C13 log scale.
- **C, dropped (4):** C3 area/pictogram scaling, C5 cumulative vs. per-period, C6 3D
  pie, C14 binning tricks.
- **D (well-known charts):** D1 through D10, and D14 — box/violin/strip, grouped bar,
  stacked/100% stacked bar, pie/donut, area/stacked area, bubble, pair plot,
  correlation heatmap, error bars/CI, count plot, and FacetGrid small multiples.
  **Dropped (3):** D11 radar, D12 Pareto, D13 waterfall.
- **E (charts ML already uses):** only E1, confusion matrix. **Dropped (4):** E2
  ROC/PR, E3 feature importance, E4 learning curve, E5 residual plot.

Everything picked across A-E is the candidate set for the screenplay; the presenter
still chooses the final beats from this set (brief, "pending" field).
"""


# --------------------------------------------------------------------------
# Section A — chart toolbox
# --------------------------------------------------------------------------


def a_small_multiples() -> plt.Figure:
    fig, axes = plt.subplots(1, 3, figsize=FIGSIZE, dpi=DPI, sharey=True)
    species_order = sorted(penguins["species"].unique())
    # A clearly distinct, colour-blind-safe qualitative palette — the deck's own
    # two-accent rule (identity/tokens.yaml) is for the final slides, not this
    # exploratory gallery, and three categories need three distinguishable hues.
    palette = dict(zip(species_order, sns.color_palette("colorblind", len(species_order))))
    for ax, island in zip(axes, sorted(penguins["island"].unique())):
        sub = penguins[penguins["island"] == island]
        sns.histplot(sub, x="bill_length_mm", hue="species", hue_order=species_order, palette=palette,
                     multiple="stack", ax=ax, legend=False)
        ax.set_title(island, fontsize=13)
        ax.set_xlabel("bill length (mm)", fontsize=10.5)
    axes[0].set_ylabel("count")
    handles = [plt.Rectangle((0, 0), 1, 1, color=palette[s]) for s in species_order]
    fig.legend(handles, species_order, title="species", loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, -0.02), fontsize=10.5, title_fontsize=10.5, frameon=False)
    fig.suptitle("Small multiples — penguin bill length, one panel per island", fontsize=14)
    fig.tight_layout(rect=(0, 0.1, 1, 0.92))
    return fig


def a_violin_raincloud() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    order = sorted(penguins["species"].unique())
    sns.violinplot(penguins, x="species", y="bill_length_mm", order=order, inner=None, ax=ax, color="#CFC6AE")
    sns.boxplot(penguins, x="species", y="bill_length_mm", order=order, ax=ax, width=0.12,
                boxprops={"zorder": 3, "facecolor": "white"}, showfliers=False)
    sns.stripplot(penguins, x="species", y="bill_length_mm", order=order, ax=ax, size=2.5, alpha=0.5, color=INK,
                  jitter=0.25)
    ax.set_title("Raincloud — violin + box + jittered points")
    ax.set_ylabel("bill length (mm)")
    fig.tight_layout()
    return fig


def a_ecdf() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    sns.ecdfplot(penguins, x="flipper_length_mm", hue="species", ax=ax)
    ax.set_title("ECDF — flipper length by species")
    ax.set_xlabel("flipper length (mm)")
    ax.set_ylabel("proportion ≤ x")
    fig.tight_layout()
    return fig


def _destack(values: list[float], min_gap: float) -> list[float]:
    """Nudge a list of y-positions apart just enough to avoid overlapping text,
    keeping them in the same order. Simple sequential pass, good enough for the
    handful of rows a slope/bump chart ever has."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = list(values)
    for a, b in zip(order, order[1:]):
        if out[b] - out[a] < min_gap:
            out[b] = out[a] + min_gap
    return out


def a_slope_chart() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    sub = healthexp[healthexp["Year"].isin([1971, 2020])]
    piv = sub.pivot(index="Country", columns="Year", values="Life_Expectancy").dropna()  # France has no 1971 row
    min_gap = 1.6
    left_labels = _destack(list(piv[1971]), min_gap=min_gap)
    right_labels = _destack(list(piv[2020]), min_gap=min_gap)
    for (country, row), ly, ry in zip(piv.iterrows(), left_labels, right_labels):
        ax.plot([0, 1], [row[1971], row[2020]], marker="o", color=MUTED)
        # Leader line from the dot's true height to its (possibly nudged) label
        # height, so a de-collided label still visibly belongs to its dot.
        ax.plot([-0.1, -0.04], [row[1971], ly], color=MUTED, linewidth=0.7, alpha=0.6)
        ax.plot([1.04, 1.1], [ry, row[2020]], color=MUTED, linewidth=0.7, alpha=0.6)
        ax.text(-0.12, ly, f"{country} {row[1971]:.0f}", ha="right", va="center", fontsize=9.5)
        ax.text(1.12, ry, f"{country} {row[2020]:.0f}", ha="left", va="center", fontsize=9.5)
    lo = min(*piv[1971], *piv[2020], *left_labels, *right_labels) - 1.5
    hi = max(*piv[1971], *piv[2020], *left_labels, *right_labels) + 1.5
    ax.set_ylim(lo, hi)
    ax.set_xlim(-1.0, 2.0)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["1971", "2020"])
    ax.set_yticks([])
    for spine in ("left", "right", "top"):
        ax.spines[spine].set_visible(False)
    ax.set_title("Slope chart — life expectancy, 1971 vs 2020")
    fig.tight_layout()
    return fig


def a_dumbbell() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    sub = healthexp[healthexp["Year"].isin([1971, 2020])]
    piv = sub.pivot(index="Country", columns="Year", values="Spending_USD").dropna().sort_values(2020)  # France has no 1971 row
    y = np.arange(len(piv))
    ax.hlines(y, piv[1971], piv[2020], color="#CFC6AE", linewidth=3, zorder=1)
    ax.scatter(piv[1971], y, color=MUTED, s=60, zorder=2, label="1971")
    ax.scatter(piv[2020], y, color=ACCENT_GREEN, s=60, zorder=2, label="2020")
    ax.set_yticks(y)
    ax.set_yticklabels(piv.index)
    ax.set_xlabel("health spending per capita (USD)")
    ax.set_title("Dumbbell — spending per capita, 1971 vs 2020")
    ax.legend(loc="lower right")
    fig.tight_layout()
    return fig


def a_ridgeline() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    cuts = ["Fair", "Good", "Very Good", "Premium", "Ideal"]
    offset = 0
    step = 1.0
    for cut in cuts:
        vals = np.log10(diamonds_sample.loc[diamonds_sample["cut"] == cut, "price"])
        xs = np.linspace(vals.min(), vals.max(), 200)
        kde = sp_stats.gaussian_kde(vals)
        ys = kde(xs)
        ys = ys / ys.max() * step * 0.9
        ax.fill_between(xs, offset, offset + ys, color="#CFC6AE", edgecolor=MUTED, linewidth=1.2, zorder=len(cuts) - offset)
        ax.text(vals.min() - 0.03, offset + 0.05, cut, ha="right", fontsize=10.5)
        offset += step
    ax.set_yticks([])
    ax.set_xlabel("log10(price, USD)")
    ax.set_title("Ridgeline — diamond price distribution by cut")
    for spine in ("left", "right", "top"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    return fig


def a_hexbin() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    hb = ax.hexbin(diamonds["carat"], diamonds["price"], gridsize=40, cmap="viridis", mincnt=1)
    fig.colorbar(hb, ax=ax, label="count")
    ax.set_xlabel("carat")
    ax.set_ylabel("price (USD)")
    ax.set_title("Hexbin — carat vs. price (53,940 points, no overplotting)")
    fig.tight_layout()
    return fig


def a_bump_chart() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    years = [1970, 1980, 1990, 2000, 2010, 2020]
    sub = healthexp[healthexp["Year"].isin(years)].copy()
    sub["rank"] = sub.groupby("Year")["Life_Expectancy"].rank(ascending=False, method="first")
    for country, grp in sub.groupby("Country"):
        grp = grp.sort_values("Year")
        ax.plot(grp["Year"], grp["rank"], marker="o", label=country)
        ax.text(years[-1] + 1, grp["rank"].iloc[-1], country, va="center", fontsize=9.5)
    ax.set_ylim(6.5, 0.5)
    ax.set_yticks(range(1, 7))
    ax.set_xticks(years)
    ax.set_xlabel("year")
    ax.set_ylabel("rank by life expectancy (1 = highest)")
    ax.set_title("Bump chart — country rank by life expectancy over time")
    fig.tight_layout()
    return fig


def a_waffle() -> plt.Figure:
    from pywaffle import Waffle

    counts = penguins["species"].value_counts()
    fig = plt.figure(
        FigureClass=Waffle,
        rows=8,
        columns=18,
        values=counts.to_dict(),
        colors=["#3D6349", "#A87F20", "#8C8470"],
        figsize=FIGSIZE,
        legend={"loc": "lower center", "bbox_to_anchor": (0.5, -0.25), "ncol": 3, "fontsize": 11},
        title={"label": "Waffle — penguin species, one square = 1 bird (of 333)", "fontsize": 14},
    )
    fig.set_dpi(DPI)
    return fig


def a_treemap() -> plt.Figure:
    import squarify

    counts = diamonds.groupby("cut", observed=True).size().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    colors = ["#3D6349", "#5F8C6A", "#A87F20", "#CBA660", "#8C8470"]
    labels = [f"{c}\n{n:,}" for c, n in counts.items()]
    squarify.plot(sizes=counts.values, label=labels, color=colors, ax=ax, text_kwargs={"fontsize": 11})
    ax.set_title("Treemap — diamond count by cut")
    ax.axis("off")
    fig.tight_layout()
    return fig


def a_sankey() -> plt.Figure:
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[])
    ax.axis("off")
    counts = titanic["class"].value_counts()
    total = counts.sum()
    sankey = Sankey(ax=ax, unit=None, scale=1.0 / total, gap=0.3, shoulder=0.05)
    sankey.add(
        flows=[total, *(-counts[c] for c in counts.index)],
        labels=[f"passengers\n{total}", *(f"{c}\n{counts[c]}" for c in counts.index)],
        orientations=[0, *([1, -1, 1][: len(counts)])],
        facecolor="#CFC6AE",
        edgecolor=MUTED,
    )
    sankey.finish()
    ax.set_title("Sankey — 891 Titanic passengers by cabin class", y=0.98)
    return fig


def a_parallel_coordinates() -> plt.Figure:
    from pandas.plotting import parallel_coordinates

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    cols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g", "species"]
    sub = penguins[cols].copy()
    for c in cols[:-1]:
        sub[c] = (sub[c] - sub[c].min()) / (sub[c].max() - sub[c].min())
    parallel_coordinates(sub, "species", ax=ax, color=[ACCENT_GREEN, ACCENT_YELLOW, MUTED], alpha=0.5)
    ax.set_xticklabels(["bill length", "bill depth", "flipper length", "body mass"])
    ax.set_ylabel("normalised value (0-1)")
    ax.set_title("Parallel coordinates — four penguin measurements")
    fig.tight_layout()
    return fig


def a_calendar_heatmap() -> plt.Figure:
    daily = taxis.set_index("pickup").resample("D").size()
    daily = daily[(daily.index >= "2019-03-01") & (daily.index < "2019-04-01")]
    first = daily.index.min()
    start = first - pd.Timedelta(days=first.weekday())
    week = ((daily.index - start).days // 7)
    weekday = daily.index.weekday
    grid = np.full((week.max() + 1, 7), np.nan)
    grid[week, weekday] = daily.values
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    im = ax.imshow(grid, cmap="viridis", aspect="auto")
    ax.set_xticks(range(7))
    ax.set_xticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    ax.set_yticks(range(grid.shape[0]))
    ax.set_yticklabels([f"wk {i + 1}" for i in range(grid.shape[0])])
    fig.colorbar(im, ax=ax, label="taxi trips")
    ax.set_title("Calendar heatmap — NYC taxi trips per day, March 2019")
    fig.tight_layout()
    return fig


def a_lollipop() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    top = car_crashes.nlargest(12, "total").sort_values("total")
    y = np.arange(len(top))
    ax.hlines(y, 0, top["total"], color="#CFC6AE", linewidth=2)
    ax.scatter(top["total"], y, color=ACCENT_GREEN, s=70, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(top["abbrev"])
    ax.set_xlabel("crashes per billion miles")
    ax.set_title("Lollipop — 12 highest-crash-rate US states")
    fig.tight_layout()
    return fig


def a_annotated_timeseries() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.plot(dowjones["Date"], dowjones["Price"], color=MUTED)
    peak_idx = dowjones.loc[dowjones["Date"].dt.year == 1929, "Price"].idxmax()
    peak = dowjones.loc[peak_idx]
    trough_idx = dowjones.loc[
        (dowjones["Date"].dt.year >= 1929) & (dowjones["Date"].dt.year <= 1933), "Price"
    ].idxmin()
    trough = dowjones.loc[trough_idx]
    drop_pct = (1 - trough["Price"] / peak["Price"]) * 100
    ax.scatter([trough["Date"]], [trough["Price"]], color=BAD_RED, zorder=3, s=60)
    ax.annotate(
        f"1932 low: down {drop_pct:.0f}%\nfrom the 1929 peak",
        xy=(trough["Date"], trough["Price"]),
        xytext=(trough["Date"] + pd.Timedelta(days=365 * 7), trough["Price"] + 320),
        arrowprops={"arrowstyle": "->", "color": INK},
        fontsize=10.5,
    )
    ax.set_xlabel("year")
    ax.set_ylabel("Dow Jones Industrial Average")
    ax.set_title("Annotated time series — Dow Jones, 1914-1968")
    fig.tight_layout()
    return fig


SECTION_A = [
    ("a01_small_multiples", "Small multiples", a_small_multiples, None,
     "Splits one chart into a grid of small, identically-scaled panels, one per category or facet.",
     "Compares many groups at once without one cluttered overlay; the eye repeats the same read across panels.",
     "Don't use with more than ~12 panels, or when panels need different axis scales to be readable.",
     "`sns.histplot(df, x=..., hue=..., ...)` faceted manually, or `sns.displot(df, x=..., col=...)`"),
    ("a02_raincloud", "Violin / raincloud", a_violin_raincloud, None,
     "Shows the full distribution shape (violin/KDE) plus the raw points and quartiles, per group.",
     "Answers 'what does the whole distribution look like, not just its mean', including multimodality a box plot hides.",
     "Don't use with very small samples (<~15 per group) — the KDE invents shape that isn't there.",
     "`sns.violinplot(df, x=.., y=.., inner=None)` + `sns.stripplot(...)` overlaid"),
    ("a03_ecdf", "ECDF", a_ecdf, None,
     "The empirical cumulative distribution: for each x, the fraction of points ≤ x. No binning choice to argue about.",
     "Answers 'what fraction of the group is below/above a threshold' and compares distributions without histogram bin artefacts.",
     "Don't use with an audience unfamiliar with reading a cumulative curve without more framing/annotation.",
     "`sns.ecdfplot(df, x=.., hue=..)`"),
    ("a04_slope_chart", "Slope chart", a_slope_chart, None,
     "One line per entity connecting its value at two time points (or two conditions).",
     "Answers 'who went up, who went down, by how much' between exactly two points — better than a grouped bar for that.",
     "Don't use with more than ~10-15 entities (the lines cross and the labels collide) or more than two time points.",
     "`ax.plot([0,1], [before, after])` per row, drawn directly on a plain `matplotlib` axis"),
    ("a05_dumbbell", "Dumbbell", a_dumbbell, None,
     "A horizontal line between two dots per category — the two dots are the two values being compared, sorted by one of them.",
     "Answers 'how far apart are these two values, for each of many categories', sorted so the biggest gaps are easy to spot.",
     "Don't use for more than ~2 points per category — a dumbbell is specifically a two-point comparison.",
     "`ax.hlines(y, v1, v2)` then `ax.scatter(v1, y)` / `ax.scatter(v2, y)` on a plain `matplotlib` axis"),
    ("a06_ridgeline", "Ridgeline", a_ridgeline, None,
     "Stacked, overlapping KDE curves, one per category, offset vertically.",
     "Answers 'how does the distribution shift and change shape across an ordered set of categories' (e.g. price by grade).",
     "Don't use with unordered categories (the stacking order becomes arbitrary and misleading) or more than ~8-10 rows.",
     "`scipy.stats.gaussian_kde` per group, plotted with `ax.fill_between` at increasing offsets (no seaborn/matplotlib ridgeline primitive)"),
    ("a07_hexbin", "Hexbin / 2D density", a_hexbin, None,
     "Bins a scatter into hexagonal cells and colours each by point count — a scatter plot that doesn't saturate into one black smear.",
     "Answers 'where is the data actually dense' for two continuous variables with tens of thousands of points.",
     "Don't use for small n (<~1,000) — a plain scatter is clearer and binning adds nothing but noise.",
     "`ax.hexbin(x, y, gridsize=40, cmap='viridis')`, or `sns.jointplot(df, x=.., y=.., kind='hex')`"),
    ("a08_bump_chart", "Bump chart", a_bump_chart, None,
     "Like a slope chart but for rank, at more than two time points: one line per entity, y-axis is rank (1 = best).",
     "Answers 'who was ahead of whom, and when did the order change' — rank over time, not the raw values.",
     "Don't use when the underlying values matter as much as the order — a bump chart hides magnitude entirely.",
     "`ax.plot(years, ranks)` per entity on a plain `matplotlib` axis with an inverted y-axis"),
    ("a09_waffle", "Waffle", a_waffle, "pywaffle",
     "A part-to-whole chart as a grid of small squares, each worth one unit (or a fixed count), coloured by category.",
     "Answers 'what share of the whole does each category hold', literally countable, for a small number of categories.",
     "Don't use for more than ~5-6 categories, or when precise comparison (not just 'roughly how much') matters — use a bar.",
     "`pywaffle.Waffle` as a custom `matplotlib` Figure class: `plt.figure(FigureClass=Waffle, rows=.., values=..)`"),
    ("a10_treemap", "Treemap", a_treemap, "squarify",
     "A part-to-whole chart as nested/adjacent rectangles, area proportional to value.",
     "Answers 'what share of the whole does each category hold' when there are too many categories for a pie or waffle to stay legible.",
     "Don't use when precise comparison matters (area is hard to compare precisely — Cleveland's ranking again) or categories are few enough for a bar chart.",
     "`squarify.plot(sizes=.., label=..)` (no treemap primitive in seaborn/matplotlib)"),
    ("a11_sankey", "Sankey / flow", a_sankey, None,
     "Shows a quantity splitting (or merging) from one state into several, width proportional to amount.",
     "Answers 'where did the people/volume/money go' — a flow or funnel question, not a static comparison.",
     "Don't use for more than 2-3 stages by hand with `matplotlib.sankey` — it has no automatic layout, unlike a dedicated alluvial library.",
     "`matplotlib.sankey.Sankey(ax=ax).add(flows=.., labels=.., orientations=..).finish()`"),
    ("a12_parallel_coordinates", "Parallel coordinates", a_parallel_coordinates, None,
     "One vertical axis per variable, normalised to the same 0-1 range, one polyline per row connecting its values across all axes.",
     "Answers 'do rows that are high on one variable tend to be high (or low) on another', across more than 2-3 variables at once.",
     "Don't use with more than ~6-8 variables or categories whose lines are indistinguishable once overplotted — the chart becomes visual noise.",
     "`pandas.plotting.parallel_coordinates(df, class_column=..)`"),
    ("a13_calendar_heatmap", "Calendar heatmap", a_calendar_heatmap, None,
     "A grid with weekday on one axis and week on the other, each cell shaded by a daily value.",
     "Answers 'which days were unusual' and reveals weekly/seasonal rhythm that a plain time-series line smooths over.",
     "Don't use for less than a few weeks of data (too few cells to show a pattern) or more than ~2 years (cells get unreadably small).",
     "`ax.imshow(grid, cmap=..)` on a week-by-weekday array built with `pandas` resample + reshape (no calendar-heatmap primitive in seaborn/matplotlib)"),
    ("a14_lollipop", "Lollipop", a_lollipop, None,
     "A bar chart with the bar replaced by a thin line and a dot at the tip.",
     "Answers the same ranking question as a bar chart, with less ink — useful when there are many categories and a solid bar gets heavy.",
     "Don't use when the audience needs to read exact bar lengths quickly at a glance — a dot is a little harder to compare than a bar edge.",
     "`ax.hlines(y, 0, value)` + `ax.scatter(value, y)` on a plain `matplotlib` axis"),
    ("a15_annotated_timeseries", "Annotated time series", a_annotated_timeseries, None,
     "A line chart with a callout marking the specific point the chart is about.",
     "Answers 'what happened, and when' by pointing at the moment that matters instead of leaving the audience to find it.",
     "Don't use more than 1-2 annotations per chart — past that they compete with each other and with the line.",
     "`ax.annotate(text, xy=.., xytext=.., arrowprops=..)` on top of `ax.plot(...)`"),
]


# --------------------------------------------------------------------------
# Section B — principles (before / after)
# --------------------------------------------------------------------------


def b_choose_by_question() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Choosing the chart by the question")
    order = sorted(penguins["species"].unique())
    means = penguins.groupby("species", observed=True)["body_mass_g"].mean().reindex(order)
    ax1.plot(order, means.values, marker="o", color=BAD_RED)
    ax1.set_title("Before: a line over categories")
    ax1.set_ylabel("mean body mass (g)")
    ax2.bar(order, means.values, color=ACCENT_GREEN)
    ax2.set_title("After: a bar — species has no order")
    return fig


def b_cleveland_ranking() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Cleveland's perceptual ranking: position > angle/area")
    counts = diamonds.groupby("cut", observed=True).size().sort_values(ascending=False)
    ax1.pie(counts.values, labels=counts.index, autopct="%1.0f%%", colors=sns.color_palette("flare", len(counts)))
    ax1.set_title("Before: angle + area (pie)")
    ax2.barh(counts.index[::-1], counts.values[::-1], color=ACCENT_GREEN)
    ax2.set_title("After: position (bar)")
    ax2.set_xlabel("count")
    return fig


def b_data_ink() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Data-ink and decluttering")
    top = car_crashes.nlargest(6, "total").sort_values("total")
    ax1.barh(top["abbrev"], top["total"], color="#9A9478", edgecolor="black", linewidth=1.5, hatch="//")
    ax1.grid(True, which="both", linewidth=1.2)
    ax1.set_title("Before: heavy grid, border, hatch")
    for spine in ax1.spines.values():
        spine.set_visible(True)
    ax2.barh(top["abbrev"], top["total"], color=ACCENT_GREEN)
    for spine in ("top", "right"):
        ax2.spines[spine].set_visible(False)
    ax2.set_title("After: only the data-ink that carries meaning")
    return fig


def b_colour() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Colour: sequential data needs a sequential, colour-blind-safe map")
    corr = diamonds[["carat", "depth", "table", "price"]].corr()
    sns.heatmap(corr, cmap="jet", annot=True, fmt=".2f", ax=ax1, cbar=False)
    ax1.set_title("Before: 'jet' (not perceptually uniform)")
    sns.heatmap(corr, cmap="viridis", annot=True, fmt=".2f", ax=ax2, cbar=False)
    ax2.set_title("After: viridis (sequential, colour-blind safe)")
    return fig


def b_annotation() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Annotation")
    dates = pd.to_datetime(flights["year"].astype(str) + "-" + flights["month"].astype(str), format="%Y-%b")
    s = pd.Series(flights["passengers"].values, index=dates).sort_index()
    ax1.plot(s.index, s.values, color=MUTED)
    ax1.set_title("Before: no callout, reader hunts for the point")
    ax2.plot(s.index, s.values, color=MUTED)
    peak_date = s.idxmax()
    ax2.annotate(f"all-time high\n{peak_date:%b %Y}", xy=(peak_date, s.max()),
                 xytext=(peak_date - pd.Timedelta(days=365 * 4), s.max() - 90),
                 arrowprops={"arrowstyle": "->"}, fontsize=9.5)
    ax2.set_title("After: the point is marked")
    return fig


def b_takeaway_title() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("A title that states the takeaway")
    order = sorted(penguins["species"].unique())
    means = penguins.groupby("species", observed=True)["body_mass_g"].mean().reindex(order)
    ax1.bar(order, means.values, color=ACCENT_GREEN)
    ax1.set_title("Figure 1")
    ax2.bar(order, means.values, color=ACCENT_GREEN)
    ax2.set_title("Gentoo penguins are nearly 50% heavier", fontsize=11.5)
    return fig


def b_sorting() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Sorting")
    top = car_crashes.nlargest(10, "total").sort_values("abbrev")
    ax1.barh(top["abbrev"], top["total"], color="#9A9478")
    ax1.set_title("Before: alphabetical order")
    top_sorted = top.sort_values("total")
    ax2.barh(top_sorted["abbrev"], top_sorted["total"], color=ACCENT_GREEN)
    ax2.set_title("After: sorted by value")
    return fig


def b_aspect_ratio() -> plt.Figure:
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    fig.suptitle("Aspect ratio", fontsize=15)
    sub = flights.groupby("year")["passengers"].sum()
    ax1 = fig.add_axes([0.08, 0.58, 0.38, 0.28])
    ax1.plot(sub.index, sub.values, color=BAD_RED)
    ax1.set_title("Before: tall and narrow\nexaggerates the slope", fontsize=10.5)
    ax2 = fig.add_axes([0.52, 0.15, 0.42, 0.65])
    ax2.plot(sub.index, sub.values, color=ACCENT_GREEN)
    ax2.set_title("After: banked to ~45°\n(a well-chosen aspect ratio)", fontsize=10.5)
    return fig


SECTION_B = [
    ("b01_choose_by_question", "Choose the chart by the question", b_choose_by_question,
     "A line implies order/continuity between categories; species has neither. The bar makes no claim the data doesn't support."),
    ("b02_cleveland_ranking", "Cleveland's perceptual ranking", b_cleveland_ranking,
     "People read position on a common scale far more accurately than angle or area — the pie slices are genuinely hard to rank by eye; the bar is instant."),
    ("b03_data_ink", "Data-ink and decluttering", b_data_ink,
     "Every mark that isn't carrying information (heavy grid, border, hatch, redundant axis lines) is a tax on the reader's attention; strip it."),
    ("b04_colour", "Colour choice", b_colour,
     "'jet' is not perceptually uniform (equal steps in value don't look equally far apart) and fails for colour-blind readers; a sequential map like viridis fixes both."),
    ("b05_annotation", "Annotation", b_annotation,
     "A chart states what happened; an annotation states why the reader should care about one point in particular, instead of leaving them to search for it."),
    ("b06_takeaway_title", "A title that states the takeaway", b_takeaway_title,
     "'Figure 1' tells the reader nothing; a title that states the finding lets them read the chart in the direction the presenter means it."),
    ("b07_sorting", "Sorting", b_sorting,
     "Alphabetical order answers 'what letter does the name start with', which is almost never the question; sorting by value makes the ranking the first thing seen."),
    ("b08_aspect_ratio", "Aspect ratio", b_aspect_ratio,
     "The same line, stretched tall and narrow, reads as a much steeper trend than the identical line banked near 45°, the rule of thumb for an undistorted slope."),
]


# --------------------------------------------------------------------------
# Section C — how to lie with charts (misleading / honest)
# --------------------------------------------------------------------------


def c_truncated_axis() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Truncated y-axis")
    vals = penguins.groupby("species", observed=True)["body_mass_g"].mean().sort_values()
    ax1.bar(vals.index, vals.values, color=BAD_RED)
    ax1.set_ylim(3400, 5100)
    ax1.set_title("Misleading: axis starts at 3,400 g")
    ax2.bar(vals.index, vals.values, color=ACCENT_GREEN)
    ax2.set_ylim(0, 5500)
    ax2.set_title("Honest: axis starts at 0")
    return fig


def c_dual_axes() -> plt.Figure:
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    fig.suptitle("Dual axes make unrelated trends look locked together", fontsize=14)
    sub = flights[(flights["year"] >= 1949) & (flights["year"] <= 1960)].groupby("year")["passengers"].mean()
    dj = dowjones[(dowjones["Date"].dt.year >= 1949) & (dowjones["Date"].dt.year <= 1960)]
    dj_yearly = dj.groupby(dj["Date"].dt.year)["Price"].mean()
    ax1 = fig.add_axes([0.1, 0.15, 0.38, 0.65])
    ax1.plot(sub.index, sub.values, color=ACCENT_GREEN)
    ax1.set_ylabel("flight passengers/mo", color=ACCENT_GREEN, fontsize=10.5)
    ax1b = ax1.twinx()
    ax1b.plot(dj_yearly.index, dj_yearly.values, color=ACCENT_YELLOW)
    ax1b.set_ylabel("Dow Jones price", color=ACCENT_YELLOW, fontsize=10.5)
    ax1.set_title("Misleading: two y-axes, scaled\nto look like one story", fontsize=10.5)
    ax2 = fig.add_axes([0.58, 0.15, 0.38, 0.65])
    idx = lambda s: s / s.iloc[0] * 100
    ax2.plot(sub.index, idx(sub), color=ACCENT_GREEN, label="flights")
    ax2.plot(dj_yearly.index, idx(dj_yearly), color=ACCENT_YELLOW, label="Dow Jones")
    ax2.set_ylabel("index (1949 = 100)", fontsize=10.5)
    ax2.legend(fontsize=9)
    ax2.set_title("Honest: one axis, both series\nindexed to the same start", fontsize=10.5)
    return fig


def c_area_scaling() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Area / pictogram scaling")
    v1, v2 = diamonds_sample.loc[diamonds_sample["cut"] == "Fair", "price"].mean(), \
        diamonds_sample.loc[diamonds_sample["cut"] == "Ideal", "price"].mean()
    r1, r2 = 0.3, 0.3 * (v2 / v1)
    ax1.add_patch(plt.Circle((0.3, 0.5), r1, color=BAD_RED))
    ax1.add_patch(plt.Circle((0.75, 0.5), r2, color=BAD_RED, alpha=0.7))
    ax1.text(0.3, 0.08, f"Fair\n${v1:,.0f}", ha="center", fontsize=9.5)
    ax1.text(0.75, 0.08, f"Ideal\n${v2:,.0f}", ha="center", fontsize=9.5)
    ax1.set_xlim(0, 1.1); ax1.set_ylim(0, 1); ax1.axis("off"); ax1.set_aspect("equal")
    ax1.set_title("Misleading: radius scaled to value\n(area then grows with value squared)", fontsize=10.5)
    a1, a2 = 1.0, v2 / v1
    r1b, r2b = np.sqrt(a1 / np.pi) * 0.3, np.sqrt(a2 / np.pi) * 0.3
    ax2.add_patch(plt.Circle((0.3, 0.5), r1b, color=ACCENT_GREEN))
    ax2.add_patch(plt.Circle((0.75, 0.5), r2b, color=ACCENT_GREEN, alpha=0.7))
    ax2.text(0.3, 0.08, f"Fair\n${v1:,.0f}", ha="center", fontsize=9.5)
    ax2.text(0.75, 0.08, f"Ideal\n${v2:,.0f}", ha="center", fontsize=9.5)
    ax2.set_xlim(0, 1.1); ax2.set_ylim(0, 1); ax2.axis("off"); ax2.set_aspect("equal")
    ax2.set_title("Honest: area scaled to value", fontsize=10.5)
    return fig


def c_cherry_picked_window() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Cherry-picked time window")
    boom = dowjones[(dowjones["Date"].dt.year >= 1949) & (dowjones["Date"].dt.year <= 1956)]
    ax1.plot(boom["Date"], boom["Price"], color=BAD_RED)
    ax1.set_title("Misleading: 1949-1956 only\n('stocks only go up')", fontsize=10.5)
    ax2.plot(dowjones["Date"], dowjones["Price"], color=ACCENT_GREEN)
    ax2.axvspan(pd.Timestamp("1949-01-01"), pd.Timestamp("1956-12-31"), color=BAD_RED, alpha=0.15)
    ax2.set_title("Honest: full 1914-1968 range\n(the 1929 crash is in there)", fontsize=10.5)
    return fig


def c_cumulative_vs_period() -> plt.Figure:
    # Apple's FISCAL quarters (fiscal year runs Oct-Sep, one quarter ahead of the
    # calendar): FY2008 Q1 = Oct-Dec 2007 = 2.32M units, ... FY2018 Q4 = Jul-Sep
    # 2018 = 46.89M units. Labelled as fiscal quarters below so the axis matches
    # the data instead of silently reading one quarter off against calendar time.
    fiscal_labels = [f"FY{str(y)[2:]} Q{q}" for y in range(2008, 2019) for q in range(1, 5)]
    units = [
        2.32, 1.70, 0.72, 6.89, 4.36, 3.79, 5.21, 7.37, 8.74, 8.75, 8.40, 14.10,
        16.24, 18.65, 20.34, 17.07, 37.04, 35.06, 26.03, 26.91, 47.79, 37.43, 31.24, 33.80,
        51.03, 43.72, 35.20, 39.27, 74.47, 61.17, 47.53, 48.05, 74.78, 51.19, 40.40, 45.51,
        78.29, 50.76, 41.03, 46.68, 77.32, 52.22, 41.30, 46.89,
    ]
    s = pd.Series(units, index=fiscal_labels)
    fig, ax1, ax2 = pair_fig("Cumulative vs. per-period (Apple's 2013 iPhone chart, fiscal quarters)")
    ax1.plot(s.index, s.cumsum().values, color=BAD_RED)
    ax1.set_xticks(ax1.get_xticks()[::8])
    ax1.set_title("Misleading: cumulative units sold\n(can only ever go up)", fontsize=10.5)
    ax2.bar(s.index, s.values, color=ACCENT_GREEN)
    ax2.set_xticks(ax2.get_xticks()[::8])
    ax2.set_title("Honest: per-quarter units\n(growth slows after 2015)", fontsize=10.5)
    return fig


def c_3d_pie() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("3D pie")
    counts = diamonds.groupby("cut", observed=True).size().sort_values(ascending=False)
    colors = sns.color_palette("flare", len(counts))
    n = 200
    theta = np.linspace(0, 2 * np.pi, n)
    cum = np.concatenate([[0], np.cumsum(counts.values)]) / counts.sum() * 2 * np.pi
    ax1.set_xlim(-1.3, 1.3); ax1.set_ylim(-1.1, 1.3); ax1.axis("off")
    for i in range(len(counts)):
        t = np.linspace(cum[i], cum[i + 1], 60)
        x = np.concatenate([[0], np.cos(t)])
        y_top = np.concatenate([[0], np.sin(t) * 0.55])
        ax1.fill(x, y_top, color=colors[i])
        y_side = np.concatenate([[0], np.sin(t) * 0.55 - 0.18])
        ax1.fill(np.r_[x, x[::-1]], np.r_[y_side, y_top[::-1]], color=colors[i], alpha=0.6)
    ax1.set_title("Misleading: perspective + squash\ndistort angle and area further", fontsize=10.5)
    ax2.pie(counts.values, labels=counts.index, autopct="%1.0f%%", colors=colors)
    ax2.set_title("Honest: flat 2D pie\n(still angle/area — see Cleveland)", fontsize=10.5)
    return fig


def c_mean_median() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Mean vs. median on skewed data")
    prices = diamonds_sample["price"]
    ax1.hist(prices, bins=40, color="#CFC6AE")
    ax1.axvline(prices.mean(), color=BAD_RED, linewidth=2.5)
    ax1.text(prices.mean() + 400, ax1.get_ylim()[1] * 0.9, f"mean\n${prices.mean():,.0f}", color=BAD_RED, fontsize=9.5)
    ax1.set_title("Misleading: 'the average diamond'\n(mean, pulled right by outliers)", fontsize=10.5)
    ax2.hist(prices, bins=40, color="#CFC6AE")
    ax2.axvline(prices.median(), color=ACCENT_GREEN, linewidth=2.5)
    ax2.text(prices.median() + 400, ax2.get_ylim()[1] * 0.9, f"median\n${prices.median():,.0f}", color=ACCENT_GREEN, fontsize=9.5)
    ax2.set_title("Honest: median\n(the typical diamond)", fontsize=10.5)
    return fig


def c_simpsons_paradox() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Simpson's paradox: kidney-stone treatment (Charig et al. 1986)")
    agg = pd.DataFrame({"treatment": ["Open surgery", "PCNL"], "rate": [273 / 350 * 100, 289 / 350 * 100]})
    ax1.bar(agg["treatment"], agg["rate"], color=[ACCENT_GREEN, BAD_RED])
    for i, r in enumerate(agg["rate"]):
        ax1.text(i, r + 1, f"{r:.0f}%", ha="center", fontsize=10.5)
    ax1.set_ylim(0, 100)
    ax1.set_ylabel("success rate (%)")
    ax1.set_title("Misleading: pooled\n('PCNL looks better')", fontsize=10.5)
    detail = pd.DataFrame({
        "size": ["small (<2cm)", "small (<2cm)", "large (≥2cm)", "large (≥2cm)"],
        "treatment": ["Open", "PCNL", "Open", "PCNL"],
        "rate": [81 / 87 * 100, 234 / 270 * 100, 192 / 263 * 100, 55 / 80 * 100],
    })
    x = np.arange(2)
    w = 0.35
    for i, t in enumerate(["Open", "PCNL"]):
        vals = detail.loc[detail["treatment"] == t, "rate"].values
        ax2.bar(x + (i - 0.5) * w, vals, width=w, label=t, color=[ACCENT_GREEN, BAD_RED][i])
    ax2.set_xticks(x)
    ax2.set_xticklabels(["small", "large"])
    ax2.set_ylim(0, 100)
    ax2.legend(fontsize=9)
    ax2.set_title("Honest: split by stone size\n(open surgery wins both groups)", fontsize=10.5)
    return fig


def c_spurious_correlation() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Correlation ≠ causation (spurious correlation)")
    japan_spend = healthexp.loc[healthexp["Country"] == "Japan"].set_index("Year")["Spending_USD"]
    usa_life = healthexp.loc[healthexp["Country"] == "USA"].set_index("Year")["Life_Expectancy"]
    merged = pd.merge(japan_spend.rename("spend"), usa_life.rename("life"), left_index=True, right_index=True)
    r = merged["spend"].corr(merged["life"])
    ax1.scatter(merged["spend"], merged["life"], color=BAD_RED)
    z = np.polyfit(merged["spend"], merged["life"], 1)
    xs = np.linspace(merged["spend"].min(), merged["spend"].max(), 50)
    ax1.plot(xs, np.polyval(z, xs), color=BAD_RED, linestyle="--")
    ax1.set_xlabel("Japan health spending per capita (USD)")
    ax1.set_ylabel("US life expectancy")
    ax1.set_title(f"Misleading: r={r:.2f} looks strong\n(both just trend over time)", fontsize=10.5)
    idx = lambda s: (s - s.min()) / (s.max() - s.min())
    ax2.plot(merged.index, idx(merged["spend"]), color=ACCENT_GREEN, label="Japan spending (indexed)")
    ax2.plot(merged.index, idx(merged["life"]), color=ACCENT_YELLOW, label="US life exp. (indexed)")
    ax2.legend(fontsize=9)
    ax2.set_title("Honest: both are just monotonic\nover time, no shared mechanism", fontsize=10.5)
    return fig


def c_survivorship_bias() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Survivorship bias: WWII bomber returns (Wald, 1943)")
    body = plt.Polygon([(-1, 0), (1, 0), (0.85, 0.35), (-0.85, 0.35)], closed=True, fill=False, edgecolor=INK, linewidth=1.5)
    wing = plt.Polygon([(-0.15, 0.17), (0.15, 0.17), (0.45, 0.9), (-0.45, 0.9)], closed=True, fill=False, edgecolor=INK, linewidth=1.5)
    for ax, title in ((ax1, "Misleading: reinforce where\nreturning planes ARE hit"), (ax2, "Honest: reinforce where\nreturning planes are NOT hit")):
        ax.add_patch(plt.Polygon(body.get_xy(), closed=True, fill=False, edgecolor=INK, linewidth=1.5))
        ax.add_patch(plt.Polygon(wing.get_xy(), closed=True, fill=False, edgecolor=INK, linewidth=1.5))
        ax.set_xlim(-1.1, 1.1); ax.set_ylim(-0.1, 1.0); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(title, fontsize=10.5)
    body_hits_x = rng.uniform(-0.8, 0.8, 35)
    body_hits_y = rng.uniform(0.02, 0.33, 35)
    ax1.scatter(body_hits_x, body_hits_y, color=BAD_RED, s=14)
    ax1.scatter(rng.uniform(-0.4, 0.4, 10), rng.uniform(0.2, 0.85, 10), color=BAD_RED, s=14)
    engines = [(-0.5, 0.45), (0.5, 0.45)]
    for ex, ey in engines:
        ax2.add_patch(plt.Circle((ex, ey), 0.1, fill=False, edgecolor=ACCENT_GREEN, linewidth=2.5))
    ax2.text(0, -0.08, "no damage seen here\non planes that made it back\n→ a hit there likely means it didn't", ha="center", fontsize=8.5, color=ACCENT_GREEN)
    return fig


def c_base_rate_neglect() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Base-rate neglect (synthetic — standard textbook numbers)")
    ax1.text(0.5, 0.6, "Test is 90% accurate.\nYou tested positive.", ha="center", va="center", fontsize=13)
    ax1.text(0.5, 0.25, "...so 90% chance you\nhave the disease?", ha="center", va="center", fontsize=12, color=BAD_RED)
    ax1.axis("off")
    ax1.set_title("Misleading: accuracy alone\nignores the base rate", fontsize=10.5)
    prevalence = 0.01
    n = 10000
    sick = int(n * prevalence)
    well = n - sick
    true_pos = int(sick * 0.9)
    false_pos = int(well * 0.1)
    cats = ["sick,\npositive", "sick,\nmissed", "well,\nfalse positive", "well,\ncorrect"]
    vals = [true_pos, sick - true_pos, false_pos, well - false_pos]
    ax2.bar(cats, vals, color=[ACCENT_GREEN, "#9A9478", BAD_RED, "#CFC6AE"])
    ax2.set_ylabel("people (of 10,000, 1% prevalence)")
    ppv = true_pos / (true_pos + false_pos) * 100
    ax2.set_title(f"Honest: only {ppv:.0f}% of positives\nactually have it", fontsize=10.5)
    return fig


def c_misleading_colour_scale() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Misleading colour scale (synthetic smooth field)")
    # A smooth, continuous field (sum of two Gaussian bumps) with no real edges
    # in it anywhere — any banding or false contour the colour scale creates is
    # therefore visibly an artefact of the colormap, not of the data.
    x = np.linspace(-4, 4, 300)
    y = np.linspace(-4, 4, 300)
    X, Y = np.meshgrid(x, y)
    field = np.exp(-((X - 1.3) ** 2 + (Y - 1.0) ** 2) / 4.5) + 0.75 * np.exp(-((X + 1.6) ** 2 + (Y + 0.8) ** 2) / 6.0)
    for ax, cmap, title in (
        (ax1, "jet", "Misleading: 'jet' creates false\nbands that aren't in the data"),
        (ax2, "viridis", "Honest: perceptually uniform\nsequential colormap, same data"),
    ):
        cs = ax.contourf(X, Y, field, levels=24, cmap=cmap)
        fig.colorbar(cs, ax=ax, fraction=0.046, pad=0.04)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(title, fontsize=10.5)
    return fig


def c_log_scale() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Log scale without saying so")
    s = flights.groupby("year")["passengers"].sum()
    # Misleading: a log y-axis, but with plain round-number tick labels (no
    # "10^" notation, axis not named "log") — a log scale also visually
    # flattens accelerating growth into something that reads as steady, so
    # the chart looks like gentle, even growth either way you check it.
    ax1.plot(s.index, s.values, color=BAD_RED)
    ax1.set_yscale("log")
    # Default LogLocator only places ticks at power-of-ten decades (1000,
    # 10000, ...), both outside this series' 1500-6000 range, which would
    # leave the axis blank. LogLocator(subs=...) places a few log-spaced
    # ticks inside the visible range instead, formatted as plain round
    # numbers rather than "10^x" notation.
    ax1.yaxis.set_major_locator(mticker.LogLocator(subs=(1.0, 2.0, 3.0, 5.0, 7.0)))
    ax1.yaxis.set_major_formatter(mticker.ScalarFormatter())
    ax1.yaxis.set_minor_locator(mticker.NullLocator())
    ax1.set_ylabel("passengers/year")
    ax1.set_title("Misleading: log y-axis, plain-looking\nticks, axis not labelled as log", fontsize=10.5)
    # Honest: the same data on a linear axis, clearly labelled — the true
    # accelerating (convex) growth late in the series is now visible, instead
    # of being compressed into a near-straight line by the log scale.
    ax2.plot(s.index, s.values, color=ACCENT_GREEN)
    ax2.set_ylabel("passengers/year (linear scale)")
    ax2.set_title("Honest: linear axis, clearly\nlabelled — growth is accelerating", fontsize=10.5)
    return fig


def c_binning_tricks() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Binning tricks in histograms (Old Faithful durations)")
    ax1.hist(geyser["duration"], bins=5, color="#CFC6AE", edgecolor=MUTED)
    ax1.set_title("Misleading: 5 wide bins\nhide the bimodal shape", fontsize=10.5)
    ax1.set_xlabel("eruption duration (min)")
    ax2.hist(geyser["duration"], bins=40, color=ACCENT_GREEN, edgecolor=MUTED)
    ax2.set_title("Honest: fine bins reveal\ntwo distinct eruption types", fontsize=10.5)
    ax2.set_xlabel("eruption duration (min)")
    return fig


SECTION_C = [
    ("c01_truncated_axis", "Truncated y-axis", c_truncated_axis,
     "Starting the y-axis above zero stretches small differences into what looks like a large gap. Spot it by checking where the axis actually starts; the honest version starts a bar axis at zero."),
    ("c02_dual_axes", "Dual axes", c_dual_axes,
     "Two independent y-axes can always be rescaled until their lines overlap, making any two trends look locked together. Spot it by asking whether the two axes' ranges were chosen to make the lines match; the honest version puts both series on one shared, meaningful scale (e.g. indexed to 100)."),
    ("c03_area_scaling", "Area / pictogram scaling", c_area_scaling,
     "Scaling an icon's width/radius by the value makes its area grow with the square of the value, exaggerating the ratio. Spot it by checking whether width or area was scaled; the honest version scales area directly."),
    ("c04_cherry_picked_window", "Cherry-picked time window", c_cherry_picked_window,
     "A short window chosen because it happens to show a clean trend hides what the series does outside it. Spot it by asking why that start/end date, specifically; the honest version shows the full available range."),
    ("c05_cumulative_vs_period", "Cumulative vs. per-period", c_cumulative_vs_period,
     "A cumulative total can only go up even while the underlying per-period activity is slowing or falling, which is exactly how Apple's 2013 chart made slowing iPhone growth look unstoppable. Spot it by asking 'cumulative since when?'; the honest version plots the per-period value. Labelled in Apple's own fiscal quarters (FY runs Oct-Sep, one quarter ahead of the calendar) rather than relabelled to calendar quarters, so the axis matches the data it's actually plotting."),
    ("c06_3d_pie", "3D pie", c_3d_pie,
     "Perspective and the squashed ellipse of a 3D pie distort both the angle and the apparent area of each slice, on top of a pie's existing Cleveland problem. Spot it by the fake depth/shadow; the honest version is a flat 2D chart (and a bar is better still)."),
    ("c07_mean_median", "Mean vs. median (skew)", c_mean_median,
     "On a right-skewed distribution the mean is pulled toward the few extreme high values and no longer describes a 'typical' case. Spot it by checking the distribution's shape; the honest version reports the median (or both, named)."),
    ("c08_simpsons_paradox", "Simpson's paradox", c_simpsons_paradox,
     "Pooling two groups with very different sizes and success rates can flip which treatment looks better, as in the classic Charig et al. (1986) kidney-stone data: open surgery wins in both the small-stone and large-stone groups, but PCNL wins pooled, because PCNL was used mostly on the easier small-stone cases. Spot it by asking whether a hidden grouping variable differs between the compared groups; the honest version reports the split."),
    ("c09_spurious_correlation", "Correlation ≠ causation (spurious correlation)", c_spurious_correlation,
     "Any two series that both trend monotonically over the same years will correlate strongly by construction, with no causal link between them (in the spirit of Tyler Vigen's spurious-correlations project, tylervigen.com — redrawn here with two real but unrelated datasets rather than his exact pairing, which we did not have verified numbers for). Spot it by asking whether a shared third cause (here, just time) explains both; the honest version shows both series indexed over time side by side instead of implying a relationship."),
    ("c10_survivorship_bias", "Survivorship bias", c_survivorship_bias,
     "Studying only the aircraft that returned (Abraham Wald, WWII) means the sample has already excluded the planes hit in the fatal spots — the undamaged areas on survivors are exactly where a hit was fatal. Spot it by asking what didn't make it into the sample; the honest version reasons about the missing cases, not just the visible ones."),
    ("c11_base_rate_neglect", "Base-rate neglect", c_base_rate_neglect,
     "A test's accuracy sounds like the chance a positive result is correct, but with a rare condition most positives are still false positives. Spot it by asking for the base rate before trusting a headline accuracy figure; the honest version works through the actual counts (or Bayes' rule)."),
    ("c12_misleading_colour_scale", "Misleading colour scales", c_misleading_colour_scale,
     "A non-perceptually-uniform colormap like 'jet' creates visual bands and false edges that aren't in the underlying values — shown here on a synthetic, perfectly smooth field (sum of two Gaussian bumps, no real edges anywhere) so any banding visible is purely the colormap's doing. Spot it by looking for hard colour boundaries that don't match the data; the honest version uses a perceptually uniform sequential map (viridis, rocket, ...)."),
    ("c13_log_scale", "Log scale without saying so", c_log_scale,
     "A log y-axis compresses large values and makes accelerating growth look steady — not dishonest by itself, but misleading when the axis doesn't say it's log, especially with plain round-number tick labels that give no hint of the log spacing. Spot it by checking whether the tick values are evenly spaced (linear) or not (log); the honest version here plots the same series on a clearly labelled linear axis, where the true accelerating growth is visible."),
    ("c14_binning_tricks", "Binning tricks in histograms", c_binning_tricks,
     "Too few or oddly-placed histogram bins can hide real structure (like Old Faithful's two distinct eruption types) or invent structure that isn't there. Spot it by re-drawing with a different bin count/width and checking whether the shape survives; the honest version picks bins fine enough to show real structure (or uses an ECDF/KDE instead)."),
]

# Round 3: items the user picked from sections A and C. "dropped" items are
# still rendered and described below — PICKED_SO_FAR and the gallery.md tag
# are the record of the decision, not a reason to stop drawing them.
STATUS_A = {key: ("" if key == "a02_raincloud" else "dropped") for key, *_ in SECTION_A}
STATUS_C = {
    "c01_truncated_axis": "", "c02_dual_axes": "", "c04_cherry_picked_window": "",
    "c07_mean_median": "", "c08_simpsons_paradox": "", "c09_spurious_correlation": "",
    "c10_survivorship_bias": "",
    "c11_base_rate_neglect": "backup", "c12_misleading_colour_scale": "backup",
    "c13_log_scale": "backup",
    "c03_area_scaling": "dropped", "c05_cumulative_vs_period": "dropped",
    "c06_3d_pie": "dropped", "c14_binning_tricks": "dropped",
}


# --------------------------------------------------------------------------
# Section D — well-known charts (standard ones part 1 didn't cover)
# --------------------------------------------------------------------------


def d_box_violin_strip() -> plt.Figure:
    fig, axes = plt.subplots(1, 3, figsize=FIGSIZE, dpi=DPI, sharey=True)
    order = sorted(penguins["species"].unique())
    sns.boxplot(penguins, x="species", y="bill_length_mm", order=order, ax=axes[0], color="#CFC6AE")
    axes[0].set_title("Box", fontsize=13)
    sns.violinplot(penguins, x="species", y="bill_length_mm", order=order, ax=axes[1], color="#CFC6AE")
    axes[1].set_title("Violin", fontsize=13)
    sns.stripplot(penguins, x="species", y="bill_length_mm", order=order, ax=axes[2], size=2.5, alpha=0.5, color=INK)
    axes[2].set_title("Strip", fontsize=13)
    for ax in axes[1:]:
        ax.set_ylabel("")
    fig.suptitle("Box vs. violin vs. strip — same data, three views", fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    return fig


def d_grouped_bar() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    sns.barplot(penguins, x="species", y="body_mass_g", hue="sex", ax=ax,
                palette={"Male": ACCENT_GREEN, "Female": ACCENT_YELLOW})
    ax.set_ylabel("mean body mass (g)")
    ax.set_title("Grouped bar — body mass by species and sex")
    fig.tight_layout()
    return fig


def d_stacked_bar() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Stacked bar and 100% stacked bar")
    ct = pd.crosstab(titanic["class"], titanic["survived"])
    ct.columns = ["died", "survived"]
    ct.plot(kind="bar", stacked=True, ax=ax1, color=[BAD_RED, ACCENT_GREEN], legend=False)
    ax1.set_title("Stacked bar — counts", fontsize=12.5)
    ax1.set_xlabel(""); ax1.tick_params(axis="x", rotation=0)
    pct = ct.div(ct.sum(axis=1), axis=0) * 100
    pct.plot(kind="bar", stacked=True, ax=ax2, color=[BAD_RED, ACCENT_GREEN], legend=False)
    ax2.set_title("100% stacked — share", fontsize=12.5)
    ax2.set_xlabel(""); ax2.tick_params(axis="x", rotation=0)
    # Every bar in the 100% panel reaches the top, so there's no free space
    # inside either axes for a legend — one shared legend below both instead.
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (BAD_RED, ACCENT_GREEN)]
    fig.subplots_adjust(bottom=0.24)
    fig.legend(handles, ["died", "survived"], loc="lower center", ncol=2,
               bbox_to_anchor=(0.5, 0.0), fontsize=10.5, frameon=False)
    return fig


def d_pie_donut() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Pie / donut — fine at a few parts, unreadable at many")
    counts3 = titanic["class"].value_counts()
    ax1.pie(counts3.values, labels=counts3.index, autopct="%1.0f%%",
            colors=sns.color_palette("colorblind", len(counts3)), wedgeprops={"width": 0.4})
    ax1.set_title("Fine: 3 parts (donut)", fontsize=12.5)
    counts8 = diamonds["clarity"].value_counts()
    ax2.pie(counts8.values, labels=counts8.index, autopct="%1.0f%%",
            colors=sns.color_palette("flare", len(counts8)), wedgeprops={"width": 0.4})
    ax2.set_title("Not fine: 8 parts (donut)", fontsize=12.5)
    return fig


def d_area() -> plt.Figure:
    fig, ax1, ax2 = pair_fig("Area and stacked area")
    total = flights.groupby("year")["passengers"].sum()
    ax1.fill_between(total.index, total.values, color=ACCENT_GREEN, alpha=0.6)
    ax1.plot(total.index, total.values, color=ACCENT_GREEN)
    ax1.set_title("Area — total passengers/year", fontsize=12.5)
    # Countries are sampled on different, irregular years (e.g. Canada has no
    # 1970 row, France skips most of the 1970s/80s) — pivoting straight to a
    # stackplot leaves NaN gaps that render as spurious vertical spikes.
    # Interpolating each country's own series onto the full year range first
    # gives a smooth, honest composition-over-time read instead.
    piv = healthexp.pivot(index="Year", columns="Country", values="Spending_USD")
    piv = piv.reindex(range(piv.index.min(), piv.index.max() + 1)).interpolate(
        method="linear", limit_direction="both")
    ax2.stackplot(piv.index, piv.T.values, labels=piv.columns,
                  colors=sns.color_palette("colorblind", piv.shape[1]))
    ax2.legend(fontsize=7.5, loc="upper left")
    ax2.set_title("Stacked area — spending by country", fontsize=12.5)
    return fig


def d_bubble() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    sns.scatterplot(penguins, x="bill_length_mm", y="flipper_length_mm", size="body_mass_g",
                     hue="species", sizes=(20, 300), alpha=0.7, ax=ax,
                     palette=dict(zip(sorted(penguins["species"].unique()), sns.color_palette("colorblind", 3))))
    ax.legend(fontsize=8, loc="lower right", ncol=2)
    ax.set_title("Bubble chart — bill length vs. flipper length,\nsize = body mass")
    fig.tight_layout()
    return fig


def d_pairplot() -> plt.Figure:
    g = sns.pairplot(penguins, vars=["bill_length_mm", "flipper_length_mm", "body_mass_g"],
                      hue="species", palette=dict(zip(sorted(penguins["species"].unique()),
                                                       sns.color_palette("colorblind", 3))),
                      plot_kws={"s": 12, "alpha": 0.6}, height=1.5)
    g.figure.suptitle("Pair plot — three penguin measurements", fontsize=13, y=1.02)
    g.figure.set_size_inches(*FIGSIZE)
    g.figure.set_dpi(DPI)
    for ax in g.figure.axes:
        ax.tick_params(labelsize=7)
        ax.xaxis.label.set_size(8)
        ax.yaxis.label.set_size(8)
    if g.legend is not None:
        plt.setp(g.legend.get_texts(), fontsize=9)
        if g.legend.get_title() is not None:
            g.legend.get_title().set_fontsize(10)
    return g.figure


def d_corr_heatmap() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    corr = diamonds[["carat", "depth", "table", "price"]].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, mask=mask, cmap="coolwarm", vmin=-1, vmax=1, center=0, annot=True, fmt=".2f",
                square=True, ax=ax, cbar_kws={"label": "Pearson r"})
    ax.set_title("Correlation matrix — annotated, diverging,\nupper triangle masked")
    fig.tight_layout()
    return fig


def d_error_bars() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    order = sorted(penguins["species"].unique())
    sns.pointplot(penguins, x="species", y="body_mass_g", order=order, errorbar=("ci", 95),
                  ax=ax, color=ACCENT_GREEN, capsize=0.15)
    ax.set_ylabel("mean body mass (g), 95% CI")
    ax.set_title("Error bars — the bars are a 95% CI,\nnot the full spread of the data")
    fig.tight_layout()
    return fig


def d_count_plot() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    sns.countplot(titanic, x="class", hue="survived", ax=ax,
                  palette={0: BAD_RED, 1: ACCENT_GREEN}, order=["First", "Second", "Third"])
    handles, _ = ax.get_legend_handles_labels()
    ax.legend(handles, ["died", "survived"], title="")
    ax.set_title("Count plot — passengers per class")
    fig.tight_layout()
    return fig


def d_radar() -> plt.Figure:
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_subplot(1, 1, 1, polar=True)
    cols = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    norm = penguins[cols].apply(lambda c: (c - c.min()) / (c.max() - c.min()))
    norm["species"] = penguins["species"]
    means = norm.groupby("species", observed=True)[cols].mean()
    angles = np.linspace(0, 2 * np.pi, len(cols), endpoint=False).tolist()
    angles += angles[:1]
    colors = sns.color_palette("colorblind", len(means))
    for (species, row), color in zip(means.iterrows(), colors):
        vals = row.tolist() + row.tolist()[:1]
        ax.plot(angles, vals, color=color, label=species)
        ax.fill(angles, vals, color=color, alpha=0.15)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(["bill length", "bill depth", "flipper length", "body mass"], fontsize=9)
    ax.tick_params(axis="x", pad=14)  # otherwise the left-hand spoke label clips against the frame
    ax.set_yticklabels([])
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=9)
    ax.set_title("Radar / spider — four measurements,\nnormalised 0-1, by species", y=1.2)
    fig.subplots_adjust(left=0.12, right=0.82, top=0.78)
    return fig


def d_pareto() -> plt.Figure:
    fig, ax1 = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    counts = diamonds["clarity"].value_counts().sort_values(ascending=False)
    cum_pct = counts.cumsum() / counts.sum() * 100
    ax1.bar(counts.index, counts.values, color=ACCENT_GREEN)
    ax1.set_ylabel("count")
    ax2 = ax1.twinx()
    ax2.plot(counts.index, cum_pct.values, color=BAD_RED, marker="o")
    ax2.axhline(80, color=BAD_RED, linestyle=":", linewidth=1)
    ax2.set_ylabel("cumulative %", color=BAD_RED)
    ax2.set_ylim(0, 105)
    ax1.set_title("Pareto chart — diamonds by clarity grade,\nsorted bars + cumulative %")
    fig.tight_layout()
    return fig


def d_waterfall() -> plt.Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    labels = ["Start", "+ Grant", "- Equipment", "- Staff time", "End"]
    values = [2000, 1500, -800, -1200, None]
    running = 2000
    bottoms, heights, colors = [0], [2000], [MUTED]
    for v in values[1:-1]:
        if v >= 0:
            bottoms.append(running); heights.append(v); colors.append(ACCENT_GREEN)
        else:
            running += v
            bottoms.append(running); heights.append(-v); colors.append(BAD_RED)
        running = bottoms[-1] + heights[-1] if v >= 0 else running
    running = 2000 + 1500 - 800 - 1200
    bottoms.append(0); heights.append(running); colors.append(MUTED)
    ax.bar(labels, heights, bottom=bottoms, color=colors)
    for x, (b, h) in enumerate(zip(bottoms, heights)):
        ax.text(x, b + h + 40, f"{b + h if x in (0, 4) else h:,.0f}", ha="center", fontsize=10)
    ax.set_ylabel("budget (synthetic units)")
    ax.set_title("Waterfall — a budget walk (synthetic, illustrative only)")
    fig.tight_layout()
    return fig


def d_facetgrid_small_multiples() -> plt.Figure:
    g = sns.catplot(data=penguins, x="species", y="body_mass_g", col="island", kind="box",
                     color="#CFC6AE", height=2.2, aspect=0.85)
    g.set_titles("{col_name}")
    g.figure.set_size_inches(*FIGSIZE)
    g.figure.set_dpi(DPI)
    for ax in g.figure.axes:
        ax.tick_params(labelsize=9)
        ax.xaxis.label.set_size(10)
        ax.yaxis.label.set_size(10)
        ax.title.set_size(13)
    g.figure.subplots_adjust(top=0.82)
    g.figure.suptitle("Small multiples the seaborn way — catplot(col=...)", fontsize=13, y=0.98)
    return g.figure


SECTION_D = [
    ("d01_box_violin_strip", "Box vs. violin vs. strip", d_box_violin_strip, True, None,
     "Three ways to draw the same distribution: a box (quartiles only), a violin (full shape via KDE), a strip (every raw point).",
     "Answers 'what does this distribution look like' at three levels of detail — box for a quick comparison, violin for shape, strip for seeing the actual n and any gaps/clusters.",
     "Don't use a box alone when the shape matters (it can hide bimodality); don't use a strip alone with large n (overplots).",
     "`sns.boxplot(...)`, `sns.violinplot(...)`, `sns.stripplot(...)` — three calls, same `x=`/`y=`"),
    ("d02_grouped_bar", "Grouped bar", d_grouped_bar, True, None,
     "Bars for one category, grouped side by side by a second category.",
     "Answers 'how does the value compare across two categorical dimensions at once' — e.g. a metric by group and by sub-group.",
     "Don't use with more than ~3-4 sub-groups per cluster or many categories — the clusters get wide and hard to compare.",
     "`sns.barplot(df, x=.., y=.., hue=..)`"),
    ("d03_stacked_bar", "Stacked bar + 100% stacked bar", d_stacked_bar, True, None,
     "A bar split into coloured segments by a second category; the 100% version rescales every bar to the same height so segments show share, not raw total.",
     "Stacked: answers 'what's the total, and its composition'. 100% stacked: answers 'what share does each part hold', comparable across categories with very different totals.",
     "Don't use stacked (non-100%) when the audience needs to compare a middle segment across bars — only the bottom segment and the total are easy to compare.",
     "`pandas` `crosstab(...).plot(kind='bar', stacked=True)`, or `df.div(df.sum(axis=1), axis=0)` first for the 100% version"),
    ("d04_pie_donut", "Pie / donut", d_pie_donut, False, None,
     "A circle split into wedges (or a ring, for donut) sized by share of the whole.",
     "Answers 'what share of the whole does each part hold' — genuinely fine at 2-3 parts, where the comparison is obvious at a glance.",
     "Don't use past ~4-5 parts (this sample's 8-part version is already hard to rank by eye — see Cleveland's ranking, principle B2); use a bar instead.",
     "`ax.pie(values, labels=.., wedgeprops={'width': 0.4})` (the `width` makes it a donut; omit for a plain pie)"),
    ("d05_area", "Area and stacked area", d_area, False, None,
     "A line chart with the area under it filled; stacked area layers several filled series so the top line is their running total.",
     "Plain area: emphasises magnitude/volume over time more than a bare line. Stacked area: answers 'how does the total, and each part's contribution to it, change over time'.",
     "Don't use stacked area with more than ~5-6 series (the bands become hard to read individually) or with series that cross zero.",
     "`ax.fill_between(x, y)` for plain area; `ax.stackplot(x, *series, labels=..)` for stacked"),
    ("d06_bubble", "Bubble chart", d_bubble, True, None,
     "A scatter plot with a third continuous variable mapped to point size (and often a fourth to colour).",
     "Answers 'how do three (or four) variables relate at once' for individual points — e.g. two measurements plus a magnitude.",
     "Don't use when the size differences are subtle (hard to compare area by eye — Cleveland again) or with too many overlapping points.",
     "`sns.scatterplot(df, x=.., y=.., size=.., hue=.., sizes=(min,max))`"),
    ("d07_pairplot", "Pair plot", d_pairplot, False, None,
     "A grid of scatter plots for every pair of chosen variables, with each variable's own distribution on the diagonal.",
     "Answers 'how does every variable relate to every other one' in a single exploratory view — the first thing to run on a new numeric dataset.",
     "Don't use with more than ~5-6 variables (the grid gets too small per panel to read) or for a polished final slide — it's an exploration tool, not a takeaway chart.",
     "`sns.pairplot(df, vars=[...], hue=..)`"),
    ("d08_corr_heatmap", "Correlation-matrix heatmap", d_corr_heatmap, True, None,
     "A heatmap of pairwise correlation coefficients, with a diverging colour scale centred on zero, annotated values, and the redundant upper triangle masked out.",
     "Answers 'which variables move together, and how strongly' across many variables at once, faster than scanning a pair plot.",
     "Don't use a sequential colormap here (correlation is signed, -1 to 1 — needs diverging, see principle B4) or skip the mask (the matrix is symmetric; showing both triangles doubles the ink for no new information).",
     "`sns.heatmap(df.corr(), mask=np.triu(...), cmap='coolwarm', center=0, annot=True)`"),
    ("d09_error_bars", "Error bars / confidence intervals", d_error_bars, True, None,
     "A point or bar estimate (here, a mean) with a line through it marking a confidence interval — the range the true value plausibly falls in, not the spread of the raw data.",
     "Answers 'how sure are we about this estimate' — whether two groups' CIs overlap is a quick, honest check for whether a difference is likely real.",
     "Don't present a bar/point estimate without some error indicator when the audience might compare groups — and don't label the interval as 'the data's spread' (it isn't; that's a box/violin's job).",
     "`sns.pointplot(df, x=.., y=.., errorbar=('ci', 95))`, or `sns.barplot(..., errorbar=...)`"),
    ("d10_count_plot", "Count plot", d_count_plot, False, None,
     "A bar chart where the bar height is just the count of rows in each category — seaborn builds the tally for you.",
     "Answers 'how many of each category are there' straight from raw rows, without a manual `.value_counts()` first.",
     "Don't use when the quantity of interest isn't a row count (use `barplot` with an explicit `y=` for a computed statistic instead).",
     "`sns.countplot(df, x=.., hue=..)`"),
    ("d11_radar", "Radar / spider chart", d_radar, False, None,
     "Several normalised variables plotted as spokes around a circle, one polygon per entity.",
     "Answers 'how does this entity's profile compare across several variables at once' — popular for comparing a handful of named things (players, products, species).",
     "Don't use with more than ~6-8 spokes (hard to read) or more than ~4-5 overlaid entities (the polygons occlude each other); and never to compare magnitude precisely — spoke length is easy to misjudge.",
     "No seaborn/matplotlib radar primitive — build with `fig.add_subplot(polar=True)`, `ax.plot`/`ax.fill` on angles from `np.linspace(0, 2*pi, n, endpoint=False)`"),
    ("d12_pareto", "Pareto chart", d_pareto, True, None,
     "Bars sorted largest to smallest, with a line tracking the cumulative percentage of the total as you move left to right.",
     "Answers the classic 80/20 question: 'how many categories account for most of the total' — where the cumulative line crosses 80% is the answer.",
     "Don't use when the categories have a natural order that isn't by size (e.g. time periods) — sorting breaks that order and the chart stops answering a real question.",
     "`ax.bar(sorted_counts)` + `ax.twinx().plot(cumulative_pct)` — no single seaborn/matplotlib call does both"),
    ("d13_waterfall", "Waterfall chart", d_waterfall, False, None,
     "A bar chart where each bar starts where the running total left off, so positive and negative steps visibly build up to (or draw down from) a final total.",
     "Answers 'what added to, and what subtracted from, this total, and by how much' — a budget, a bridge from one period's number to the next.",
     "Don't use when the steps aren't genuinely additive (they must sum to the start/end values) or there are more than ~6-8 steps (the bridge gets hard to follow).",
     "`ax.bar(labels, heights, bottom=running_totals)` — no seaborn/matplotlib waterfall primitive"),
    ("d14_facetgrid", "Small multiples via FacetGrid/catplot", d_facetgrid_small_multiples, False, None,
     "The seaborn-native way to build small multiples: pass `col=` (and/or `row=`) to a figure-level function and it builds the grid, shared axes, and legend for you.",
     "Same question as A1's small multiples (compare many groups at once) — this is the idiomatic seaborn call instead of a hand-rolled `plt.subplots` loop.",
     "Don't reach for this over a hand-built grid when you need per-panel customisation the figure-level API doesn't expose (different chart types per panel, custom per-panel annotation).",
     "`sns.catplot(df, x=.., y=.., col=.., kind='box')`, or `sns.displot(..., col=..)` for distributions"),
]


# --------------------------------------------------------------------------
# Section E — charts ML people already use
# --------------------------------------------------------------------------
#
# Every chart here fits a small model first (sklearn), purely to have real
# predictions/residuals to plot — the point is the chart, not the model, so
# each one uses the simplest classifier/regressor that gets there and refits
# independently rather than sharing state across functions.


def e_confusion_matrix() -> plt.Figure:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import confusion_matrix
    from sklearn.model_selection import train_test_split

    features = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    X, y = penguins[features], penguins["species"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
    clf = RandomForestClassifier(n_estimators=200, random_state=0).fit(X_train, y_train)
    labels = sorted(y.unique())
    cm = confusion_matrix(y_test, clf.predict(X_test), labels=labels)
    cm_norm = cm / cm.sum(axis=1, keepdims=True)
    fig, ax1, ax2 = pair_fig("Confusion matrix — penguin species classifier (held-out test set)")
    sns.heatmap(cm, annot=True, fmt="d", cmap="viridis", xticklabels=labels, yticklabels=labels, ax=ax1, cbar=False)
    ax1.set_xlabel("predicted"); ax1.set_ylabel("true"); ax1.set_title("Counts", fontsize=12.5)
    sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="viridis", xticklabels=labels, yticklabels=labels, ax=ax2,
                cbar=False, vmin=0, vmax=1)
    ax2.set_xlabel("predicted"); ax2.set_ylabel(""); ax2.set_title("Normalised (row %)", fontsize=12.5)
    return fig


def e_roc_pr() -> plt.Figure:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import auc, average_precision_score, precision_recall_curve, roc_curve
    from sklearn.model_selection import train_test_split

    cols = ["pclass", "age", "fare", "sibsp", "parch"]
    df = titanic.dropna(subset=[*cols, "survived"])
    X, y = df[cols], df["survived"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
    clf = LogisticRegression(max_iter=1000).fit(X_train, y_train)
    proba = clf.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, proba)
    roc_auc = auc(fpr, tpr)
    prec, rec, _ = precision_recall_curve(y_test, proba)
    ap = average_precision_score(y_test, proba)
    fig, ax1, ax2 = pair_fig("ROC and precision-recall — Titanic survival classifier")
    ax1.plot(fpr, tpr, color=ACCENT_GREEN)
    ax1.plot([0, 1], [0, 1], color=MUTED, linestyle="--", linewidth=1)
    ax1.set_xlabel("false positive rate"); ax1.set_ylabel("true positive rate")
    ax1.set_title(f"ROC (AUC = {roc_auc:.2f})", fontsize=12.5)
    ax2.plot(rec, prec, color=ACCENT_YELLOW)
    ax2.set_xlabel("recall"); ax2.set_ylabel("precision")
    ax2.set_title(f"Precision-recall (AP = {ap:.2f})", fontsize=12.5)
    return fig


def e_feature_importance() -> plt.Figure:
    from sklearn.ensemble import RandomForestClassifier

    features = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    X, y = penguins[features], penguins["species"]
    clf = RandomForestClassifier(n_estimators=200, random_state=0).fit(X, y)
    importances = pd.Series(clf.feature_importances_, index=features).sort_values()
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.barh(importances.index, importances.values, color=ACCENT_GREEN)
    ax.set_xlabel("importance (mean decrease in impurity)")
    ax.set_title("Feature importance — penguin species classifier")
    fig.tight_layout()
    return fig


def e_learning_curve() -> plt.Figure:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import learning_curve

    features = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    X, y = penguins[features], penguins["species"]
    train_sizes, train_scores, val_scores = learning_curve(
        RandomForestClassifier(n_estimators=100, random_state=0), X, y,
        train_sizes=np.linspace(0.1, 1.0, 8), cv=5, random_state=0,
    )
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.plot(train_sizes, train_scores.mean(axis=1), marker="o", color=ACCENT_GREEN, label="train")
    ax.plot(train_sizes, val_scores.mean(axis=1), marker="o", color=ACCENT_YELLOW, label="validation")
    ax.set_xlabel("training set size")
    ax.set_ylabel("accuracy")
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.set_title("Learning curve — penguin species classifier")
    fig.tight_layout()
    return fig


def e_residuals() -> plt.Figure:
    from sklearn.linear_model import LinearRegression

    X, y = diamonds_sample[["carat"]], diamonds_sample["price"]
    reg = LinearRegression().fit(X, y)
    resid = y - reg.predict(X)
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.scatter(reg.predict(X), resid, s=8, alpha=0.4, color=MUTED)
    ax.axhline(0, color=BAD_RED, linewidth=1.5)
    ax.set_xlabel("predicted price (USD)")
    ax.set_ylabel("residual (actual - predicted)")
    ax.set_title("Residual plot — price ~ carat (linear fit)\nfan shape: variance grows with price")
    fig.tight_layout()
    return fig


SECTION_E = [
    ("e01_confusion_matrix", "Confusion matrix", e_confusion_matrix, True, "scikit-learn",
     "A grid of predicted class vs. true class counts (or row-normalised rates) for a classifier.",
     "Answers 'which classes does the model actually confuse with which' — far more specific than a single accuracy number.",
     "Don't read counts alone when classes are imbalanced (a few errors on a rare class can be a bigger problem than many on a common one) — check the normalised version too.",
     "`sklearn.metrics.confusion_matrix(y_true, y_pred)`, plotted with `sns.heatmap(cm, annot=True)`"),
    ("e02_roc_pr", "ROC and precision-recall curves", e_roc_pr, True, "scikit-learn",
     "ROC plots true- vs. false-positive rate across every classification threshold; precision-recall plots precision vs. recall across the same thresholds.",
     "Answers 'how good is this classifier across all thresholds, not just the default 0.5' — PR is the one to trust when the positive class is rare.",
     "Don't use ROC/AUC alone on a strongly imbalanced problem (it can look good even when precision is poor) — check precision-recall too.",
     "`sklearn.metrics.roc_curve`/`auc`, `precision_recall_curve`/`average_precision_score`"),
    ("e03_feature_importance", "Feature-importance bar", e_feature_importance, False, "scikit-learn",
     "A sorted, horizontal bar of how much each input feature contributed to a fitted model's predictions.",
     "Answers 'what is the model actually using to decide' — a first, rough check before trusting or explaining a model.",
     "Don't treat built-in importances as a causal explanation, and don't use them to compare models of different types (the scales aren't comparable); consider permutation importance for a fairer comparison.",
     "`clf.feature_importances_` (tree models), plotted with `ax.barh(sorted_features, sorted_importances)`"),
    ("e04_learning_curve", "Learning curve", e_learning_curve, False, "scikit-learn",
     "Train and validation score plotted against training-set size.",
     "Answers 'would this model improve with more data, or is it already maxed out' — and whether the gap between the two lines signals overfitting.",
     "Don't run it on a dataset too small to leave a meaningful validation fold, and don't read a single run's noise as a trend — average over folds (as `learning_curve`'s cross-validation already does).",
     "`sklearn.model_selection.learning_curve(estimator, X, y, train_sizes=.., cv=..)`"),
    ("e05_residuals", "Residual plot", e_residuals, False, "scikit-learn",
     "Predicted value on the x-axis, (actual - predicted) on the y-axis, for a fitted regression.",
     "Answers 'is the model's error random, or is there a pattern left over' — a fan shape, curve, or trend in the residuals means the model is missing something systematic.",
     "Don't skip this for a regression chart that only shows predicted vs. actual — a residual plot makes a systematic pattern far easier to spot than the same information folded into a 45° scatter.",
     "`residuals = y_true - model.predict(X)`, plotted with `ax.scatter(model.predict(X), residuals)`"),
]


# --------------------------------------------------------------------------
# Driver: render every sample, build contact sheets, write gallery.md
# --------------------------------------------------------------------------


def build_contact_sheet(section_key: str, entries: list, image_paths: dict, ncols: int, out_name: str) -> Path:
    nrows = -(-len(entries) // ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3.6, nrows * 2.6), dpi=150)
    axes = np.atleast_2d(axes)
    for i, entry in enumerate(entries):
        r, c = divmod(i, ncols)
        ax = axes[r][c]
        img = plt.imread(image_paths[entry[0]])
        ax.imshow(img)
        # No ax.set_title here: every sample PNG already carries its own title
        # baked in (section A chart name, or section B/C principle/trick name
        # in the figure suptitle) — a tile label on top of that just repeats it.
        ax.axis("off")
    for j in range(len(entries), nrows * ncols):
        r, c = divmod(j, ncols)
        axes[r][c].axis("off")
    fig.suptitle({
        "A": "Chart toolbox", "B": "Principles (before / after)", "C": "How to lie with charts",
        "D": "Well-known charts", "E": "Charts ML people already use",
    }[section_key], fontsize=18)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path = IMG_DIR / out_name
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def wrap(text: str, width: int = 96) -> str:
    return "\n".join(textwrap.wrap(text, width=width)) if text else text


def gallery_md_section_a(image_paths: dict) -> str:
    lines = ["## A. Chart toolbox\n",
             "![Chart toolbox contact sheet](images/contact_sheet_a.png)\n"]
    for key, name, _fn, extra, what, question, when_not, call in SECTION_A:
        tags = []
        if extra:
            tags.append(f"needs `{extra}`, not in seaborn/matplotlib/pandas/scipy")
        if STATUS_A.get(key):
            tags.append(STATUS_A[key])
        flag = f" **({'; '.join(tags)})**" if tags else ""
        lines.append(f"### {name}{flag}\n")
        lines.append(f"![{name}](images/{key}.png)\n")
        lines.append(f"- **What it shows:** {what}")
        lines.append(f"- **Answers well:** {question}")
        lines.append(f"- **When not to use it:** {when_not}")
        lines.append(f"- **Call:** {call}\n")
    return "\n".join(lines)


def gallery_md_section_b() -> str:
    lines = ["## B. Principles (before / after)\n",
             "![Principles contact sheet](images/contact_sheet_b.png)\n"]
    for key, name, _fn, desc in SECTION_B:
        lines.append(f"### {name}\n")
        lines.append(f"![{name}](images/{key}.png)\n")
        lines.append(f"{desc}\n")
    return "\n".join(lines)


def gallery_md_section_c() -> str:
    lines = ["## C. How to lie with charts (misleading vs. honest)\n",
             "![How-to-lie contact sheet](images/contact_sheet_c.png)\n"]
    for key, name, _fn, desc in SECTION_C:
        status = STATUS_C.get(key)
        flag = f" **({status})**" if status else ""
        lines.append(f"### {name}{flag}\n")
        lines.append(f"![{name}](images/{key}.png)\n")
        lines.append(f"{desc}\n")
    return "\n".join(lines)


def _gallery_md_toolbox_section(heading: str, contact_sheet: str, entries: list, status: dict) -> str:
    """Shared renderer for D and E: same (key, name, fn, star, extra, what,
    question, when_not, call) shape as SECTION_A. `star` was this agent's
    "teach this one" suggestion before the user picked; the user's actual
    picks are recorded in `status` instead (see STATUS_D/STATUS_E) and take
    over the tag shown here."""
    lines = [f"## {heading}\n", f"![contact sheet]({contact_sheet})\n"]
    for key, name, _fn, _star, extra, what, question, when_not, call in entries:
        tags = []
        if extra:
            tags.append(f"needs `{extra}`, not in seaborn/matplotlib/pandas/scipy")
        if status.get(key):
            tags.append(status[key])
        flag = f" **({'; '.join(tags)})**" if tags else ""
        lines.append(f"### {name}{flag}\n")
        lines.append(f"![{name}](images/{key}.png)\n")
        lines.append(f"- **What it shows:** {what}")
        lines.append(f"- **Answers well:** {question}")
        lines.append(f"- **When not to use it:** {when_not}")
        lines.append(f"- **Call:** {call}\n")
    return "\n".join(lines)


# Round 3, second pass: the user picked from D and E too, verbatim: "Except
# pareto, waterfall and radar we are fine for D. Except the confusion matrix
# lets ignore the ones from E." All of D and E were already drawn by the time
# this landed, so the dropped ones stay rendered and tagged "(dropped)"
# (not "(dropped, not drawn)", which is only for a pick that arrives before
# the corresponding chart is ever generated).
STATUS_D = {key: ("dropped" if key in ("d11_radar", "d12_pareto", "d13_waterfall") else "")
            for key, *_ in SECTION_D}
STATUS_E = {key: ("" if key == "e01_confusion_matrix" else "dropped") for key, *_ in SECTION_E}


def gallery_md_section_d() -> str:
    return _gallery_md_toolbox_section(
        "D. Well-known charts (not covered in part 1)",
        "images/contact_sheet_d.png", SECTION_D, STATUS_D,
    )


def gallery_md_section_e() -> str:
    return _gallery_md_toolbox_section(
        "E. Charts ML people already use",
        "images/contact_sheet_e.png", SECTION_E, STATUS_E,
    )


def main() -> None:
    image_paths: dict[str, Path] = {}

    print("Section A — chart toolbox")
    for key, name, fn, *_ in SECTION_A:
        fig = fn()
        image_paths[key] = save(fig, key)
        print(f"  {key}: {name} -> {image_paths[key].name}")

    print("Section B — principles")
    for key, name, fn, _desc in SECTION_B:
        fig = fn()
        image_paths[key] = save(fig, key)
        print(f"  {key}: {name} -> {image_paths[key].name}")

    print("Section C — how to lie with charts")
    for key, name, fn, _desc in SECTION_C:
        fig = fn()
        image_paths[key] = save(fig, key)
        print(f"  {key}: {name} -> {image_paths[key].name}")

    print("Section D — well-known charts")
    for key, name, fn, *_ in SECTION_D:
        fig = fn()
        image_paths[key] = save(fig, key)
        print(f"  {key}: {name} -> {image_paths[key].name}")

    print("Section E — charts ML people already use")
    for key, name, fn, *_ in SECTION_E:
        fig = fn()
        image_paths[key] = save(fig, key)
        print(f"  {key}: {name} -> {image_paths[key].name}")

    print("Building contact sheets")
    build_contact_sheet("A", SECTION_A, image_paths, ncols=5, out_name="contact_sheet_a.png")
    build_contact_sheet("B", SECTION_B, image_paths, ncols=4, out_name="contact_sheet_b.png")
    build_contact_sheet("C", SECTION_C, image_paths, ncols=4, out_name="contact_sheet_c.png")
    build_contact_sheet("D", SECTION_D, image_paths, ncols=5, out_name="contact_sheet_d.png")
    build_contact_sheet("E", SECTION_E, image_paths, ncols=3, out_name="contact_sheet_e.png")

    print("Writing gallery.md")
    title_and_picks = textwrap.dedent("""\
        # datavis-2 chart gallery

        ## Picked so far

        """) + PICKED_SO_FAR
    intro = textwrap.dedent(f"""\
        Generated by `make_gallery.py`. Re-run it to regenerate every image and this
        file from scratch:

            uv run --no-project \\
                --with seaborn --with matplotlib --with pandas --with scipy \\
                --with squarify --with pywaffle --with scikit-learn \\
                python make_gallery.py

        Style: {STYLE_NOTE}, with larger fonts applied on top for gallery legibility.
        All images are {int(FIGSIZE[0] * DPI)}x{int(FIGSIZE[1] * DPI)} px.

        Nothing here uses the Digimon dataset, plotly, Altair, or any political
        example. Every real-world example is redrawn from data (never a copied
        image); synthetic data is labelled as such. Dataset sources:

        """)
    sources = "\n".join(f"- **{k}** — {v}" for k, v in DATASET_SOURCES.items())
    body = "\n\n".join([
        title_and_picks,
        intro + sources,
        gallery_md_section_a(image_paths),
        gallery_md_section_b(),
        gallery_md_section_c(),
        gallery_md_section_d(),
        gallery_md_section_e(),
    ])
    (HERE / "gallery.md").write_text(body + "\n")
    print("Done.")


if __name__ == "__main__":
    main()
