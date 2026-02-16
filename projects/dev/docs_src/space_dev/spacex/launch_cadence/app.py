"""
SpaceX Launch Cadence — Interactive Dash Application
=====================================================

Kirk Chapter 8: Interactivity — letting the reader explore the data
on their own terms, guided by the same editorial framing from the
static composition.

Wraps the primary bar chart from tutorial_final.py with three controls:
  1. Year range slider — zoom into any era
  2. Phase checklist — isolate acceleration phases
  3. Annotation toggle — layer editorial context on/off

Run with: python app.py
Open:     http://localhost:8050
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input

from data.utils import get_spacex_data

IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Data: loaded once at startup, filtered to completed launches
# ---------------------------------------------------------------------------
_raw = get_spacex_data()
DF = _raw[_raw["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])].copy()

PHASE_COLORS = {
    "Startup (2006-2013)": "#B0BEC5",
    "Growth (2014-2019)": "#42A5F5",
    "Hyperscale (2020+)": "#0D47A1",
}

SOURCE = "Source: Launch Library 2 API | thespacedevs.com"

ALL_YEARS = sorted(DF["year"].unique())
MIN_YEAR, MAX_YEAR = ALL_YEARS[0], ALL_YEARS[-1]


def assign_phase(year: int) -> str:
    """Map a year to its acceleration phase."""
    if year <= 2013:
        return "Startup (2006-2013)"
    elif year <= 2019:
        return "Growth (2014-2019)"
    return "Hyperscale (2020+)"


# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------

# Hint: swap Dash(__name__) for Dash(__name__, external_stylesheets=[...])
# to add Bootstrap or another CSS framework for richer styling.
# See: https://dash-bootstrap-components.opensource.faculty.ai/
app = Dash(__name__)

app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "maxWidth": "1200px", "margin": "0 auto", "padding": "24px"},
    children=[
        html.H2("SpaceX Launch Cadence Explorer"),
        html.P(
            "From 1 launch in 2006 to 170 in 2025 — filter by year and acceleration "
            "phase to explore how SpaceX scaled to hyperscale operations.",
            style={"color": "#666", "fontSize": "14px", "marginBottom": "24px"},
        ),

        # --- Controls row ---
        html.Div(
            style={"display": "flex", "gap": "40px", "alignItems": "flex-start", "marginBottom": "24px"},
            children=[
                # Control 1: Year range slider
                html.Div(
                    style={"flex": "1"},
                    children=[
                        html.Label("Year Range", style={"fontWeight": "bold", "marginBottom": "8px"}),
                        dcc.RangeSlider(
                            id="year-range",
                            min=MIN_YEAR,
                            max=MAX_YEAR,
                            value=[MIN_YEAR, MAX_YEAR],
                            marks={str(y): str(y) for y in ALL_YEARS if y % 5 == 0 or y == MIN_YEAR or y == MAX_YEAR},
                            step=1,
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                ),

                # Control 2: Phase filter
                html.Div(
                    style={"minWidth": "220px"},
                    children=[
                        html.Label("Phases", style={"fontWeight": "bold", "marginBottom": "8px"}),
                        dcc.Checklist(
                            id="phase-filter",
                            options=[{"label": phase, "value": phase} for phase in PHASE_COLORS],
                            value=list(PHASE_COLORS.keys()),
                            # Hint: add inline=True for horizontal layout
                            style={"fontSize": "13px"},
                        ),
                    ],
                ),

                # Control 3: Annotation toggle
                html.Div(
                    style={"minWidth": "160px"},
                    children=[
                        html.Label("Annotations", style={"fontWeight": "bold", "marginBottom": "8px"}),
                        dcc.Checklist(
                            id="annotation-toggle",
                            options=[{"label": "Show annotations", "value": "on"}],
                            value=["on"],
                            style={"fontSize": "13px"},
                        ),
                    ],
                ),
            ],
        ),

        # --- Chart ---
        dcc.Graph(id="cadence-chart"),

        # --- Footer ---
        html.P(
            SOURCE,
            style={"color": "#999", "fontSize": "11px", "marginTop": "8px"},
        ),
        # Hint: add dcc.Markdown() here for narrative text or tutorial context.
        # See: https://dash.plotly.com/dash-core-components/markdown
    ],
)


# ---------------------------------------------------------------------------
# Callback: rebuild chart on any control change
# ---------------------------------------------------------------------------
@callback(
    Output("cadence-chart", "figure"),
    Input("year-range", "value"),
    Input("phase-filter", "value"),
    Input("annotation-toggle", "value"),
)
def update_chart(year_range: list, phases: list, annotations: list) -> go.Figure:
    """Rebuild the bar chart from filtered data and optional annotations."""
    y_min, y_max = year_range
    yearly = DF.groupby("year").size().reset_index(name="launches")
    yearly["phase"] = yearly["year"].apply(assign_phase)
    yearly = yearly[(yearly["year"] >= y_min) & (yearly["year"] <= y_max)]
    yearly = yearly[yearly["phase"].isin(phases)]

    fig = px.bar(
        yearly,
        x="year",
        y="launches",
        color="phase",
        labels={"year": "Year", "launches": "Launches", "phase": "Phase"},
        text="launches",
        color_discrete_map=PHASE_COLORS,
        category_orders={"phase": list(PHASE_COLORS.keys())},
    )
    fig.update_traces(textposition="outside", textfont_size=10)

    fig.update_layout(
        title=dict(
            text=(
                "From 1 to 170: SpaceX's Launch Acceleration"
                "<br><sup style='color:#666'>Completed launches per year "
                "— three distinct acceleration phases</sup>"
            ),
            x=0.5,
            xanchor="center",
            font=dict(size=18),
        ),
        xaxis=dict(dtick=1, title="Year"),
        yaxis=dict(title="Launches"),
        height=620,
        margin=dict(t=120, b=80),
        legend=dict(
            orientation="h", yanchor="top", y=-0.08,
            xanchor="center", x=0.5, font=dict(size=11),
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")

    # --- Annotations (only when toggled on) ---
    show = "on" in (annotations or [])
    if show:
        in_range = y_min <= 2020 <= y_max and y_min <= 2025 <= y_max
        has_hyperscale = "Hyperscale (2020+)" in phases

        if in_range and has_hyperscale:
            fig.add_annotation(
                x=2020, y=29,
                text="Hyperscale begins<br><b>+93% YoY</b>",
                showarrow=True, arrowhead=2, arrowsize=1.2, arrowcolor="#0D47A1",
                ax=-70, ay=-50,
                font=dict(size=11, color="#0D47A1"),
                bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
            )

            bracket_y = 200
            for x0, y0, x1, y1 in [
                (2020, 40, 2020, bracket_y),
                (2020, bracket_y, 2025, bracket_y),
                (2025, 182, 2025, bracket_y),
            ]:
                fig.add_shape(
                    type="line", x0=x0, y0=y0, x1=x1, y1=y1,
                    line=dict(color="#0D47A1", width=1.5, dash="dot"),
                )
            fig.add_annotation(
                x=2022.5, y=bracket_y + 8,
                text="2020-2025 CAGR <b>42%</b>",
                showarrow=False, font=dict(size=12, color="#0D47A1"),
                bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
            )

            fig.add_annotation(
                x=2025, y=170,
                text="<b>170 launches</b><br>170\u00d7 the first year",
                showarrow=True, arrowhead=2, arrowsize=1.2, arrowcolor="#0D47A1",
                ax=70, ay=-40,
                font=dict(size=11, color="#0D47A1"),
                bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
            )

    return fig


def save_dashboard_screenshot() -> None:
    """Launch the app in a background thread, screenshot the full page with
    headless Chrome, then shut down the background server."""
    import threading
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By

    # Start Dash in a daemon thread so it doesn't block
    server_thread = threading.Thread(
        target=lambda: app.run(debug=False, use_reloader=False),
        daemon=True,
    )
    server_thread.start()
    time.sleep(2)

    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1400,900")
    driver = webdriver.Chrome(options=opts)

    try:
        driver.get("http://127.0.0.1:8050")
        # Wait for the Plotly chart to render
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "js-plotly-plot"))
        )
        time.sleep(1)

        out = IMAGES_DIR / "app_image_01_default_view.png"
        driver.save_screenshot(str(out))
        print(f"Saved: {out}")
    finally:
        driver.quit()


if __name__ == "__main__":
    save_dashboard_screenshot()
    app.run(debug=True)
