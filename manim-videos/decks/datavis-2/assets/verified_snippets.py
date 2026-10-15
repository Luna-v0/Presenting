"""datavis-2: every line of code that goes on a slide, and every figure the deck shows.

Each `# %% <beat-id>` cell is the code of the screenplay beat with that id,
verbatim, in deck order. Cells marked "not on a slide" set up what the slide
cells need (a small model). The cells are also the skeleton of the companion
notebooks, datavis_exercises.ipynb and datavis_solutions.ipynb in
Data_Science_be_like, which assets/make_notebooks.py builds from them.

Run it in a throwaway environment, never a project's:

    uv run --no-project --with seaborn --with matplotlib --with pandas \
        --with scipy --with scikit-learn python verified_snippets.py [WORKDIR]

Running the file executes the cells the way a notebook does: in order, in one
namespace, each starting on a fresh figure. Without that, every seaborn call
would draw onto the previous cell's axes. Then the checks at the bottom run, and
then the deck figures are written to WORKDIR (default: ./built next to this
file, git-ignored). Pass --no-figures to skip the figures.

Needs network: the datasets come from seaborn.load_dataset (mwaskom/seaborn-data
on GitHub), cached under ~/seaborn-data after the first run. On slides: penguins
(palmerpenguins), titanic, tips, mpg (UCI Auto MPG, 1970-82), planets (NASA
Exoplanet Archive, to 2014), taxis (NYC yellow taxis, Feb-Mar 2019). In the
figures only: flights (airline passengers 1949-60), dowjones (1914-68), diamonds,
car_crashes (US states). Also: the kidney-stone table of Charig et al. (1986),
BMJ 292:879-882; base-rate counts and the smooth colour field are synthetic; the
bomber is an illustration after Wald (1943), not data.

Verified 2026-10-15 with Python 3.12.12, pandas 3.0.6, seaborn 0.13.2,
matplotlib 3.11.1, numpy 2.4.4, scipy 1.17.1, scikit-learn 1.9.1 (the run prints
the versions it used). Expected warnings, with -W default: two
MatplotlibDeprecationWarnings ("vert: bool was deprecated in Matplotlib 3.11")
raised inside seaborn's own boxplot, once for the d-spread cell and once for its
figure; nothing in this file triggers them. Slide code lines stay at or under
60 characters, the most a full-width code panel holds at the legibility floor.
The checks fail loudly if the data or a library changes under the slides.
"""

# %% setup (not on a slide: runs every cell below in order, each on a fresh figure, like a notebook)
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
END_OF_CELLS = "# ═══"


def cells() -> list[tuple[str, str]]:
    """(name, source) of every `# %% <name>` cell after this one, in order."""
    found, name, lines = [], None, []
    for line in Path(__file__).read_text().split("\n"):
        if line.startswith(END_OF_CELLS):
            break
        match = re.match(r"# %% (\S+)", line)
        if match:
            if name:
                found.append((name, "\n".join(lines).strip("\n")))
            name, lines = match.group(1), []
        elif not line.startswith("# ──"):
            lines.append(line)
    if name:
        found.append((name, "\n".join(lines).strip("\n")))
    return [(n, s) for n, s in found if n != "setup"]


def tail() -> str:
    """The code after the cells: checks and figures."""
    text = Path(__file__).read_text()
    return text[text.index("\n" + END_OF_CELLS) + 1:]


if __name__ == "__main__":
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    namespace: dict = {"__name__": "datavis_cells", "HERE": HERE}
    for cell_name, source in cells():
        exec(compile(source, f"cell {cell_name}", "exec"), namespace)
        plt.close("all")
    exec(compile(tail(), "checks and figures", "exec"), namespace)
    namespace["main"](namespace, HERE, sys.argv[1:])
    raise SystemExit(0)

# %% imports
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ── Section 2: eight habits ─────────────────────────────────────────────────

# %% b-fixes-code
penguins = sns.load_dataset("penguins")
means = penguins.groupby("species")["body_mass_g"].mean()
ax = means.sort_values().plot.barh()
ax.set(xlabel="mean body mass (g)", ylabel="")
ax.set_title("Gentoo penguins are over a third heavier")
sns.despine()

# ── Section 4: a small toolbox ──────────────────────────────────────────────

# %% toolbox-data
titanic = sns.load_dataset("titanic")
tips = sns.load_dataset("tips")
mpg = sns.load_dataset("mpg")
planets = sns.load_dataset("planets")

# %% d-spread
kw = dict(data=penguins, x="flipper_length_mm", y="island")
fig, axes = plt.subplots(1, 3, sharey=True)
sns.boxplot(**kw, ax=axes[0])
sns.violinplot(**kw, ax=axes[1])
sns.stripplot(**kw, ax=axes[2])

# %% d-raincloud
sns.violinplot(**kw, inner=None, color="0.85")
sns.stripplot(**kw, color="black", size=3)

# %% d-errorbars
sns.pointplot(tips, x="day", y="tip",
              errorbar=("ci", 95), linestyle="none")

# %% d-countplot
sns.countplot(titanic, x="class", hue="alive")

# %% d-groupedbar
sns.barplot(penguins, x="species", y="body_mass_g",
            hue="sex")

# %% d-stacked
counts = pd.crosstab(titanic["class"], titanic["alive"])
counts.plot.bar(stacked=True)
shares = counts.div(counts.sum(axis=1), axis=0)
shares.plot.bar(stacked=True)

# %% d-pie
classes = titanic["class"].value_counts()
plt.pie(classes, labels=classes.index, autopct="%.0f%%",
        wedgeprops={"width": 0.4}, pctdistance=0.8)

# %% d-area
per_year = pd.crosstab(planets["year"], planets["method"])
per_year[["Radial Velocity", "Transit"]].plot.area()

