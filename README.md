# Analytics by Mark

Practical notes and tutorials on building insurance data models, with and for AI agents. This repo holds the whole site at [analyticsbymark.blog](https://www.analyticsbymark.blog): the blog, the tutorials, and the tested Python code behind them.

| Section | URL | What's there |
|---------|-----|--------------|
| Blog | `/blog/` | Articles on data engineering, analytics and AI agents in insurance |
| Learn | `/learn/` | Hands-on tutorials with runnable Python code (SpaceX launch data as the practice dataset) |
| Newsletter | `/newsletter/` | The Agentic Layer, a weekly email (Mailchimp) |

## Quick start

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync                                   # install dependencies
uv run pytest                             # run every tutorial's tests (45 at time of writing)
uv run mkdocs serve -f website/mkdocs.yml # preview the site at http://127.0.0.1:8000
```

## Write a new blog post

Add **one markdown file** in `website/docs/blog/posts/`:

```markdown
---
date:
  created: 2026-10-10
categories:
  - Actuarial
tags:
  - Pydantic
authors:
  - abm
slug: my-post-slug
---

# Post title

Intro paragraph shown on the blog index.

<!-- more -->

Rest of the post.
```

The newsletter sign-up form, share buttons, RSS feed, tags and LinkedIn card are added automatically.
Allowed categories are listed in `website/mkdocs.yml` under `plugins > blog > categories_allowed`.

## Add a tutorial

1. Create the tested code in `website/docs_src/space_dev/...` with a `tests/` folder beside it.
2. Add a markdown page in `website/docs/learn/` and embed code with `--8<-- "docs_src/path/to/file.py:start:end"`.
3. Add the page to the `Learn` nav in `website/mkdocs.yml`.

## Project layout

```
website/
  mkdocs.yml            # the one site config (nav, plugins, newsletter form, consent)
  docs/                 # pages: index, about, newsletter, cookie-policy
    blog/posts/         # blog posts
    learn/              # tutorials
  docs_src/space_dev/   # tutorial source code + tests
  overrides/            # theme overrides (announce bar, newsletter form partial)
  layouts/              # social card layouts
hooks/                  # MkDocs hook: share buttons on blog posts
tests/                  # shared pytest fixtures
docs/adal/              # planning and review notes
```

## Mailchimp newsletter form

The form is defined once in `website/overrides/partials/newsletter.html` and configured in `website/mkdocs.yml`:

```yaml
extra:
  newsletter:
    action: "https://<your-dc>.list-manage.com/subscribe/post?u=...&id=..."
    honeypot: "b_<u>_<id>"
    placeholder: false
```

While `placeholder: true`, CI will build `develop` (UAT) but refuses to deploy `master` (production).

## Deployment

Push to `develop` (UAT) or `master` (production). GitHub Actions runs the tests, builds the site with `mkdocs build --strict`, and force-pushes the output to `gh-pages-uat` or `gh-pages-prod`. DigitalOcean serves from those branches.

## Parked: A/B testing

Statsig experimentation was removed to keep the site simple. The full implementation is in git tag `archive/statsig-v1`; see `docs/adal/statsig_parked.md`.

## Tech stack

**Site** — [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) 9.7.0, GitHub Actions, DigitalOcean

**Data** — Python 3.11+, pandas, SQLModel, Pydantic, requests; [uv](https://docs.astral.sh/uv/) for dependencies

**Visualisation** — Plotly, Dash, Kaleido (image export)

## License

MIT
