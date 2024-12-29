import dash
from dash import html
import dash_bootstrap_components as dbc
from app.components.utils import id_factory

page_id = id_factory("login")

dash.register_page(__name__, path="/login")

email_input = dbc.Row(
    [
        dbc.Label("Email", html_for=page_id("email-input")),
        dbc.Input(
            id=page_id("email-input"),
            placeholder="Enter Email...",
            valid=True,
            type="email",
            name="username",
        ),
    ],
    className="mb-3",
)

password_input = dbc.Row(
    [
        dbc.Label("Password", html_for=page_id("password-input")),
        dbc.Input(
            id=page_id("password-input"),
            placeholder="Enter Password...",
            type="password",
            name="password",
        ),
    ],
    className="mb-3",
)


def layout(**kwargs):
    return dbc.Container(
        [
            email_input,
            password_input,
            dbc.Button("Login", n_clicks=0, id=page_id("login-button"), type="submit"),
            html.P("", id=page_id("email-validator")),
        ],
    )