# %% d-bubble
sns.scatterplot(mpg, x="horsepower", y="mpg",
                size="weight", hue="origin")

# %% d-pairplot
sns.pairplot(mpg, hue="origin",
             vars=["mpg", "weight", "horsepower"])

# %% d-corr
cols = ["mpg", "weight", "horsepower", "acceleration"]
corr = mpg[cols].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag",
            vmin=-1, vmax=1)

# %% d-facets
sns.relplot(mpg, x="weight", y="mpg", col="origin")

# %% confusion-setup (not on a slide: a small model, to have predictions)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

data = penguins.dropna()
X = data[["bill_depth_mm", "flipper_length_mm"]]
y = data["species"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=0)
model = LogisticRegression(max_iter=1000)
y_pred = model.fit(X_train, y_train).predict(X_test)
labels = model.classes_

# %% d-confusion
cm = confusion_matrix(y_test, y_pred, normalize="true")
ax = sns.heatmap(cm, annot=True, fmt=".2f", cmap="Greens",
                 xticklabels=labels, yticklabels=labels)
ax.set(xlabel="predicted", ylabel="true")

# ── Section 7: fix this chart ───────────────────────────────────────────────

# %% fix-bad
taxis = sns.load_dataset("taxis")
fares = taxis.groupby("pickup_borough")["fare"].mean()
ax = fares.plot.bar(color=["red", "gold", "green", "blue"])
ax.set_ylim(10, 26)
ax.set_title("Figure 1")

# %% fix-one-answer
order = ["Queens", "Bronx", "Brooklyn", "Manhattan"]
ax = sns.barplot(taxis, x="fare", y="pickup_borough",
                 estimator="median", order=order,
                 errorbar=None)
ax.set(xlabel="median fare (USD)", ylabel="")
ax.set_title("A Queens pickup costs 2.5x a Manhattan one")

# %% fix-per-mile
rides = taxis[taxis["distance"] > 0].copy()
rides["per_mile"] = rides["fare"] / rides["distance"]
ax = sns.barplot(rides, x="per_mile", y="pickup_borough",
                 estimator="median", order=order,
                 errorbar=None)
ax.set(xlabel="median fare per mile (USD)", ylabel="")
ax.set_title("Per mile, Queens rides are the cheapest")


# ═══ Not slide code below: checks, and the deck's figures ═══════════════════
# Executed by the setup cell after every cell above has run, in their namespace.

import platform
from pathlib import Path

import numpy as np

# The deck identity (identity/tokens.yaml). Charts take their colours from here
# unless the colour map is the point of the beat (jet, viridis, vlag, Greens).
GROUND, INK, MUTED = "#E4DCC6", "#232A24", "#5F5A4B"
FILL, STROKE = "#CFC6AE", "#8C8470"
GREEN, GREEN_TINT, GREEN_DARK = "#3D6349", "#CCE0C6", "#1E3527"
YELLOW, YELLOW_TINT = "#A87F20", "#F6E5A5"

# Kidney-stone outcomes, Charig et al. (1986), BMJ 292:879-882, table II:
# successes / patients, by treatment and stone size.
KIDNEY = {("open", "small"): (81, 87), ("open", "large"): (192, 263),
          ("pcnl", "small"): (234, 270), ("pcnl", "large"): (55, 80)}


def rate(*keys) -> float:
    ok = sum(KIDNEY[k][0] for k in keys)
    return 100 * ok / sum(KIDNEY[k][1] for k in keys)


def deck_data() -> dict:
    """Datasets only the deck's figures use (no slide code reads them)."""
    return {name: sns.load_dataset(name)
            for name in ("flights", "dowjones", "diamonds", "car_crashes")}


