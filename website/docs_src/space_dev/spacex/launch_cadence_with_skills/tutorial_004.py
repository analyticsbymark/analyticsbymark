"""
What You'll Learn
=================
- How purposeful ANNOTATION turns a coloured chart into an argument (Kirk Ch 9)
- The difference between LABELLING (naming every value) and ANNOTATING
  (guiding the eye to the one thing that matters)
- Kirk's annotation hierarchy, applied in order of prominence:
    1. Title & subtitle   — the editorial frame, read first
    2. Direct callouts     — 1-2 strategic arrows/notes, NOT every point
    3. Axis labels         — orientation
    4. Source attribution  — credibility
- Why restraint wins: 1-2 deliberate callouts beat a chart smothered in notes
- Output: a before/after pair for the headline BAR chart
    * image 01 — every bar LABELLED (necessary, but no story)
    * image 02 — the same bar ANNOTATED (the reader is guided to the insight)

The chart TYPE (bar) and the COLOUR (the ordered single-hue regime ramp) are
carried forward UNCHANGED from tutorial_003. Only annotation changes here.

Run standalone:
    python3 tutorial_004.py
"""

import sys
from pathlib import Path

# Ensure the parent directory is on the path so `from data.utils import ...`
# works when this script is run directly from the curiosity folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Standard imports
import pandas as pd
import plotly.express as px

# Local imports — data/utils.py is the only sanctioned loader.
from data.utils import get_spacex_data

# ---------------------------------------------------------------------------
# Constants & image export
# ---------------------------------------------------------------------------
IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# Image standards (Analytics by Mark): white background, fixed resolution.
# Inlined here so the tutorial stays copy-paste standalone — no imports from
# the skills folder.
IMG_WIDTH, IMG_HEIGHT, IMG_SCALE = 1200, 800, 2

# --- Carried forward UNCHANGED from tutorial_003 (Kirk Ch 10) ---------------
# Colour ROLE on the bar = GROUPING by acceleration regime. The regimes are an
# *ordered* category, so an ordered light->dark single-hue ramp is honest and
# colour-blind safe (it varies in lightness, not hue). We do not touch colour
# in this step; annotation is the only new variable.
PHASE_ORDER = ["Startup (2006–2013)", "Growth (2014–2019)", "Hyperscale (2020+)"]
PHASE_COLORS = {
    "Startup (2006–2013)": "#9ecae1",   # light
    "Growth (2014–2019)": "#4292c6",    # mid
    "Hyperscale (2020+)": "#084594",    # dark
}

# Annotation ink reuses the darkest regime hue so callouts read as "part of the
# same visual family", not a new colour code (Kirk Ch 9: annotation supports the
# encoding, it does not compete with it).
INK = PHASE_COLORS["Hyperscale (2020+)"]
MUTED = "#9e9e9e"  # mid-grey for low-priority, integrity-level notes

HYPERSCALE_START = 2020  # first year of the Hyperscale regime (from tutorial_003)


def save_chart(fig, name: str) -> None:
    """Export a Plotly figure to images/ on a white background per standards."""
    fig.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    out = IMAGES_DIR / name
    fig.write_image(str(out), width=IMG_WIDTH, height=IMG_HEIGHT, scale=IMG_SCALE)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Data loading & shared shaping (same rules as tutorial_001 / _002 / _003)
