import dash
from dash import html, dcc

dash.register_page(__name__)


def layout(**kwargs):
    return html.Div(
        [
            html.Div(
                html.H2("You have been logged out - You will be redirected to login")
            ),
            dcc.Interval(
                id={"index": "redirectLogin", "type": "redirect"},
                n_intervals=0,
                interval=1 * 3000,
            ),
        ]
    )