def checks(ns: dict, extra: dict) -> None:
    """Fail loudly if the data or a library changed under the slides."""
    penguins, titanic, mpg, planets = ns["penguins"], ns["titanic"], ns["mpg"], ns["planets"]
    taxis, rides = ns["taxis"], ns["rides"]
    tips, flights, dow, diamonds = (ns["tips"], extra["flights"], extra["dowjones"],
                                    extra["diamonds"])

    # b-fixes-code, b6: "over a third heavier" than both other species.
    means = ns["means"]
    assert list(means.sort_values().index) == ["Adelie", "Chinstrap", "Gentoo"]
    for other in ("Adelie", "Chinstrap"):
        assert 1.34 < means["Gentoo"] / means[other] < 1.40, means

    # opening: pooled PCNL wins, split open surgery wins both.
    assert round(rate(("open", "small"), ("open", "large"))) == 78
    assert round(rate(("pcnl", "small"), ("pcnl", "large"))) == 83
    assert rate(("open", "small")) > rate(("pcnl", "small"))
    assert rate(("open", "large")) > rate(("pcnl", "large"))
    # Individual rates by size: small stones 93%/87%, large stones 73%/69%.
    assert round(rate(("open", "small"))) == 93
    assert round(rate(("pcnl", "small"))) == 87
    assert round(rate(("open", "large"))) == 73
    assert round(rate(("pcnl", "large"))) == 69
    # Total patients in kidney-stone study.
    total_patients = sum(KIDNEY[k][1] for k in KIDNEY)
    assert total_patients == 700

    # b2: of the seven colour grades, G is the largest share.
    assert diamonds["color"].value_counts().idxmax() == "G"

    # d-spread: Biscoe has two species, so its flipper lengths have two humps.
    biscoe = penguins[penguins["island"] == "Biscoe"]
    assert set(biscoe["species"]) == {"Adelie", "Gentoo"}

    # d-errorbars: the four days' 95% intervals overlap (normal approximation of
    # seaborn's bootstrap), and Friday's, from only 19 bills, is the widest.
    by_day_tip = tips.groupby("day", observed=True)["tip"]
    half = 1.96 * by_day_tip.std() / np.sqrt(by_day_tip.count())
    low, high = by_day_tip.mean() - half, by_day_tip.mean() + half
    assert low.max() < high.min(), (low, high)
    assert half.idxmax() == "Fri" and by_day_tip.count()["Fri"] == 19

    # d-pie: Third class is over half the ship.
    shares = ns["classes"] / ns["classes"].sum()
    assert round(100 * shares["Third"]) == 55 and round(100 * shares["First"]) == 24
    assert round(100 * shares["Second"]) == 21

    # d-stacked: survival share falls from First to Third.
    share_alive = ns["shares"]["yes"]
    assert share_alive["First"] > share_alive["Second"] > share_alive["Third"]

    # d-area: transit discoveries overtook radial velocity from 2012 on.
    rv, tr = ns["per_year"]["Radial Velocity"], ns["per_year"]["Transit"]
    assert all(tr[y] > rv[y] for y in (2012, 2013, 2014)) and rv[2011] > tr[2011]

    # d-bubble, d-corr: heavier cars, fewer miles per gallon, at -0.83.
    assert round(ns["corr"].loc["weight", "mpg"], 2) == -0.83

    # d-confusion: 83% accurate, yet it calls 70% of Chinstraps Adelie.
    cm = ns["cm"]
    labels = list(ns["labels"])
    chin, adel = labels.index("Chinstrap"), labels.index("Adelie")
    assert round(cm[chin, chin], 2) == 0.30 and round(cm[chin, adel], 2) == 0.70
    accuracy = (ns["y_pred"] == ns["y_test"]).mean()
    assert round(accuracy, 2) == 0.83, accuracy

    # c1: Sunday tips +19% over Friday; from a $2.60 baseline it looks ~5x.
    by_day = tips.groupby("day", observed=True)["tip"].mean()
    assert round(by_day["Sun"] / by_day["Fri"], 2) == 1.19
    assert 4.5 < (by_day["Sun"] - 2.6) / (by_day["Fri"] - 2.6) < 5.0

    # c2: from 1970 to 1982, mpg +79%, weight -27%.
    by_year = mpg.groupby("model_year")[["mpg", "weight"]].mean()
    change = by_year.loc[82] / by_year.loc[70] - 1
    assert round(100 * change["mpg"]) == 79 and round(100 * change["weight"]) == -27

    # c4: July to November 1960 fell 37%, and every year dips in the autumn.
    month = flights.set_index(["year", "month"])["passengers"]
    assert (month[(1960, "Jul")], month[(1960, "Nov")]) == (622, 390)
    assert round(100 * (390 / 622 - 1)) == -37
    assert all(month[(y, "Nov")] < month[(y, "Jul")] for y in range(1949, 1961))

    # b5: the Dow Jones fell 87% from Sep 1929 to Jun 1932.
    price = dow.set_index("Date")["Price"]
    peak, low = price["1929"].idxmax(), price["1929":"1932"].idxmin()
    assert (peak.strftime("%b %Y"), low.strftime("%b %Y")) == ("Sep 1929", "Jun 1932")
    assert round(100 * (price[low] / price[peak] - 1)) == -87

    # c7: mean $3,933, median $2,401.
    assert round(diamonds["price"].mean()) == 3933 and diamonds["price"].median() == 2401

    # c9: passengers and the Dow, yearly: r = 0.98; their yearly changes: r = 0.27.
    pair = spurious_pair(flights, dow)
    assert round(pair["passengers"].corr(pair["dow"]), 2) == 0.98
    changes = pair.pct_change().dropna()
    assert round(changes["passengers"].corr(changes["dow"]), 2) == 0.27

    # c11: 1% prevalence, 90% sensitivity and specificity: 9 of 108 positives are sick.
    assert base_rate() == (9, 99)

    # fix: medians 21 / 16 / 12.5 / 8.5, so Queens is ~2.5x Manhattan; per mile it flips.
    median_fare = taxis.groupby("pickup_borough")["fare"].median()
    assert list(median_fare.sort_values(ascending=False).index) == ns["order"]
    assert round(median_fare["Queens"] / median_fare["Manhattan"], 1) == 2.5
    per_mile = rides.groupby("pickup_borough")["per_mile"].median()
    # ...because Queens rides are the longest.
    assert taxis.groupby("pickup_borough")["distance"].median().idxmax() == "Queens"
    assert list(per_mile.sort_values().index) == ["Queens", "Bronx", "Brooklyn", "Manhattan"]
    assert taxis["fare"].mean() > taxis["fare"].median() * 1.3        # skewed: mean misleads
    mean_fare = ns["fares"]
    assert 10 < mean_fare.min() and mean_fare.max() < 26               # inside the cut axis

    print("checks passed")
    print(f"penguins mean mass: {means.round(0).to_dict()}")
    print(f"kidney stones: pooled open {rate(('open', 'small'), ('open', 'large')):.0f}% "
          f"pcnl {rate(('pcnl', 'small'), ('pcnl', 'large')):.0f}%")
    print(f"confusion: accuracy {accuracy:.2f}, Chinstrap recall {cm[chin, chin]:.2f}")
    print(f"taxi median fare {median_fare.round(2).to_dict()}")
    print(f"taxi median per mile {per_mile.round(2).to_dict()}")


def spurious_pair(flights, dow) -> pd.DataFrame:
    passengers = flights.groupby("year")["passengers"].sum()
    yearly_dow = dow.groupby(dow["Date"].dt.year)["Price"].mean()
    return pd.concat([passengers.rename("passengers"), yearly_dow.rename("dow")],
                     axis=1).dropna()


def base_rate(people=1000, prevalence=0.01, sensitivity=0.9, specificity=0.9):
    sick = round(people * prevalence)
    true_pos = round(sick * sensitivity)
    false_pos = round((people - sick) * (1 - specificity))
    return true_pos, false_pos


