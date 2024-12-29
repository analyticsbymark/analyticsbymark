import dash_bootstrap_components as dbc


def NavigationButton(text: str, id_: str, disabled: bool = False, **kwargs):
    href = kwargs.get("href")
    return dbc.Button(
        text,
        color="secondary",
        id=id_,
        disabled=disabled,
        href=f"/{href}" if href != "/" else "/",
        style={"border-radius": "20px"},
        class_name="mx-2 col-6 col-md-3",
    )

def BasicButton(text: str, id_: str, **kwargs):
    href = kwargs.get("href")
    return dbc.Button(
        text,
        color="secondary",
        id=id_,
        href=f"/{href}" if href != "/" else "/",
        class_name=kwargs.get("class_name")
    )

def CTAButton(text: str, id_: str, **kwargs):
    href = kwargs.get("href")

    return dbc.Button(
        text,
        color="primary",
        id=id_,
        href=f"/{href}" if href and href != "/" else "/" if href else None,
        class_name=kwargs.get("class_name"),
        disabled=kwargs.get("disabled")

    )


def SingleAnswerButton(text: str, id_: str, **kwargs):
    return dbc.Button(
        text,
        color="secondary",
        id=id_,
        style={"width": "fit-content"},
        **kwargs
    )
