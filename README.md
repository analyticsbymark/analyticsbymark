# Analytics by Mark

I build datasets and design data visualizations that turn raw API data into clear, actionable analytics. This repo contains everything behind my two sites — articles, tutorials, and the full source code you can run yourself.

| Site | What's there |
|------|-------------|
| [analyticsbymark.blog](https://www.analyticsbymark.blog) | Articles on data engineering, analytics, and APIs in insurance |
| [analyticsbymark.dev](https://www.analyticsbymark.dev) | Hands-on tutorials with runnable Python code and interactive dashboards |

## What you'll find here

The dev site tutorials follow a progressive structure, currently built around SpaceX launch data from the [Launch Library 2 API](https://thespacedevs.com/llapi):

- **Data pipelines** — Fetch from a REST API, validate with SQLModel, cache to CSV, persist to SQLite (`docs_src/space_dev/modelling/`)
- **Data profiling** — Explore and understand a dataset before visualizing it
- **Visualization series** — Chart selection, color design, annotation, and final composition using Plotly, following Andy Kirk's data visualization framework
- **Interactive dashboards** — Dash apps for exploring launch data

Each tutorial is a standalone Python script you can run independently.

## Quick start

Requires Python 3.11+.

```bash
# Install dependencies
pip install uv
uv sync

# Run a tutorial (no API key needed)
python projects/dev/docs_src/space_dev/modelling/spacex/spacex.py

# Serve a site locally
mkdocs serve -f projects/dev/mkdocs.yml
```

## Project layout

```
projects/
  blog/                     # Blog site (MkDocs Material)
  dev/                      # Dev site (MkDocs Material)
    docs_src/space_dev/     # Tutorial source code
      modelling/spacex/     # Data fetch + SQLModel persistence
      spacex/               # Launch visualizations and Dash apps
        data/               # Cached datasets (CSV)
        launch_cadence/     # Tutorial series: SpaceX launch frequency
        launch_reliability/ # Tutorial series: success/failure analysis
        customer_concentration/ # Tutorial series: mission customer mix
hooks/                      # Shared MkDocs hooks (social media footers)
tests/                      # pytest suite for all tutorials
```

## Tech stack

**Sites** — [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) (Insiders), deployed via GitHub Actions

**Data** — Python, pandas, SQLModel, Pydantic, requests

**Visualization** — Plotly, Dash, Kaleido (image export)

**CI/CD** — GitHub Actions builds both sites on push to `develop` (staging) and `master` (production)

## License

MIT
