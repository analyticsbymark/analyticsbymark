from pathlib import Path
from PIL import Image
from dash import html
import dash_bootstrap_components as dbc


PATH = Path(__file__).parent
ASSET_FOLDER = PATH.joinpath("../../assets")
LOGO_PATH = ASSET_FOLDER.joinpath("aby_logo.png").resolve()
logo = Image.open(LOGO_PATH)


class NavBar:
    color_mode_switch = html.Span(
        [
            dbc.Label(className="fa fa-moon", html_for="switch"),
            dbc.Switch(
                id="switch",
                value=True,
                className="d-inline-block ms-1",
                persistence=True,
            ),
            dbc.Label(className="fa fa-sun", html_for="switch"),
        ]
    )

    def create_navbar(
        self, user_status_text: str = "Login", user_status_href: str = "/login"
    ):
        navbar = dbc.Navbar(
            dbc.Container(
                [
                    dbc.NavbarBrand("CompareActuarialSalaries"),
                    dbc.NavbarToggler(
                        id="navbar-menu-button",
                        className="mb-2",
                        n_clicks=0,
                    ),
                    dbc.Popover(
                        children=[
                            dbc.DropdownMenuItem("Dashboard", href="/"),
                            dbc.DropdownMenuItem("Items", href="/items"),
                            dbc.DropdownMenuItem(divider=True),
                            dbc.DropdownMenuItem("User Settings", href="/settings"),
                            dbc.DropdownMenuItem("Admin", href="/admin"),
                            dbc.DropdownMenuItem(
                                user_status_text, href=user_status_href
                            ),
                        ],
                        id="navbar-menu-popover",
                        target="navbar-menu-button",
                        trigger="hover",
                        placement="bottom",
                        is_open=False,
                        hide_arrow=True,
                        style={"padding": "1rem"},
                    ),
                ]
            ),
            className="mb-5 mx-2",
            sticky="top",
            expand="all",
            class_name="dbc",
        )

        return navbar

    def create_offcanvas(self, menu: dbc.ListGroup = None):
        navbar = dbc.Navbar(
            dbc.Container(
                [
                    dbc.NavbarToggler(
                        id="navbar-menu-button",
                        className="mb-2",
                        n_clicks=0,
                    ),
                    # dbc.NavbarBrand("CompareActuarialSalaries"),
                    self.color_mode_switch,
                    dbc.Offcanvas(
                        [
                            html.Img(
                                src=logo,
                                width=50,
                                height=50,
                                style={"padding-bottom": "1rem"},
                            ),
                            menu,
                        ],
                        id="offcanvas",
                        is_open=False,
                        style={"max-width": "50%"},
                    ),
                ]
            ),
            expand="all",
            color="primary",
            sticky="top",
            id="navbar",
        )

        return navbar


navbar = NavBar()