# ── figures ─────────────────────────────────────────────────────────────────
#
# Sized in slide units (the frame is 14.22 x 8): a figure that will be shown
# 6.26 units wide is drawn 6.26 * K inches wide, so a font size means the same
# thing on every slide. At K = 0.55 a 14 pt tick label is 0.23 units tall
# (cap height), above the deck's legibility floor of about 0.20; axis labels
# are 16 pt, headers 18 pt. Every image is 1600 px on its long edge, the most
# manim can use without paying for pixels nobody sees.

K = 0.55
LONG_EDGE = 1600
TICK, LABEL, HEAD = 14, 16, 18
TWO_UP = (6.26, 4.42)          # one panel of two-up-compare
WIDE = (8.0, 3.39)             # claim-above-figure's visual slot, under a caption


def style() -> None:
    import matplotlib.pyplot as plt
    from cycler import cycler

    path = HERE.parents[2] / "identity" / "out" / "presenting.mplstyle"
    if path.exists():
        plt.style.use(str(path))
    plt.rcParams.update({
        "font.size": TICK, "axes.titlesize": LABEL + 1, "axes.labelsize": LABEL,
        "xtick.labelsize": TICK, "ytick.labelsize": TICK,
        "legend.fontsize": TICK, "legend.title_fontsize": TICK,
        "figure.titlesize": HEAD, "figure.titleweight": "bold",
        "savefig.bbox": "standard",
        # Muted for a single series; green then yellow when a hue splits it.
        "axes.prop_cycle": cycler(color=[MUTED, GREEN, YELLOW, STROKE]),
    })
    sns.set_palette([MUTED, GREEN, YELLOW, STROKE])