# ---------------------------------------------------------------------------
def load_completed(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to launches that actually flew (Success / Failure / Partial)."""
    return df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])]


def yearly_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Launches per year — the single series the bar encodes."""
    return df.groupby("year").size().reset_index(name="launches")


def phase_of(year: int) -> str:
    """Label each year with its acceleration regime (an *ordered* category)."""
    if year <= 2013:
        return PHASE_ORDER[0]
    if year <= 2019:
        return PHASE_ORDER[1]
    return PHASE_ORDER[2]


# ===========================================================================
# IMAGE 1 — LABELLING.  Every bar named; no story.
# ===========================================================================
def bar_labels_only(yearly: pd.DataFrame) -> None:
    """The tutorial_003 bar with a value LABEL on every bar.

    Kirk Ch 9 — LABELLING answers "what value is this?":
    - A number on each bar is a *label*. Labels identify; they make the chart
      readable to the decimal, and they are necessary for a precise audience.
    - But labelling everything is not the same as saying anything. With 21 bars
      each wearing a number, nothing is emphasised, so EVERYTHING competes for
      attention and the reader is left to find the story alone.

    This is the honest "before": correct, complete, and mute.
    """
    yearly = yearly.copy()
    yearly["phase"] = yearly["year"].apply(phase_of)

    fig = px.bar(
        yearly, x="year", y="launches", color="phase",
        category_orders={"phase": PHASE_ORDER},
        color_discrete_map=PHASE_COLORS,
        text="launches",  # <- label every bar
        title="Bar — Labelled (every value named, nothing emphasised)",
        labels={"year": "Year", "launches": "Number of Launches", "phase": "Phase"},
    )
    fig.update_traces(textposition="outside", textfont_size=11)
    fig.update_layout(xaxis=dict(dtick=2), legend_title_text="Phase")
    save_chart(fig, "tutorial_004_image_01_bar_labels_only.png")


# ===========================================================================
# IMAGE 2 — ANNOTATING.  The same bar; the eye is guided to the insight.
# ===========================================================================
def bar_annotated(yearly: pd.DataFrame) -> None:
    """The same coloured bar, now ANNOTATED to carry the argument.

    Kirk Ch 9 — ANNOTATING answers "what should I notice?":
    - Annotations are editorial. They carry the author's reading of the data.
    - Strategic means SELECTIVE. We add just TWO direct callouts — the moment
      the curve bends and the payoff it leads to — because 1-2 deliberate notes
      land, whereas a callout on every bar is just labelling with arrows.

    Kirk's annotation hierarchy, applied in order of prominence:
      1. TITLE & SUBTITLE   — the first thing read; frames the editorial angle.
      2. DIRECT CALLOUTS    — the two strategic moments below.
      3. AXIS LABELS        — Year / Number of Launches; quiet orientation.
      4. SOURCE             — small, grey, out of the way; credibility not noise.

    Every number in the annotations is DERIVED from the data, so the chart stays
    correct when the dataset is refreshed.
    """
    yearly = yearly.copy()
    yearly["phase"] = yearly["year"].apply(phase_of)

    # --- Derive every annotation value from the data (never hard-code) -------
    first_year = int(yearly["year"].iloc[0])
    first_count = int(yearly["launches"].iloc[0])

    # The trailing year is only partial (the year is still in progress), so it
    # must NOT be mistaken for the peak. We separate it out and quote the peak
    # from completed years only — an honesty point Kirk stresses in Ch 9.
    partial_year = int(yearly["year"].max())
    full_years = yearly[yearly["year"] < partial_year]

    peak_idx = full_years["launches"].idxmax()
    peak_year = int(full_years.loc[peak_idx, "year"])
    peak_count = int(full_years.loc[peak_idx, "launches"])

    # Inflection: the first Hyperscale year vs the one before it (YoY jump).
    hs_count = int(yearly.loc[yearly["year"] == HYPERSCALE_START, "launches"].iloc[0])
    prev_count = int(yearly.loc[yearly["year"] == HYPERSCALE_START - 1, "launches"].iloc[0])
    yoy_pct = round((hs_count - prev_count) / prev_count * 100)

    # Payoff: compound annual growth across the Hyperscale era (2020 -> peak).
    cagr_years = peak_year - HYPERSCALE_START
    cagr_pct = round(((peak_count / hs_count) ** (1 / cagr_years) - 1) * 100)

    fig = px.bar(
        yearly, x="year", y="launches", color="phase",
        category_orders={"phase": PHASE_ORDER},
        color_discrete_map=PHASE_COLORS,
        labels={"year": "Year", "launches": "Number of Launches", "phase": "Phase"},
    )

    # --- Hierarchy 1: TITLE & SUBTITLE ---------------------------------------
    # "SpaceX launches per year" would be a LABEL for the chart. "From 1 to 170"
    # is an ANNOTATION — it tells the reader what to notice before they look.
    fig.update_layout(
        title=dict(
            text=(
                f"From {first_count} to {peak_count}: SpaceX's launch acceleration"
                f"<br><sup style='color:#666'>Completed launches per year, "
                f"{first_year}–{peak_year}  ·  three acceleration regimes  ·  "
                f"{partial_year} is a partial year</sup>"
            ),
            x=0.5, xanchor="center",
        ),
        xaxis=dict(dtick=2),
        legend_title_text="Phase",
        margin=dict(t=110, b=90),
    )

    # --- Hierarchy 2: DIRECT CALLOUT #1 — the inflection ---------------------
    # Where the curve bends. The arrow does the pointing; the text gives the
    # reader the takeaway ("hyperscale begins"), not just the number.
    fig.add_annotation(
        x=HYPERSCALE_START, y=hs_count,
        text=f"Hyperscale begins<br><b>+{yoy_pct}% YoY</b>",
        showarrow=True, arrowhead=2, arrowsize=1.1, arrowcolor=INK,
        ax=-55, ay=-70,
        font=dict(size=12, color=INK),
        bgcolor="white", bordercolor=INK, borderwidth=1, borderpad=4,
    )

    # --- Hierarchy 2: DIRECT CALLOUT #2 — the payoff -------------------------
    # The peak full year, read as compound annual growth across the Hyperscale
    # era. CAGR is the finance audience's native language and — unlike a multiple
    # off the base-1 founding year — it is robust to that fragile denominator.
    fig.add_annotation(
        x=peak_year, y=peak_count,
        text=f"<b>{peak_count} launches</b><br>≈{cagr_pct}% CAGR since {HYPERSCALE_START}",
        showarrow=True, arrowhead=2, arrowsize=1.1, arrowcolor=INK,
        ax=-70, ay=-30,
        font=dict(size=12, color=INK),
        bgcolor="white", bordercolor=INK, borderwidth=1, borderpad=4,
    )

    # --- Integrity note (footnote level, deliberately quiet) -----------------
    # A data-integrity cue, not a story beat — so it is small and grey and sits
    # right on its bar, well below the two real callouts in the hierarchy.
    partial_val = int(yearly.loc[yearly["year"] == partial_year, "launches"].iloc[0])
    fig.add_annotation(
        x=partial_year, y=partial_val,
        text=f"{partial_year} partial", showarrow=False, yshift=12,
        font=dict(size=10, color=MUTED),
    )

    # --- Hierarchy 4: SOURCE ATTRIBUTION -------------------------------------
    fig.add_annotation(
        text="Source: Launch Library 2 API · thespacedevs.com",
        xref="paper", yref="paper", x=0, y=-0.13,
        showarrow=False, font=dict(size=9, color=MUTED),
    )

    save_chart(fig, "tutorial_004_image_02_bar_annotated.png")


# ---------------------------------------------------------------------------
# Main — show the labelling -> annotating progression on the headline bar
# ---------------------------------------------------------------------------
def main() -> None:
    """Annotate the winning bar chart (Kirk Ch 9)."""
    df = load_completed(get_spacex_data())
    yearly = yearly_counts(df)

    print("=" * 66)
    print("ANNOTATION — Kirk Ch 9  (applied to the headline BAR)")
    print("=" * 66)

    bar_labels_only(yearly)   # before: every value named, no emphasis
    bar_annotated(yearly)     # after: two strategic callouts carry the story

    print()
    print("=" * 66)
    print("ANNOTATION DECISIONS — labelling vs annotating")
    print("=" * 66)
    print(f"""
HIERARCHY (Kirk Ch 9, most -> least prominent):
  1. TITLE/SUBTITLE  "From 1 to 170: SpaceX's launch acceleration"
                     -> editorial frame, read before the bars.
  2. CALLOUTS (x2)   the {HYPERSCALE_START} inflection (+YoY) and the peak
                     full year (Hyperscale-era CAGR). TWO, on purpose.
  3. AXIS LABELS     Year / Number of Launches — quiet orientation.
  4. SOURCE          small, grey, bottom-left — credible, not loud.

LABELLING vs ANNOTATING:
  LABELLING  = "this bar is 170"          -> identifies; necessary for precision.
  ANNOTATING = "≈42% CAGR since 2020"     -> interprets; hands over the takeaway.
  Image 01 labels every bar (mute). Image 02 annotates two (an argument).
  CAGR beats a "×first-year" multiple: the 2006 base of 1 makes any multiple a
  fragile artifact, whereas compound growth off the robust Hyperscale base is
  both honest and the finance audience's native language.

RESTRAINT: more notes are not more insight. Two deliberate callouts guide the
eye; a callout on every bar would just be labelling with arrows. The trailing
partial year is flagged quietly so it is never mistaken for the peak.

NEXT (tutorial_final): composition — strip the teaching scaffolding and compose
the single, clean, decision-ready version of this chart.
""")


if __name__ == "__main__":
    main()
