import dash
from dash import html
import dash_bootstrap_components as dbc


dash.register_page(__name__, path="/settings", order=3)

layout = dbc.Container(
    [
        html.H1("This is my user settings page"),
    ],
)