def deck_figures(ns: dict, extra: dict, out: Path) -> list[Path]:
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from PIL import Image

    style()
    written: list[Path] = []

    def new(size, nrows=1, ncols=1, layout="constrained", **kw):
        w, h = size
        return plt.subplots(nrows, ncols, figsize=(w * K, h * K),
                            dpi=LONG_EDGE / (max(w, h) * K), layout=layout, **kw)

    def save(fig, name):
        path = out / f"{name}.png"
        fig.savefig(path, dpi=fig.dpi)
        plt.close(fig)
        with Image.open(path) as image:
            assert max(image.size) <= LONG_EDGE, (name, image.size)
        written.append(path)

    def header(fig, text):
        fig.suptitle(text, fontsize=HEAD, fontweight="bold", color=INK)

    def resize_grid(grid, size):
        """A seaborn figure-level grid, resized to slide units, laid out again."""
        w, h = size
        grid.figure.set_size_inches(w * K, h * K)
        grid.figure.set_dpi(LONG_EDGE / (max(w, h) * K))
        grid.figure.set_layout_engine("constrained")
        return grid.figure

    penguins, titanic, mpg = ns["penguins"], ns["titanic"], ns["mpg"]
    taxis, rides, order, kw = ns["taxis"], ns["rides"], ns["order"], ns["kw"]
    tips, flights, dow = ns["tips"], extra["flights"], extra["dowjones"]
    diamonds, crashes = extra["diamonds"], extra["car_crashes"]
    species = ["Adelie", "Chinstrap", "Gentoo"]
    mass = penguins.groupby("species")["body_mass_g"].mean().reindex(species)

    # ── Section 1: the opening chart ──
    fig, ax = new(WIDE)
    pooled = [rate(("open", "small"), ("open", "large")),
              rate(("pcnl", "small"), ("pcnl", "large"))]
    bars = ax.bar(["Open surgery", "PCNL (keyhole)"], pooled, color=[GREEN, YELLOW],
                  width=0.5)
    ax.bar_label(bars, labels=[f"{v:.0f}%" for v in pooled], padding=4, fontsize=LABEL + 2)
    ax.set(ylim=(0, 100), ylabel="success rate (%)")
    ax.grid(axis="x", visible=False)
    save(fig, "opening-chart")

    fig, ax = new(WIDE)
    x = np.arange(2)
    for i, (key, name, colour) in enumerate((("open", "Open surgery", GREEN),
                                             ("pcnl", "PCNL (keyhole)", YELLOW))):
        values = [rate((key, "small")), rate((key, "large"))]
        bars = ax.bar(x + (i - 0.5) * 0.36, values, width=0.36, color=colour, label=name)
        ax.bar_label(bars, labels=[f"{v:.0f}%" for v in values], padding=3,
                     fontsize=LABEL)
    ax.set_xticks(x, ["small stones", "large stones"])
    ax.set(ylim=(0, 105), ylabel="success rate (%)")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncols=2)
    save(fig, "opening-split")

    # ── Section 2: habits, before | after ──
    fig, ax = new(TWO_UP)
    ax.plot(species, mass.values, marker="o", color=MUTED)
    ax.set_ylabel("mean body mass (g)")
    save(fig, "b1-question-l")
    fig, ax = new(TWO_UP)
    ax.bar(species, mass.values, color=MUTED, width=0.6)
    ax.set_ylabel("mean body mass (g)")
    ax.grid(axis="x", visible=False)
    save(fig, "b1-question-r")

    grades = list("DEFGHIJ")
    colour_share = (diamonds["color"].value_counts(normalize=True)
                    .reindex(grades) * 100)
    ramp = LinearSegmentedColormap.from_list("sand_green", [FILL, GREEN, GREEN_DARK])
    wedge_colours = [ramp(i / (len(grades) - 1)) for i in range(len(grades))]
    fig, ax = new(TWO_UP)
    ax.pie(colour_share.values, labels=grades, colors=wedge_colours, startangle=90,
           counterclock=False, wedgeprops={"edgecolor": GROUND, "linewidth": 1.5},
           textprops={"fontsize": LABEL})
    save(fig, "b2-position-l")
    fig, ax = new(TWO_UP)
    ax.barh(grades[::-1], colour_share.values[::-1], color=MUTED, height=0.65)
    ax.set_xlabel("diamonds of this colour grade (%)")
    ax.grid(axis="y", visible=False)
    save(fig, "b2-position-r")

    top6 = crashes.nlargest(6, "total").sort_values("total")
    crash_label = "drivers in fatal crashes\nper billion miles"
    fig, ax = new(TWO_UP)
    ax.set_facecolor(FILL)
    ax.barh(top6["abbrev"], top6["total"], color=STROKE, edgecolor=INK, linewidth=2,
            hatch="//", label="total")
    ax.grid(True, which="both", axis="both", color=MUTED, linewidth=1.4)
    ax.minorticks_on()
    ax.grid(True, which="minor", color=MUTED, linewidth=0.6)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(2.5)
        spine.set_color(INK)
    ax.legend(loc="lower right", frameon=True, edgecolor=INK)
    ax.set_xlabel(crash_label)
    save(fig, "b3-data-ink-l")
    fig, ax = new(TWO_UP)
    ax.barh(top6["abbrev"], top6["total"], color=MUTED, height=0.65)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(crash_label)
    save(fig, "b3-data-ink-r")

    months = flights.pivot(index="month", columns="year", values="passengers")
    for side, cmap in (("l", "jet"), ("r", "viridis")):
        fig, ax = new(TWO_UP)
        sns.heatmap(months, cmap=cmap, ax=ax, cbar_kws={"label": "passengers (thousands)"},
                    xticklabels=3, yticklabels=2)
        ax.grid(False)
        ax.set(xlabel="", ylabel="")
        ax.tick_params(axis="y", rotation=0)
        save(fig, f"b4-colour-{side}")

    price = dow.set_index("Date")["Price"]
    peak, low = price["1929"].idxmax(), price["1929":"1932"].idxmin()
    for side in ("l", "r"):
        fig, ax = new(TWO_UP)
        ax.plot(price.index, price.values, color=MUTED, linewidth=1.8)
        ax.set_ylabel("Dow Jones index")
        ax.set_xticks([pd.Timestamp(f"{y}-01-01") for y in (1920, 1940, 1960)],
                      ["1920", "1940", "1960"])
        if side == "r":
            crash = price[peak:low]
            ax.plot(crash.index, crash.values, color=GREEN, linewidth=3.2)
            drop = 100 * (price[low] / price[peak] - 1)
            ax.annotate(f"1929 to 1932:\n{drop:.0f}%", xy=(peak, price[peak]),
                        xytext=(pd.Timestamp("1915-01-01"), 640), fontsize=LABEL,
                        color=GREEN_DARK,
                        arrowprops={"arrowstyle": "->", "color": GREEN, "linewidth": 2})
        save(fig, f"b5-annotate-{side}")

    for side, title in (("l", "Figure 1"), ("r", "Gentoo penguins are\nover a third heavier")):
        fig, ax = new(TWO_UP)
        ax.bar(species, mass.values, color=MUTED, width=0.6)
        ax.set_ylabel("mean body mass (g)")
        ax.set_title(title, fontsize=LABEL + 1)
        ax.grid(axis="x", visible=False)
        save(fig, f"b6-title-{side}")

    top8 = crashes.nlargest(8, "total")
    for side, ordered in (("l", top8.sort_values("abbrev", ascending=False)),
                          ("r", top8.sort_values("total"))):
        fig, ax = new(TWO_UP)
        ax.barh(ordered["abbrev"], ordered["total"], color=MUTED, height=0.65)
        ax.grid(axis="y", visible=False)
        ax.set_xlabel(crash_label)
        save(fig, f"b7-sort-{side}")

    yearly = flights.groupby("year")["passengers"].sum()
    slopes = np.abs(np.diff(yearly.values) / np.diff(yearly.index.values))
    x_range = yearly.index.max() - yearly.index.min()
    y_range = yearly.max() - yearly.min()
    banked = (y_range / x_range) / np.median(slopes)      # height / width for 45 degrees
    panel_w, panel_h = TWO_UP[0] * K, TWO_UP[1] * K
    ax_h = 0.80
    for side, ax_w in (("l", 0.16), ("r", ax_h * panel_h / banked / panel_w)):
        fig = plt.figure(figsize=(panel_w, panel_h), dpi=LONG_EDGE / panel_w)
        ax = fig.add_axes((0.5 - ax_w / 2 + 0.06, 0.12, ax_w, ax_h))
        ax.plot(yearly.index, yearly.values / 1000, color=MUTED)
        ax.set_ylabel("passengers\n(millions per year)")
        ax.set_xticks([1950, 1960] if side == "l" else [1950, 1955, 1960])
        save(fig, f"b8-aspect-{side}")

    fig, ax = new((11.5, 3.9))
    ax = ns["means"].sort_values().plot.barh(ax=ax)
    ax.set(xlabel="mean body mass (g)", ylabel="")
    ax.set_title("Gentoo penguins are over a third heavier")
    ax.grid(axis="y", visible=False)
    save(fig, "b-fixes-code")

    # ── Section 4: the toolbox (each mirrors its cell) ──
    fig, axes = new((12.4, 4.4), ncols=3, sharey=True)
    for ax, draw, name in zip(axes, (sns.boxplot, sns.violinplot, sns.stripplot),
                              ("box", "violin", "strip")):
        draw(**kw, ax=ax)
        ax.set_title(name)
    header(fig, "Box, violin, strip")
    save(fig, "d-spread")

    fig, ax = new((8.5, 5.1))
    sns.violinplot(**kw, inner=None, color="0.85", ax=ax)
    sns.stripplot(**kw, color="black", size=3, ax=ax)
    header(fig, "Violin with the points")
    save(fig, "d-raincloud")

    fig, ax = new((8.5, 5.1))
    sns.pointplot(tips, x="day", y="tip", errorbar=("ci", 95), linestyle="none", ax=ax)
    header(fig, "Error bars (95% CI)")
    save(fig, "d-errorbars")

    fig, ax = new((8.5, 5.5))
    sns.countplot(titanic, x="class", hue="alive", ax=ax)
    header(fig, "Count plot")
    save(fig, "d-countplot")

    fig, ax = new((8.5, 5.1))
    sns.barplot(penguins, x="species", y="body_mass_g", hue="sex", ax=ax)
    sns.move_legend(ax, "center left", bbox_to_anchor=(1.01, 0.5))
    header(fig, "Grouped bar")
    save(fig, "d-groupedbar")

    fig, (left, right) = new((12.0, 4.6), ncols=2)
    ns["counts"].plot.bar(stacked=True, ax=left, rot=0, legend=False)
    ns["shares"].plot.bar(stacked=True, ax=right, rot=0)
    right.legend(title="alive", loc="center left", bbox_to_anchor=(1.01, 0.5))
    left.set_title("counts")
    right.set_title("shares")
    for ax in (left, right):
        ax.grid(axis="x", visible=False)
    header(fig, "Stacked and 100% stacked bar")
    save(fig, "d-stacked")

    fig, ax = new((8.0, 4.8))
    classes = ns["classes"]
    ax.pie(classes, labels=classes.index, autopct="%.0f%%", wedgeprops={"width": 0.4},
           pctdistance=0.8, textprops={"fontsize": LABEL})
    header(fig, "Donut")
    save(fig, "d-pie")

    fig, ax = new((9.0, 5.1))
    ns["per_year"][["Radial Velocity", "Transit"]].plot.area(ax=ax)
    ax.set(xlabel="year", ylabel="planets found")
    header(fig, "Stacked area")
    save(fig, "d-area")

    fig, ax = new((11.5, 5.1))
    sns.scatterplot(mpg, x="horsepower", y="mpg", size="weight", hue="origin", ax=ax)
    sns.move_legend(ax, "center left", bbox_to_anchor=(1.01, 0.5), ncols=2)
    header(fig, "Bubble chart")
    save(fig, "d-bubble")

    pair_size = (11.0, 5.2)
    with plt.rc_context({"axes.labelsize": TICK}):
        grid = sns.pairplot(mpg, hue="origin", vars=["mpg", "weight", "horsepower"],
                            plot_kws={"s": 16}, height=pair_size[1] * K / 3.4, aspect=1.8)
    sns.move_legend(grid, "center right", bbox_to_anchor=(0.995, 0.5))
    fig = resize_grid(grid, pair_size)
    fig.get_layout_engine().set(rect=(0, 0, 0.84, 1))
    grid.figure.suptitle("Pair plot", fontsize=HEAD, fontweight="bold", color=INK)
    for axis in fig.axes:
        axis.xaxis.set_major_locator(plt.MaxNLocator(3))
        axis.yaxis.set_major_locator(plt.MaxNLocator(3))
    save(fig, "d-pairplot")

    fig, ax = new((8.5, 4.8))
    sns.heatmap(ns["corr"], annot=True, fmt=".2f", cmap="vlag", vmin=-1, vmax=1, ax=ax,
                annot_kws={"fontsize": LABEL})
    ax.grid(False)
    ax.tick_params(axis="y", rotation=0)
    header(fig, "Correlation heatmap")
    save(fig, "d-corr")

    facet_size = (11.5, 5.4)
    grid = sns.relplot(mpg, x="weight", y="mpg", col="origin",
                       height=facet_size[1] * K * 0.82, aspect=1.0, s=22)
    fig = resize_grid(grid, facet_size)
    grid.figure.suptitle("Small multiples", fontsize=HEAD,
                         fontweight="bold", color=INK)
    save(fig, "d-facets")

    fig, ax = new((7.4, 4.6))
    sns.heatmap(ns["cm"], annot=True, fmt=".2f", cmap="Greens", ax=ax,
                xticklabels=ns["labels"], yticklabels=ns["labels"],
                annot_kws={"fontsize": LABEL})
    ax.set(xlabel="predicted", ylabel="true")
    ax.grid(False)
    ax.tick_params(axis="y", rotation=0)
    header(fig, "Confusion matrix")
    save(fig, "d-confusion")

    # ── Section 6: how charts lie, misleading | honest ──
    by_day = tips.groupby("day", observed=True)["tip"].mean()
    for side, bottom in (("l", 2.6), ("r", 0)):
        fig, ax = new(TWO_UP)
        ax.bar(by_day.index.astype(str), by_day.values, color=MUTED, width=0.6)
        ax.set_ylim(bottom, 3.5 if bottom == 0 else 3.35)
        ax.set_ylabel("mean tip (USD)")
        ax.grid(axis="x", visible=False)
        save(fig, f"c1-truncated-{side}")

    cars = mpg.groupby("model_year")[["mpg", "weight"]].mean()
    years = 1900 + cars.index
    fig, ax = new(TWO_UP)
    ax.plot(years, cars["mpg"], color=GREEN)
    ax.set_ylim(15, 35)
    ax.set_ylabel("miles per gallon", color=GREEN_DARK)
    twin = ax.twinx()
    twin.plot(years, cars["weight"], color=YELLOW)
    twin.set_ylim(2200, 3600)
    twin.set_ylabel("weight (lb)", color=YELLOW)
    twin.grid(False)
    twin.spines["right"].set_visible(True)
    ax.set_xticks([1970, 1974, 1978, 1982])
    save(fig, "c2-dual-axes-l")
    fig, ax = new(TWO_UP)
    indexed = cars / cars.iloc[0] * 100
    ax.plot(years, indexed["mpg"], color=GREEN, label="miles per gallon")
    ax.plot(years, indexed["weight"], color=YELLOW, label="weight")
    ax.axhline(100, color=STROKE, linewidth=1.2)
    ax.set_ylabel("1970 = 100")
    ax.set_xticks([1970, 1974, 1978, 1982])
    ax.legend(loc="upper left")
    save(fig, "c2-dual-axes-r")

    stamps = pd.to_datetime(flights["year"].astype(str) + "-" + flights["month"].astype(str),
                            format="%Y-%b")
    monthly = pd.Series(flights["passengers"].values, index=stamps).sort_index()
    window = monthly["1960-07":"1960-11"]
    fig, ax = new(TWO_UP)
    ax.plot(window.index, window.values, color=MUTED, marker="o")
    ax.set_xticks(window.index, [d.strftime("%b") for d in window.index])
    ax.set_ylabel("passengers\n(thousands)")
    ax.set_xlabel("1960")
    save(fig, "c4-window-l")
    fig, ax = new(TWO_UP)
    ax.plot(monthly.index, monthly.values, color=MUTED, linewidth=1.6)
    ax.axvspan(window.index[0], window.index[-1], color=GREEN_TINT, zorder=0)
    ax.plot(window.index, window.values, color=GREEN, linewidth=3)
    ax.set_ylabel("passengers\n(thousands)")
    ax.set_xticks([pd.Timestamp(f"{y}-01-01") for y in (1950, 1955, 1960)],
                  ["1950", "1955", "1960"])
    save(fig, "c4-window-r")

    prices = diamonds["price"]
    for side, value, name, colour in (("l", prices.mean(), "mean", INK),
                                      ("r", prices.median(), "median", GREEN)):
        fig, ax = new(TWO_UP)
        ax.hist(prices, bins=40, color=FILL, edgecolor=STROKE, linewidth=0.6)
        ax.axvline(value, color=colour, linewidth=3)
        ax.text(value + 600, ax.get_ylim()[1] * 0.82, f"{name}\n${value:,.0f}",
                color=colour, fontsize=LABEL)
        ax.set(xlabel="price (USD)", ylabel="diamonds")
        ax.set_xticks([0, 5000, 10000, 15000], ["0", "5,000", "10,000", "15,000"])
        ax.grid(axis="x", visible=False)
        save(fig, f"c7-mean-median-{side}")

    pair = spurious_pair(flights, dow)
    fig, ax = new(TWO_UP)
    ax.scatter(pair["passengers"] / 1000, pair["dow"], color=MUTED, s=50)
    slope, icept = np.polyfit(pair["passengers"] / 1000, pair["dow"], 1)
    xs = np.linspace(1.4, 5.9, 20)
    ax.plot(xs, slope * xs + icept, color=MUTED, linestyle="--", linewidth=1.6)
    ax.set(xlabel="passengers (millions/yr)", ylabel="Dow Jones\n(yearly mean)")
    ax.text(1.5, 590, f"r = {pair['passengers'].corr(pair['dow']):.2f}", fontsize=LABEL + 2)
    save(fig, "c9-spurious-l")
    changes = pair.pct_change().dropna() * 100
    fig, ax = new(TWO_UP)
    ax.scatter(changes["passengers"], changes["dow"], color=GREEN, s=50)
    ax.axhline(0, color=STROKE, linewidth=1)
    ax.set(xlabel="passengers, change (%)", ylabel="Dow, change (%)")
    ax.text(5.5, 28, f"r = {changes['passengers'].corr(changes['dow']):.2f}",
            fontsize=LABEL + 2)
    save(fig, "c9-spurious-r")

    for side in ("l", "r"):
        fig, ax = new(TWO_UP)
        draw_bomber(ax, rng=np.random.default_rng(1943), honest=(side == "r"))
        save(fig, f"c10-survivors-{side}")

    true_pos, false_pos = base_rate()
    fig, ax = new(TWO_UP)
    ax.bar(["what the headline\nsuggests"], [90], color=MUTED, width=0.45)
    ax.set(ylim=(0, 100), ylabel="sick, if positive (%)")
    ax.text(0, 92, "90%", ha="center", fontsize=LABEL + 2)
    ax.grid(axis="x", visible=False)
    save(fig, "c11-base-rate-l")
    fig, ax = new(TWO_UP)
    ax.bar(["positive tests\n(of 1,000 people)"], [true_pos], color=GREEN, width=0.45,
           label=f"sick: {true_pos}")
    ax.bar(["positive tests\n(of 1,000 people)"], [false_pos], bottom=[true_pos],
           color=FILL, edgecolor=STROKE, width=0.45, label=f"not sick: {false_pos}")
    share = 100 * true_pos / (true_pos + false_pos)
    ax.text(0.3, true_pos / 2, f"{share:.0f}% sick", fontsize=LABEL + 2, color=GREEN_DARK,
            va="center")
    ax.set(xlim=(-0.6, 1.1), ylabel="people")
    ax.legend(loc="center right")
    ax.grid(axis="x", visible=False)
    save(fig, "c11-base-rate-r")

    grid_x, grid_y = np.meshgrid(np.linspace(-4, 4, 300), np.linspace(-4, 4, 300))
    field = (np.exp(-((grid_x - 1.3) ** 2 + (grid_y - 1.0) ** 2) / 4.5)
             + 0.75 * np.exp(-((grid_x + 1.6) ** 2 + (grid_y + 0.8) ** 2) / 6.0))
    for side, cmap in (("l", "jet"), ("r", "viridis")):
        fig, ax = new(TWO_UP)
        image = ax.imshow(field, cmap=cmap, origin="lower")
        ax.grid(False)
        fig.colorbar(image, ax=ax, shrink=0.85)
        ax.set_xticks([])
        ax.set_yticks([])
        save(fig, f"c12-colour-scale-{side}")

    import matplotlib.ticker as mticker

    for side in ("l", "r"):
        fig, ax = new(TWO_UP)
        ax.plot(yearly.index, yearly.values, color=MUTED if side == "l" else GREEN)
        if side == "l":
            ax.set_yscale("log")
            ax.yaxis.set_major_locator(mticker.FixedLocator([1500, 2000, 3000, 4000, 6000]))
            ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
            ax.yaxis.set_minor_locator(mticker.NullLocator())
            ax.set_ylabel("passengers per year\n(thousands)")
        else:
            ax.set_ylim(0, 6200)
            ax.set_ylabel("passengers per year\n(thousands, linear)")
        save(fig, f"c13-log-scale-{side}")

    # ── Section 7: fix this chart ──
    fig, ax = new((9.5, 4.6))
    ns["fares"].plot.bar(color=["red", "gold", "green", "blue"], ax=ax)
    ax.set_ylim(10, 26)
    ax.set_title("Figure 1")
    save(fig, "fix-bad")

    for name, data, x, label, title in (
            ("fix-one-answer", taxis, "fare", "median fare (USD)",
             "A Queens pickup costs 2.5x a Manhattan one"),
            ("fix-per-mile", rides, "per_mile", "median fare per mile (USD)",
             "Per mile, Queens rides are the cheapest")):
        fig, ax = new((11.5, 3.9) if name == "fix-one-answer" else (11.5, 3.6))
        sns.barplot(data, x=x, y="pickup_borough", estimator="median", order=order,
                    errorbar=None, ax=ax)
        ax.set(xlabel=label, ylabel="")
        ax.set_title(title)
        ax.grid(axis="y", visible=False)
        save(fig, name)

    return written


