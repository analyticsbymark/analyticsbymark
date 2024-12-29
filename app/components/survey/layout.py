from typing import Callable
import dash
from dash import html
import dash_bootstrap_components as dbc

from app.components.common.button import NavigationButton


def footer_next(
    page_id: Callable, next_page: str, next_disabled: bool = True, **kwargs
):
    return [
        html.Div(
            NavigationButton(
                text="Next", id_=page_id("next"), href=next_page, disabled=next_disabled
            ),
            className="d-flex justify-content-center",
        )
    ]


def footer_back(page_id: Callable, back_page: str, **kwargs):
    return [
        html.Div(
            NavigationButton(text="Back", id_=page_id("back"), href=back_page),
            className="d-flex justify-content-center",
        )
    ]

def footer_next_back(
    page_id: Callable,
    next_page: str,
    back_page: str,
    next_disabled: bool = True,
    **kwargs,
):
    return [
        html.Div(
            [
                NavigationButton(
                    text="Back", id_=page_id("back"), href=back_page, class_name="me-5"
                ),
                NavigationButton(
                    text="Next",
                    id_=page_id("next"),
                    href=next_page,
                    disabled=next_disabled,
                ),
            ],
            className="d-flex justify-content-center",
        )
    ]

def footer_basic_sign_up(
    page_id: Callable,
    next_page: str,
    back_page: str,
    next_disabled: bool = False,
    **kwargs,
):
    return [
        html.Div(
            [
                NavigationButton(
                    text="Back", id_=page_id("back"), href=back_page, class_name="me-5"
                ),
                NavigationButton(
                    text="Continue",
                    id_=page_id("next"),
                    href=next_page,
                    disabled=next_disabled,
                ),
            ],
            className="d-flex justify-content-center",
        )
    ]


def create_question(
    page_id: Callable,
    title: str = "",
    question: str = "",
    additional_text: str = "",
    progress_value: int = 0,
    options: list = list(),
    show_footer: bool = True,
    footer_value: list | None = None,
    **kwargs,
):
    title = html.H1(title, className="display-4", id=page_id("title"))
    question = html.H2(question, id=page_id("question"))
    additional_text = html.P(additional_text, id=page_id("additional-text"))
    show_footer = (
        html.Div(footer_value, className="p-3 mx-2 fixed-bottom bg-primary")
        if show_footer
        else None
    )

    children = [title, question, html.Hr(className="my-2"), additional_text] + [
        x for x in options
    ]

    return [
        dbc.Container(
            [
                dbc.Progress(
                    id='progress-bar',
                    value=progress_value,
                    # label=f"{str(progress_value)}%",
                    color="info",
                    className="mb-3",
                    style={"border-radius": "0px"},
                ),
                html.Div(
                    dbc.Container(children, fluid=True, className="py-3"),
                    className="p-3 bg-body-secondary rounded-3 text-center",
                ),
                show_footer,
            ], class_name='m-0 p-0 mx-sm-auto px-sm-auto'
        )
    ]
