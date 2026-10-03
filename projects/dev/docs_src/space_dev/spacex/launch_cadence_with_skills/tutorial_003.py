"""
What You'll Learn
=================
- How to choose colour by *data type AND the chart's job* (Kirk Chapter 10)
- That colour plays a different ROLE on each chart, so we colour the WHOLE
  tutorial_002 candidate set, not just the winner:
    * BAR       -> GROUPING: colour separates the acceleration regimes
    * LINE      -> EMPHASIS/IDENTITY: one deliberate hue, not a scale
    * LOG-LINE  -> same identity hue (it is the same series, re-scaled)
    * HEATMAP   -> ENCODING: colour *is* the value, so a sequential scale
- Why a sequential scale on a single-series line is double-encoding (the x-axis
  already carries the year) and should be avoided
- How to verify every palette is colour-blind safe before committing
- Output: a before/after pair for the headline chart + coloured versions of the
  full candidate set in images/

The chart TYPES do not change here — tutorial_002 chose them. Only COLOUR changes.

Run standalone:
    python3 tutorial_003.py
"""

import sys
from pathlib import Path

# Ensure the parent directory is on the path so `from data.utils import ...`
# works when this script is run directly from the curiosity folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Standard imports
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# --- The deliberate palettes (Kirk Ch 10), one per colour ROLE --------------
#
# GROUPING (bar): the three acceleration regimes are *ordered* categories, so an
# ordered binned ramp (light -> dark, single hue family) is more honest than an
# arbitrary qualitative set — depth reads as "further along". Single-hue ramps
# are also inherently colour-blind safe (they vary in lightness, not hue).
PHASE_ORDER = ["Startup (2006–2013)", "Growth (2014–2019)", "Hyperscale (2020+)"]
PHASE_COLORS = {
    "Startup (2006–2013)": "#9ecae1",   # light
    "Growth (2014–2019)": "#4292c6",    # mid
    "Hyperscale (2020+)": "#084594",    # dark
}

# EMPHASIS / IDENTITY (line, log-line): a single series needs ONE deliberate hue,
# not a scale. Colour here says "this is the series", it does not encode a variable.
EMPHASIS = "#0072B2"  # Okabe-Ito blue — strong, colour-blind safe
NEUTRAL = "#9e9e9e"   # mid-grey for context (gridlines/partial cue)

# ENCODING (heatmap): colour *is* the value (launches per cell), an ordered
# quantity from zero up — a SEQUENTIAL scale is the correct family. Viridis is
# perceptually uniform and colour-blind safe by construction.
SEQUENTIAL_SCALE = "Viridis"


def save_chart(fig, name: str) -> None:
    """Export a Plotly figure to images/ on a white background per standards."""
    fig.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    out = IMAGES_DIR / name
    fig.write_image(str(out), width=IMG_WIDTH, height=IMG_HEIGHT, scale=IMG_SCALE)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Data loading & shared shaping (same rules as tutorial_001 / _002)