def draw_bomber(ax, *, rng, honest: bool) -> None:
    """A top view of a four-engine bomber, with the holes seen on returning planes.

    Illustrative, after the account of Abraham Wald's 1943 memoranda in
    Mangel & Samaniego (1984): hole positions are drawn, not measured.
    """
    import matplotlib.patches as patches

    outline = {"facecolor": FILL, "edgecolor": INK, "linewidth": 1.6}
    ax.add_patch(patches.FancyBboxPatch((-0.09, -1.0), 0.18, 1.95,
                                        boxstyle="round,pad=0.02,rounding_size=0.08",
                                        **outline))
    ax.add_patch(patches.Polygon([(-1.25, 0.12), (1.25, 0.12), (1.15, 0.32),
                                  (-1.15, 0.32)], **outline))
    ax.add_patch(patches.Polygon([(-0.42, -0.86), (0.42, -0.86), (0.36, -0.74),
                                  (-0.36, -0.74)], **outline))
    engines = [(-0.75, 0.22), (-0.38, 0.22), (0.38, 0.22), (0.75, 0.22)]
    for ex, ey in engines:
        ax.add_patch(patches.Ellipse((ex, ey + 0.08), 0.11, 0.34, **outline))
    cockpit = (0.0, 0.83)

    def clear(px, py) -> bool:
        near_engine = any(abs(px - ex) < 0.11 and abs(py - ey - 0.08) < 0.22
                          for ex, ey in engines)
        return not near_engine and py < 0.68

    holes = []
    while len(holes) < 46:
        part = rng.choice(["wing", "body", "tail"], p=[0.55, 0.33, 0.12])
        if part == "wing":
            px, py = rng.uniform(-1.15, 1.15), rng.uniform(0.15, 0.30)
        elif part == "body":
            px, py = rng.uniform(-0.06, 0.06), rng.uniform(-0.7, 0.62)
        else:
            px, py = rng.uniform(-0.38, 0.38), rng.uniform(-0.85, -0.76)
        if clear(px, py):
            holes.append((px, py))
    hx, hy = zip(*holes)
    ax.scatter(hx, hy, s=16, color=INK if not honest else STROKE, zorder=3)
    if honest:
        for ex, ey in engines:
            ax.add_patch(patches.Circle((ex, ey + 0.08), 0.17, fill=False,
                                        edgecolor=GREEN, linewidth=2.6, zorder=4))
        ax.add_patch(patches.Circle(cockpit, 0.15, fill=False, edgecolor=GREEN,
                                    linewidth=2.6, zorder=4))
        ax.text(0, -1.2, "no holes here on planes that came back", ha="center",
                fontsize=TICK, color=GREEN_DARK)
    else:
        ax.text(0, -1.2, "holes on planes that came back", ha="center", fontsize=TICK,
                color=INK)
    ax.text(1.32, -1.38, "illustrative", ha="right", fontsize=TICK - 2, color=MUTED)
    ax.set(xlim=(-1.4, 1.4), ylim=(-1.42, 1.05), aspect="equal")
    ax.axis("off")


def versions() -> str:
    import matplotlib
    import scipy
    import sklearn

    return (f"Python {platform.python_version()}, pandas {pd.__version__}, "
            f"seaborn {sns.__version__}, matplotlib {matplotlib.__version__}, "
            f"numpy {np.__version__}, scipy {scipy.__version__}, "
            f"scikit-learn {sklearn.__version__}")


def main(ns: dict, here: Path, argv: list[str]) -> None:
    paths = [a for a in argv if not a.startswith("--")]
    out = Path(paths[0]).resolve() if paths else here / "built"
    out.mkdir(parents=True, exist_ok=True)
    extra = deck_data()
    checks(ns, extra)
    print(versions())
    if "--no-figures" not in argv:
        written = deck_figures(ns, extra, out)
        print(f"{len(written)} figures in {out}")
