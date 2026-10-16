"""Build the class's one companion notebook from the verified slide code.

    uv run --no-project --with nbformat --with pyyaml python make_notebooks.py [OUT_DIR]

OUT_DIR defaults to Data_Science_be_like's notebooks folder next to this repo
(../ds_be_like/code/notebooks, relative to the Repos folder holding Presenting).
Writes one notebook, datavis_2.ipynb, with one part per activity block of the
screenplay, in its order and wording.

Every exercise cell is a comment-only skeleton, so it never errors when run.
The cell right after it holds the real solution, collapsed in both Colab (its
first line is `# @title Solution { display-mode: "form" }`) and JupyterLab
(its metadata has `"jupyter": {"source_hidden": true}`), so "Run all" plays
top to bottom while the solutions stay out of sight.

Every cell that is also slide code is taken verbatim from the matching
`# %% <beat-id>` cell of verified_snippets.py, so the notebook and the slides
cannot drift apart. The notebook is written without outputs; execute it with
nbconvert to store it with outputs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE.parents[4] / "ds_be_like" / "code" / "notebooks"
SCREENPLAY = HERE.parent / "screenplay.md"


def verified_cells() -> dict[str, str]:
    cells, name, buf = {}, None, []
    for line in (HERE / "verified_snippets.py").read_text().split("\n"):
        if line.startswith("# ═══"):
            break
        match = re.match(r"# %% (\S+)", line)
        if match:
            if name:
                cells[name] = "\n".join(buf).strip("\n")
            name, buf = match.group(1), []
            continue
        if not line.startswith("# ──"):
            buf.append(line)
    if name:
        cells[name] = "\n".join(buf).strip("\n")
    return cells


V = verified_cells()


def v(*ids: str) -> str:
    return "\n".join(V[i] for i in ids)


def as_comment(text: str) -> str:
    """Every line of text, commented out, so it is safe inside a code cell."""
    return "\n".join("# " + line if line.strip() else "#" for line in text.split("\n"))


def activity(beat_id: str, key: str) -> str:
    """A setup task or parking instruction, as the screenplay words it."""
    sys.path.insert(0, str(HERE.parents[2]))
    from presenting_lib import screenplay as sp

    text = sp.load(SCREENPLAY).beat(beat_id).content[key]
    return " ".join(text.split())


# ── the notebook, as (kind, ...) entries ────────────────────────────────────
#   ("md", text)                      a markdown cell
#   ("md2", question, answer)         a visible question, then a hidden answer
#                                      (the answer is prose, so it is commented
#                                      out rather than run as code)
#   ("code", source)                  a given, runnable code cell
#   ("todo", label, stub, solution)   a visible comment-only skeleton, then the
#                                      hidden solution that actually runs

INTRO = """\
Companion notebook to the class **Honest charts** (data visualisation, part 2).
There is one part per notebook block of the class, in the same order:

1. the habits: redraw three charts that break them
2. pick the chart: five questions, the chart is yours to choose
3. fix this chart: in pairs

Between parts 1 and 2 there is the toolbox from the slides, one runnable cell per
chart, to copy from.

**Running it.** On Google Colab everything is already installed: just run the
cells. Locally, install the libraries first: `pip install seaborn scikit-learn`
(seaborn 0.13 or newer).

