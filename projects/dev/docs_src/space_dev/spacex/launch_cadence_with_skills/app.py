"""
SpaceX Launch Cadence — interactive Dash app (Kirk Ch 8: Interactivity).

Wraps the final chart from tutorial_final.py in a small dashboard. The lesson of
Kirk Ch 8 is that interactivity REPLACES chart proliferation: there is ONE
primary chart, and all the complexity lives in the filters that reshape it.

Three controls, one chart, plus a table to interrogate the underlying data:
  - Year range  (which span of years to show)
  - Phase       (which acceleration regimes to include)
  - Y-axis      (linear counts, or log scale to check the exponential)
  - Data table  (the individual launches behind the current filter — sort,
                 search, and export to CSV)

Run with: python app.py  ->  http://localhost:8050
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dash_table, dcc, html, Input, Output

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data.utils import get_spacex_data

# --- Colour + regime constants, carried forward from tutorial_final ---------
PHASE_ORDER = ["Startup (2006–2013)", "Growth (2014–2019)", "Hyperscale (2020+)"]
PHASE_COLORS = {
    "Startup (2006–2013)": "#9ecae1",
    "Growth (2014–2019)": "#4292c6",
    "Hyperscale (2020+)": "#084594",
}
MUTED = "#9e9e9e"

# The record-level columns to surface in the data table, mapped to human labels.
# Colour shows the aggregate; this table shows the individual launches behind it.
TABLE_COLUMNS = {
    "date": "Date",
    "launch_name": "Mission",
    "rocket_name": "Rocket",
    "mission_type": "Type",
    "launchpad_name": "Pad",
    "launch_status_abbrev": "Status",
}


def phase_for_year(year: pd.Series) -> pd.Series:
    """Vectorised regime label for a year column (same bins as tutorial_final)."""
    return pd.cut(year, bins=[-1, 2013, 2019, 9999], labels=PHASE_ORDER).astype(str)


# ---------------------------------------------------------------------------
# Load + shape the data ONCE at startup (Kirk Ch 8 / claude.md).
# We keep TWO in-memory frames: RECORDS (one launch per row, for the table) and
# YEARLY (aggregated counts, for the chart). Callbacks only filter these — they
# never re-load or re-aggregate from the source.
# ---------------------------------------------------------------------------
def load_records() -> pd.DataFrame:
    df = get_spacex_data()
    df = df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])].copy()
    df["date"] = df["net"].dt.strftime("%Y-%m-%d")
    df["phase"] = phase_for_year(df["year"])
    return df


RECORDS = load_records()
YEARLY = (
    RECORDS.groupby("year").size().reset_index(name="launches")
    .assign(phase=lambda d: phase_for_year(d["year"]))
)
YEAR_MIN = int(YEARLY["year"].min())
YEAR_MAX = int(YEARLY["year"].max())
PARTIAL_YEAR = YEAR_MAX  # the trailing year is still in progress

app = Dash(__name__)
app.title = "SpaceX Launch Cadence"

# ---------------------------------------------------------------------------
# Layout — deliberately minimal. To restyle, drop in a CSS file under assets/
# (Dash auto-loads it) or swap to a component kit like dash-mantine-components.
# ---------------------------------------------------------------------------
app.layout = html.Div(
    style={"maxWidth": "1000px", "margin": "0 auto", "fontFamily": "sans-serif",
           "padding": "1.5rem"},
    children=[
        html.H1("SpaceX Launch Cadence", style={"marginBottom": "0.25rem"}),
        html.P(
            "One chart, three filters, and the launches behind them. Drag the "
            "year range, toggle the acceleration regimes, or switch to a log "
            "axis to test the exponential — the table updates to match.",
            style={"color": "#555", "marginTop": 0},
        ),

        # --- Control 1: year range -----------------------------------------
        html.Label("Year range", style={"fontWeight": "bold"}),
        dcc.RangeSlider(
            id="year-range", min=YEAR_MIN, max=YEAR_MAX, step=1,
            value=[YEAR_MIN, YEAR_MAX],
            marks={y: str(y) for y in range(YEAR_MIN, YEAR_MAX + 1, 2)},
            tooltip={"placement": "bottom", "always_visible": False},
        ),

        html.Div(style={"display": "flex", "gap": "3rem", "marginTop": "1rem"}, children=[
            # --- Control 2: which phases ------------------------------------
            html.Div([
                html.Label("Phase", style={"fontWeight": "bold"}),
                dcc.Checklist(
                    id="phase-pick",
                    options=[{"label": " " + p, "value": p} for p in PHASE_ORDER],
                    value=PHASE_ORDER,
                ),
            ]),
            # --- Control 3: y-axis scale ------------------------------------
            html.Div([
                html.Label("Y-axis", style={"fontWeight": "bold"}),
                dcc.RadioItems(
                    id="y-scale",
                    options=[{"label": " Linear", "value": "linear"},
                             {"label": " Log", "value": "log"}],
                    value="linear",
                ),
            ]),
        ]),

        # --- The ONE primary chart -----------------------------------------
        dcc.Graph(id="cadence-chart"),

        # --- Interrogate the underlying data -------------------------------
        # Kirk Ch 8: the chart shows the aggregate; this table shows the rows
        # behind it. A table is not a second chart — it is the evidence. Sort,
        # search (filter row), and export are all built in.
        # Customise columns / conditional formatting: https://dash.plotly.com/datatable
        html.H3("Launches in view", style={"marginTop": "1.5rem", "marginBottom": "0.5rem"}),
        dash_table.DataTable(
            id="launch-table",
            columns=[{"name": label, "id": key} for key, label in TABLE_COLUMNS.items()],
            sort_action="native",
            filter_action="native",
            page_size=12,
            export_format="csv",
            style_table={"overflowX": "auto"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f0f3f7"},
            style_cell={"fontFamily": "sans-serif", "fontSize": "0.85rem",
                        "padding": "6px 10px", "textAlign": "left"},
        ),
    ],
)


# ---------------------------------------------------------------------------
# Callback — pure function of the controls over the in-memory frames.
# It only filters and restyles; it never touches the data source. One filter
# drives BOTH outputs so the chart and the table can never disagree.
# ---------------------------------------------------------------------------
@app.callback(
    Output("cadence-chart", "figure"),
    Output("launch-table", "data"),
    Input("year-range", "value"),
    Input("phase-pick", "value"),
    Input("y-scale", "value"),
)
def update(year_range, phases, y_scale):
    y0, y1 = year_range
    phases = phases or PHASE_ORDER  # guard: never blank the view entirely

    yearly = YEARLY[YEARLY["year"].between(y0, y1) & YEARLY["phase"].isin(phases)]
    records = RECORDS[RECORDS["year"].between(y0, y1) & RECORDS["phase"].isin(phases)]

    total = int(yearly["launches"].sum())
    fig = px.bar(
        yearly, x="year", y="launches", color="phase",
        category_orders={"phase": PHASE_ORDER},
        color_discrete_map=PHASE_COLORS,
        labels={"year": "Year", "launches": "Number of Launches", "phase": "Phase"},
    )
    fig.update_layout(
        title=dict(
            text=(
                f"SpaceX launch cadence, {y0}–{y1}"
                f"<br><sup style='color:#666'>{total:,} completed launches in view</sup>"
            ),
            x=0.5, xanchor="center",
        ),
        xaxis=dict(dtick=2),
        legend_title_text="Phase",
        margin=dict(t=90, b=60),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    if y_scale == "log":
        fig.update_yaxes(type="log", title_text="Number of Launches (log scale)")

    # Honest partial-year cue, only when that bar is actually in view.
    if y0 <= PARTIAL_YEAR <= y1 and PARTIAL_YEAR in yearly["year"].values:
        partial_val = int(yearly.loc[yearly["year"] == PARTIAL_YEAR, "launches"].iloc[0])
        fig.add_annotation(
            x=PARTIAL_YEAR, y=partial_val, text=f"{PARTIAL_YEAR} partial",
            showarrow=False, yshift=12, font=dict(size=10, color=MUTED),
        )

    table = (
        records.sort_values("date", ascending=False)[list(TABLE_COLUMNS)]
        .to_dict("records")
    )
    return fig, table


if __name__ == "__main__":
    # Local-only. To expose on your network use host="0.0.0.0"; for production
    # serve the WSGI object `app.server` behind gunicorn instead of debug mode.
    app.run(debug=True, port=8050)