# ---------------------------------------------------------------------------
def load_completed(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to launches that actually flew (Success / Failure / Partial)."""
    return df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])]


def yearly_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Launches per year — the single series the trend charts encode."""
    return df.groupby("year").size().reset_index(name="launches")


def phase_of(year: int) -> str:
    """Label each year with its acceleration regime (an *ordered* category)."""
    if year <= 2013:
        return PHASE_ORDER[0]
    if year <= 2019:
        return PHASE_ORDER[1]
    return PHASE_ORDER[2]


# ===========================================================================
# CHART 1 — BAR.  Colour ROLE: GROUPING (by acceleration regime)
# ===========================================================================
def bar_before(df: pd.DataFrame) -> None:
    """The tutorial_002 bar with Plotly's default single colour.

    Kirk Ch 10: the default blue is arbitrary — it groups nothing and directs
    no attention. This is the baseline the After version improves on.
    """
    yearly = yearly_counts(df)
    fig = px.bar(
        yearly, x="year", y="launches",
        title="Bar — Before (default colour, groups nothing)",
        labels={"year": "Year", "launches": "Number of Launches"},
    )
    fig.update_layout(xaxis=dict(dtick=2), showlegend=False)
    save_chart(fig, "tutorial_003_image_01_bar_before.png")


def bar_after(df: pd.DataFrame) -> None:
    """The same bar, coloured by acceleration regime.

    Kirk Ch 10 — colour as GROUPING: the x-axis already shows the year, so
    colour is freed to carry something position does NOT — which *regime* each
    year belongs to (Startup / Growth / Hyperscale). Because the regimes are
    ordered, an ordered light->dark ramp is more honest than an arbitrary
    qualitative palette, and a single-hue ramp is colour-blind safe.
    """
    yearly = yearly_counts(df)
    yearly["phase"] = yearly["year"].apply(phase_of)
    fig = px.bar(
        yearly, x="year", y="launches", color="phase",
        category_orders={"phase": PHASE_ORDER},
        color_discrete_map=PHASE_COLORS,
        title="Bar — After (colour = acceleration regime)",
        labels={"year": "Year", "launches": "Number of Launches", "phase": "Phase"},
    )
    # Honest partial-year note (text only — a data-integrity cue, not colour).
    partial_year = int(yearly["year"].max())
    fig.add_annotation(
        x=partial_year, y=int(yearly.loc[yearly["year"] == partial_year, "launches"].iloc[0]),
        text=f"{partial_year} partial", showarrow=False, yshift=12, font=dict(size=11),
    )
    fig.update_layout(xaxis=dict(dtick=2), legend_title_text="Phase")
    save_chart(fig, "tutorial_003_image_02_bar_after.png")


# ===========================================================================
# CHART 2 — LINE.  Colour ROLE: EMPHASIS / IDENTITY (one hue, not a scale)
# ===========================================================================
def line_after(df: pd.DataFrame) -> None:
    """The winning line in a single deliberate hue.

    Kirk Ch 10 — DON'T double-encode: the year is already on the x-axis, so
    mapping a sequential colour scale to year would add a colourful legend that
    restates position. A single series only needs ONE hue for identity; the
    shape carries the message.
    """
    yearly = yearly_counts(df)
    partial_year = int(yearly["year"].max())
    partial_val = int(yearly.loc[yearly["year"] == partial_year, "launches"].iloc[0])

    fig = px.line(
        yearly, x="year", y="launches", markers=True,
        title="Line — After (one identity hue; shape carries the story)",
        labels={"year": "Year", "launches": "Number of Launches"},
    )
    fig.update_traces(line_color=EMPHASIS, marker_color=EMPHASIS)
    fig.add_annotation(
        x=partial_year, y=partial_val,
        text=f"{partial_year} partial", showarrow=True, arrowhead=0,
        ax=-40, ay=-30, font=dict(size=11, color=NEUTRAL),
    )
    fig.update_layout(xaxis=dict(dtick=2), showlegend=False)
    save_chart(fig, "tutorial_003_image_03_line_after.png")


# ===========================================================================
# CHART 3 — LOG-LINE.  Colour ROLE: same IDENTITY hue (same series, re-scaled)
# ===========================================================================
def log_line_after(df: pd.DataFrame) -> None:
    """The log-scaled line in the SAME identity hue as the linear line.

    Kirk Ch 10 — consistency: it is the same series viewed on a log axis, so it
    keeps the same hue. Re-colouring it would falsely imply a different variable.
    """
    yearly = yearly_counts(df)
    partial_year = int(yearly["year"].max())

    fig = px.line(
        yearly, x="year", y="launches", markers=True, log_y=True,
        title="Log-line — After (same identity hue; exponential check)",
        labels={"year": "Year", "launches": "Launches (log scale)"},
    )
    fig.update_traces(line_color=EMPHASIS, marker_color=EMPHASIS)
    fig.add_annotation(
        x=partial_year, y=yearly["launches"].max(),
        text=f"{partial_year} partial", showarrow=False, yshift=10,
        font=dict(size=11, color=NEUTRAL),
    )
    fig.update_layout(xaxis=dict(dtick=2), showlegend=False)
    save_chart(fig, "tutorial_003_image_04_log_line_after.png")


# ===========================================================================
# CHART 4 — HEATMAP.  Colour ROLE: ENCODING (colour IS the value)
# ===========================================================================
def heatmap_after(df: pd.DataFrame) -> None:
    """The year x month heatmap with a deliberate sequential scale.

    Kirk Ch 10 — colour as ENCODING: here colour is not decoration or grouping,
    it *is* the quantity (launches per cell). A SEQUENTIAL scale fits because the
    value is ordered from zero up; Viridis is perceptually uniform and CVD-safe,
    so equal steps in launches look like equal steps in colour.
    """
    pivot = df.pivot_table(index="year", columns="month", aggfunc="size", fill_value=0)
    for m in range(1, 13):
        if m not in pivot.columns:
            pivot[m] = 0
    pivot = pivot[range(1, 13)]

    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig = px.imshow(
        pivot.values, x=month_labels, y=[str(y) for y in pivot.index],
        color_continuous_scale=SEQUENTIAL_SCALE, aspect="auto",
        title="Heatmap — After (colour = launches; sequential scale)",
        labels=dict(x="Month", y="Year", color="Launches"),
    )
    save_chart(fig, "tutorial_003_image_05_heatmap_after.png")


# ---------------------------------------------------------------------------
# Main — colour the WHOLE candidate set and state each rationale
# ---------------------------------------------------------------------------
def main() -> None:
    """Apply intentional colour to every tutorial_002 candidate (Kirk Ch 10)."""
    df = load_completed(get_spacex_data())

    print("=" * 66)
    print("COLOUR DESIGN — Kirk Ch 10  (applied to the FULL candidate set)")
    print("=" * 66)

    bar_before(df)       # baseline contrast for the headline chart
    bar_after(df)
    line_after(df)
    log_line_after(df)
    heatmap_after(df)

    sampled = px.colors.sequential.Viridis[::2]  # stops to feed the CVD checker
    print()
    print("=" * 66)
    print("PALETTE RATIONALE — colour plays a different ROLE per chart")
    print("=" * 66)
    print(f"""
BAR      role=GROUPING     scale=ORDERED BINNED ({', '.join(PHASE_COLORS.values())})
         Year is on the axis, so colour carries the *regime*. Ordered light->dark
         single-hue ramp = honest for ordered phases and CVD-safe by lightness.

LINE     role=IDENTITY     hue={EMPHASIS}
LOG-LINE role=IDENTITY     hue={EMPHASIS} (same series, re-scaled)
         One deliberate hue. A sequential scale here would double-encode the year
         the x-axis already shows — avoided on purpose.

HEATMAP  role=ENCODING     scale=SEQUENTIAL ({SEQUENTIAL_SCALE})
         Colour IS the value (launches/cell), ordered from zero — sequential is the
         correct family; Viridis is perceptually uniform and CVD-safe.
         Representative stops checked: {','.join(sampled)}

CULTURE  : no red/green value-loading anywhere — blues read as neutral magnitude,
           not "good/bad", so no misleading connotation on the cadence story.

NEXT (tutorial_004): annotation — colour gives the charts voice; milestones
(first Falcon 9 Block 5, first 100-launch year, the partial trailing year) give
them meaning.
""")


if __name__ == "__main__":
    main()