**Data.** Every table ships with seaborn: `sns.load_dataset(name)` downloads it
once from [mwaskom/seaborn-data](https://github.com/mwaskom/seaborn-data) and
keeps a copy in `~/seaborn-data`, so after the first run the notebook also works
offline.

- `penguins`: three Antarctic penguin species (palmerpenguins);
- `titanic`: the Titanic's passengers;
- `tips`: restaurant bills and tips;
- `mpg`: cars from 1970 to 1982 (UCI Auto MPG);
- `planets`: exoplanets found up to 2014 (NASA Exoplanet Archive);
- `diamonds`: prices and measurements of 53,940 diamonds;
- `car_crashes`: US states' crash and car-insurance figures;
- `flights`: monthly airline passengers, 1949 to 1960;
- `taxis`: New York yellow-taxi trips, February and March 2019."""

DATA_CELL = '''\
# Every table today ships with seaborn. load_dataset downloads it once from
# github.com/mwaskom/seaborn-data and caches it in ~/seaborn-data.
penguins = sns.load_dataset("penguins")
titanic = sns.load_dataset("titanic")
tips = sns.load_dataset("tips")
mpg = sns.load_dataset("mpg")
planets = sns.load_dataset("planets")
diamonds = sns.load_dataset("diamonds")
car_crashes = sns.load_dataset("car_crashes")
flights = sns.load_dataset("flights")
taxis = sns.load_dataset("taxis")

# A download cut short must not pass silently: check every table's size.
rows = {"penguins": 344, "titanic": 891, "tips": 244, "mpg": 398,
        "planets": 1035, "diamonds": 53940, "car_crashes": 51,
        "flights": 144, "taxis": 6433}
for name, expected in rows.items():
    if len(globals()[name]) != expected:
        raise RuntimeError(f"{name} looks incomplete: delete ~/seaborn-data/"
                           f"{name}.csv and run this cell again")
print("all nine tables loaded")'''

TOOLBOX = [
    ("Box, violin, strip: how is it spread out?", "d-spread"),
    ("Violin with the points", "d-raincloud"),
    ("Error bars: how sure is the average?", "d-errorbars"),
    ("Count plot: how many in each group?", "d-countplot"),
    ("Grouped bar: two categories at once", "d-groupedbar"),
    ("Stacked and 100% stacked bar: what share of the whole?", "d-stacked"),
    ("Donut: a share of two or three parts", "d-pie"),
    ("Stacked area: a total over time, and its parts", "d-area"),
    ("Bubble chart: a third number as size", "d-bubble"),
    ("Pair plot: every pair of columns at once", "d-pairplot"),
    ("Correlation heatmap: which columns move together?", "d-corr"),
    ("Small multiples: one panel per group", "d-facets"),
]

NOTEBOOK = [
    ("md", "# Honest charts\n\n" + INTRO
     + "\n\nCells marked **TODO** are yours: write your code where the cell "
       "says `# your code here`. Solutions hidden under each exercise, as the "
       "cell right after it; run all and it defines what later cells need. "
       "Where a question has more than one good chart, the solution says so."),
    ("md", "## Setup"),
    ("code", V["imports"]),
    ("code", DATA_CELL),

    # ── Part 1 ──
    ("md", "## Part 1: the habits\n\n" + activity("act-habits-setup", "task") + "\n\n"
     + activity("act-habits-parking", "instructions").replace(
         "Open datavis_exercises.ipynb, Part 1. ", "")
     + "\n\nThe eight habits: choose the chart by the question; position beats angle; "
       "every mark should carry data; colour that follows the data; point at what "
       "matters; a title that states the takeaway; sort by value; an aspect ratio "
       "that does not exaggerate. From the slides, all of it in a few lines:"),
    ("code", V["b-fixes-code"]),

    ("md", "### Chart A"),
    ("code", 'counts = diamonds["cut"].value_counts()\n'
             "plt.pie(counts, labels=counts.index,\n"
             '        colors=["red", "orange", "yellow", "green", "blue"])\n'
             'plt.title("Figure 1")'),
    ("md2", "**1.1** Which habits does chart A break?\n\n*Your answer:*",
     "**1.1** Which habits does chart A break?\n\n"
     "*Answer:* it asks the reader to rank angles instead of positions, its five "
     "rainbow colours carry no meaning, and \"Figure 1\" says nothing. Ideal and "
     "Premium are easy to rank here; Premium and Very Good are not."),
    ("todo", "1.2 Redraw chart A: horizontal bars, sorted, labelled, with a title that "
             "states the finding.",
     "counts = ____  # diamonds per cut, smallest first\n"
     "ax = ____  # horizontal bars: position, not angle\n"
     'ax.set(xlabel="diamonds", ylabel="")\n'
     'ax.set_title(____)  # the finding, not "Figure 1"',
     'counts = diamonds["cut"].value_counts().sort_values()\n'
     "ax = counts.plot.barh()\n"
     'ax.set(xlabel="diamonds", ylabel="")\n'
     'ax.set_title("Ideal is the most common cut: 40% of diamonds")'),

    ("md", "### Chart B"),
    ("code", 'top = car_crashes.nlargest(10, "ins_premium").sort_values("abbrev")\n'
             'ax = top.plot.bar(x="abbrev", y="ins_premium", hatch="//",\n'
             '                  edgecolor="black")\n'
             'ax.grid(True, color="black")'),
    ("md2", "**1.3** Which habits does chart B break?\n\n*Your answer:*",
     "**1.3** Which habits does chart B break?\n\n"
     "*Answer:* the hatching, the black grid and the one-entry legend are ink that "
     "carries no data; alphabetical order hides the ranking; and nothing says what "
     "`ins_premium` is, or what the chart shows."),
    ("todo", "1.4 Redraw chart B: sorted by value, no extra ink, a labelled axis and "
             "a title that states the finding.",
     "top = ____  # the 10 highest premiums, sorted by value\n"
     'ax = top.plot.barh(x="abbrev", y="ins_premium", legend=False)\n'
     'ax.set(xlabel=____, ylabel="")\n'
     "ax.set_title(____)\n"
     "sns.despine()",
     'top = car_crashes.nlargest(10, "ins_premium").sort_values("ins_premium")\n'
     'ax = top.plot.barh(x="abbrev", y="ins_premium", legend=False)\n'
     'ax.set(xlabel="average car insurance premium (USD)", ylabel="")\n'
     'ax.set_title("New Jersey and Louisiana pay the most for car insurance")\n'
     "sns.despine()"),

    ("md", "### Chart C"),
    ("code", "fig, ax = plt.subplots(figsize=(3, 6))\n"
             'ax.plot(flights["passengers"])'),
    ("md2", "**1.5** Which habits does chart C break?\n\n*Your answer:*",
     "**1.5** Which habits does chart C break?\n\n"
     "*Answer:* tall and narrow, it makes the growth look steeper than it is; its x "
     "axis is the row number, not the date; and there are no labels and no title."),
    ("todo", "1.6 Redraw chart C: dates on the x axis, a wide figure, labels and a "
             "title that states the finding.",
     'flights["date"] = pd.to_datetime(\n'
     '    flights["year"].astype(str) + "-" + flights["month"].astype(str),\n'
     '    format="%Y-%b")\n'
     "fig, ax = plt.subplots(figsize=____)  # wide, not tall\n"
     'ax.plot(flights["date"], flights["passengers"])\n'
     'ax.set(xlabel="", ylabel=____)\n'
     "ax.set_title(____)",
     'flights["date"] = pd.to_datetime(\n'
     '    flights["year"].astype(str) + "-" + flights["month"].astype(str),\n'
     '    format="%Y-%b")\n'
     "fig, ax = plt.subplots(figsize=(10, 4))\n"
     'ax.plot(flights["date"], flights["passengers"])\n'
     'ax.set(xlabel="", ylabel="passengers (thousands)")\n'
     'ax.set_title("Air passengers almost quadrupled from 1949 to 1960")'),
    ("todo", "1.7 *Stretch.* Annotate the one point the chart is about: the busiest "
             "month.",
     'peak = flights.loc[flights["passengers"].idxmax()]\n'
     'ax.annotate(____, xy=(peak["date"], peak["passengers"]),\n'
     '            xytext=(pd.Timestamp("1951-01-01"), 550),\n'
     '            arrowprops={"arrowstyle": "->"})\n'
     "fig",
     'peak = flights.loc[flights["passengers"].idxmax()]\n'
     'ax.annotate("busiest month: July 1960", xy=(peak["date"], peak["passengers"]),\n'
     '            xytext=(pd.Timestamp("1951-01-01"), 550),\n'
     '            arrowprops={"arrowstyle": "->"})\n'
     "fig"),

    # ── the toolbox ──
    ("md", "## The toolbox, from the slides\n\n"
           "One cell per chart from the toolbox section of the class, exactly as on "
           "the slides. Run them, change a column, and copy from them in Part 2. "
           "There is no correct chart for every case: each question has a few good "
           "ones."),
    ("code", V["toolbox-data"]),
    *[entry for title, beat in TOOLBOX
      for entry in (("md", f"### {title}"), ("code", V[beat]))],
    ("md", "### Confusion matrix: where does the model err?\n\n"
           "First a small model, only to have predictions to look at: a logistic "
           "regression that tells the penguin species apart from two measurements."),
    ("code", V["confusion-setup"]),
    ("code", V["d-confusion"]),

    # ── Part 2 ──
    ("md", "## Part 2: pick the chart\n\n" + activity("act-toolbox-setup", "task") + "\n\n"
     + activity("act-toolbox-parking", "instructions").replace("Part 2. ", "")),
    ("todo", "2.1 How are ticket fares spread in each class? (`titanic`: `fare`, `class`)",
     "ax = ____  # one distribution per class\n"
     "ax.set_title(____)",
     'ax = sns.boxplot(titanic, x="fare", y="class")\n'
     'ax.set_title("First-class fares are higher and far more spread out")\n'
     "# also good: sns.violinplot or sns.stripplot with the same x and y"),
    ("todo", "2.2 How sure is the mean bill for smokers and non-smokers? "
             "(`tips`: `total_bill`, `smoker`)",
     "ax = ____  # the mean, with its 95% interval\n"
     "ax.set_title(____)",
     'ax = sns.pointplot(tips, x="smoker", y="total_bill",\n'
     '                   errorbar=("ci", 95), linestyle="none")\n'
     'ax.set_title("The intervals overlap: no clear difference in mean bill")'),
    ("todo", "2.3 What share of each class were men, women and children? "
             "(`titanic`: `who`, `class`)",
     "shares = ____  # one row per class, its shares adding up to 1\n"
     "ax = ____\n"
     "ax.set_title(____)",
     'shares = pd.crosstab(titanic["class"], titanic["who"], normalize="index")\n'
     "ax = shares.plot.bar(stacked=True, rot=0)\n"
     'ax.legend(title="who", loc="center left", bbox_to_anchor=(1, 0.5))\n'
     'ax.set_title("Women were 42% of first class but 23% of third")'),
    ("todo", "2.4 Which diamond measurements move together? (`diamonds`: `carat`, "
             "`depth`, `table`, `price`)",
     'cols = ["carat", "depth", "table", "price"]\n'
     "ax = ____  # correlations, on a diverging map centred on zero\n"
     "ax.set_title(____)",
     'cols = ["carat", "depth", "table", "price"]\n'
     'ax = sns.heatmap(diamonds[cols].corr(), annot=True, fmt=".2f",\n'
     '                 cmap="vlag", vmin=-1, vmax=1)\n'
     'ax.set_title("Price moves with carat; depth and table barely move")'),
    ("todo", "2.5 How did fuel economy change by model year, one panel per origin? "
             "(`mpg`: `mpg`, `model_year`, `origin`)",
     "g = ____  # one panel per origin\n"
     "g.figure.suptitle(____, y=1.05)",
     'g = sns.relplot(mpg, x="model_year", y="mpg", col="origin", kind="line")\n'
     'g.figure.suptitle("Fuel economy rose for every origin, 1970 to 1982", y=1.05)'),
    ("todo", "2.6 *Stretch.* A confusion matrix for a classifier of your own: here, who "
             "survived the Titanic, from class, age and sex.",
     'data = titanic.dropna(subset=["age"])\n'
     'X = pd.get_dummies(data[["pclass", "age", "sex"]], drop_first=True)\n'
     'y = data["survived"]\n'
     "X_train, X_test, y_train, y_test = train_test_split(\n"
     "    X, y, test_size=0.3, stratify=y, random_state=0)\n"
     "model = LogisticRegression(max_iter=1000)\n"
     "y_pred = model.fit(X_train, y_train).predict(X_test)\n"
     "cm = ____  # normalised by row\n"
     "ax = ____\n"
     'ax.set(xlabel="predicted", ylabel="true")\n'
     "ax.set_title(____)",
     'data = titanic.dropna(subset=["age"])\n'
     'X = pd.get_dummies(data[["pclass", "age", "sex"]], drop_first=True)\n'
     'y = data["survived"]\n'
     "X_train, X_test, y_train, y_test = train_test_split(\n"
     "    X, y, test_size=0.3, stratify=y, random_state=0)\n"
     "model = LogisticRegression(max_iter=1000)\n"
     "y_pred = model.fit(X_train, y_train).predict(X_test)\n"
     'cm = confusion_matrix(y_test, y_pred, normalize="true")\n'
     'ax = sns.heatmap(cm, annot=True, fmt=".2f", cmap="Greens",\n'
     '                 xticklabels=["died", "survived"],\n'
     '                 yticklabels=["died", "survived"])\n'
     'ax.set(xlabel="predicted", ylabel="true")\n'
     'ax.set_title("82% accurate, yet it misses 30% of the survivors")'),
    ("md2", "**2.7** Pick one question where another chart would also have been right. "
            "Which, and why did you choose yours?\n\n*Your answer:*",
     "**2.7** Pick one question where another chart would also have been right.\n\n"
     "*One answer:* 2.1. A box plot summarises the fares; a violin shows that most "
     "third-class tickets sit in one narrow band; a strip plot shows the handful of "
     "very expensive first-class tickets one by one. Each answers the question."),

    # ── Part 3 ──
    ("md", "## Part 3: fix this chart\n\n" + activity("act-fix-setup", "task") + "\n\n"
     + activity("act-fix-parking", "instructions").replace(
         "Part 3 of the notebook draws this chart from sns.load_dataset(\"taxis\"). ",
         "The cell below draws the chart from the slide, from `sns.load_dataset(\"taxis\")`. ")),
    ("code", V["fix-bad"]),
    ("md2", "**3.1** Write down every problem you can find.\n\n*Your answer:*",
     "**3.1** Write down every problem you can find.\n\n"
     "*Answer:* five at least.\n\n"
     "1. The axis starts at 10, so Manhattan's bar almost vanishes and Queens looks "
     "about thirteen times Manhattan.\n"
     "2. It plots the mean of a skewed variable: a few long airport rides pull every "
     "borough's mean fare up.\n"
     "3. Four rainbow colours that carry no meaning.\n"
     "4. Alphabetical order hides the ranking.\n"
     "5. \"Figure 1\", no y label, and the raw column name `pickup_borough` on the x "
     "axis."),
    ("todo", "3.2 Redraw it so it answers \"where do taxi rides cost the most?\" honestly.",
     "order = ____  # boroughs from most to least expensive\n"
     "ax = ____  # horizontal bars of the median fare\n"
     'ax.set(xlabel=____, ylabel="")\n'
     "ax.set_title(____)",
     V["fix-one-answer"]),
    ("todo", "3.3 *Stretch.* Ask the same data per mile instead of per ride. What "
             "happens to the order, and why?",
     "rides = ____  # drop rides with no distance\n"
     'rides["per_mile"] = ____\n'
     "ax = ____  # the same order as in 3.2\n"
     'ax.set(xlabel="median fare per mile (USD)", ylabel="")\n'
     "ax.set_title(____)",
     V["fix-per-mile"]),
    ("md", "The same taxi rides answer two questions in opposite orders: per ride, "
           "Queens costs the most; per mile, the least, because Queens rides are the "
           "longest. Which chart is honest depends on the question you ask, so say "
           "which one your chart answers."),
]


SOLUTION_TITLE = '# @title Solution { display-mode: "form" }\n'
HIDDEN = {"jupyter": {"source_hidden": True}}


def build() -> nbformat.NotebookNode:
    cells = []
    for entry in NOTEBOOK:
        kind = entry[0]
        if kind == "md":
            cells.append(new_markdown_cell(entry[1]))
        elif kind == "md2":
            _, question, answer = entry
            cells.append(new_markdown_cell(question))
            cells.append(new_code_cell(SOLUTION_TITLE + as_comment(answer),
                                       metadata={"tags": ["solution"], **HIDDEN}))
        elif kind == "code":
            cells.append(new_code_cell(entry[1]))
        elif kind == "todo":
            _, label, stub, solution = entry
            num, text = label.split(" ", 1)
            cells.append(new_markdown_cell(f"**TODO {num}** {text}"))
            cells.append(new_code_cell(as_comment(stub) + "\n# your code here",
                                       metadata={"tags": ["todo"]}))
            cells.append(new_code_cell(SOLUTION_TITLE + solution,
                                       metadata={"tags": ["solution"], **HIDDEN}))
    nb = new_notebook(cells=cells)
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }
    return nb


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    out.mkdir(parents=True, exist_ok=True)
    nb = build()
    nbformat.validate(nb)
    nbformat.write(nb, out / "datavis_2.ipynb")
    print(out / "datavis_2.ipynb", len(nb.cells), "cells")


if __name__ == "__main__":
    main()
