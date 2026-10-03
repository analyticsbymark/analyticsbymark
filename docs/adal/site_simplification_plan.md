# Plan: One simple site (`/blog` + `/learn`), built for newsletter sign-ups

**Date:** 2026-10-03 | **Branch:** `project_restructure_with_adal` | **POC:** Mark / AdaL
**Based on:** `docs/adal/repo_review.md` | **Status:** DRAFT, awaiting approval

## TL;DR

Merge `projects/blog` and `projects/dev` into one MkDocs site at `website/`. Blog posts live at `/blog/`, the SpaceX tutorials at `/learn/`. Every page points to one Mailchimp sign-up form. Statsig comes out of the build but stays in git history under a tag. All tests move with their code and run from one command, including the new `launch_cadence_with_skills` tests.

Design rule: **adding a post means adding one markdown file. Nothing else.**

## Decisions already made

| # | Decision |
|---|---|
| 1 | One domain, `/blog` + `/learn`, optimised for newsletter sign-up |
| 2 | Park Statsig: remove from the build, keep in git history behind a tag |
| 3 | Newsletter tool is Mailchimp |
| 4 | SpaceX tutorials move under `/learn/` |
| 5 | All pytest suites move over and run green |

## Open questions (need an answer before step 1 / step 6)

1. **Which domain is primary?** `analyticsbymark.blog` or `analyticsbymark.dev`. Default in this plan: `.blog`, with `.dev` redirecting to it.
2. **Mailchimp embed code.** Paste the "Embedded form" HTML (or just the `action="https://…list-manage.com/subscribe/post?u=…&id=…"` URL). Needed for step 4.
3. **How are the two domains routed today?** CI pushes both sites into one `gh-pages-*` branch as sub-folders. I need to know where the domain mapping happens (DNS, Cloudflare, Pages `CNAME`). Needed for step 6.

## Target layout

```
analyticsbymark/
├── website/                      # the whole site
│   ├── mkdocs.yml                # ONE config
│   ├── docs/
│   │   ├── index.md              # home: promise + sign-up form + latest posts
│   │   ├── about.md
│   │   ├── newsletter.md         # dedicated sign-up page
│   │   ├── cookie-policy.md
│   │   ├── blog/                 # (was projects/blog/docs/blog)
│   │   │   └── posts/
│   │   └── learn/                # (was projects/dev/docs/tutorial)
│   │       ├── index.md
│   │       ├── data/
│   │       └── spacex/
│   ├── docs_src/                 # tested tutorial code (moved as-is, history kept)
│   │   └── space_dev/spacex/{launch_cadence, launch_cadence_with_skills,
│   │                         launch_reliability, customer_concentration, data}
│   └── overrides/                # main.html, newsletter partial, analytics partial
├── hooks/  ext/                  # unchanged
├── tests/                        # repo-level fixtures (paths updated)
├── pyproject.toml  uv.lock       # single dependency source
└── .github/workflows/build.yml   # one job, one site
```

`docs_src/` keeps its internal structure, so the 25 `--8<--` snippet references and the tests' file-relative paths keep working. Only the snippet `base_path` and a couple of fixtures change.

## Steps

Each step is one commit. After each one, the gate must pass before moving on.

### Step 0. Safety net
- Tag the current state so nothing is lost: `git tag archive/pre-restructure-2026-10-03` and `git tag archive/statsig-v1` (both at `744ce46`). Push the tags.
- Record the baseline: `.venv/bin/python -m pytest projects/ -q`. Currently 30 passing, excluding the `_with_skills` folder.
- **Gate:** tags exist on origin.

### Step 1. Move the files (no content edits)
- `git mv projects/dev/docs_src → website/docs_src`
- `git mv projects/dev/docs/tutorial → website/docs/learn`
- `git mv projects/blog/docs/* → website/docs/` and `projects/blog/overrides → website/overrides`
- `git mv projects/blog/mkdocs.yml → website/mkdocs.yml` (the blog config is the base, as it already has the blog, tags and RSS plugins)
- `git mv projects/dev/docs/virtual_environments.md → website/docs/learn/`
- **Gate:** `git status` shows renames only. Nothing builds yet, which is fine.

### Step 2. One `mkdocs.yml`
- Set `site_url` to the primary domain.
- Nav: `Home | Blog | Learn | About | Newsletter`.
- `Learn` nav takes over the dev site's tree (Data, SpaceX).
- Pull in the dev config's `social` plugin, `table-reader` plugin and layouts (`projects/dev/layouts/` → `website/layouts/`). This gives blog posts LinkedIn cards too.
- Snippets `base_path: website`.
- Update internal links that used the old `tutorial/` paths to `learn/`.
- **Gate:** `mkdocs build --strict -f website/mkdocs.yml` passes locally.

### Step 3. Park Statsig
- Delete the `js/statsig/` trees, the Statsig loader in `overrides/partials/integrations/analytics.html`, `scripts/experiments/`, `projects/blog/scripts/`, `EXPERIMENT_MAPPING.md`, the Statsig-related docs, and the "Write experiment configs" CI step.
- Add `docs/adal/statsig_parked.md`: what it was, which tag holds it (`archive/statsig-v1`), and how to restore it (`git checkout archive/statsig-v1 -- <paths>`).
- Remove the `EXPERIMENT_CONFIG_JSON_*` GitHub secrets after the merge (manual step for you).
- **Gate:** `grep -ri statsig website/ .github/` returns nothing, and the strict build still passes.

### Step 4. Newsletter-first pages (Mailchimp)
- Add one partial, `overrides/partials/newsletter.html`, containing the Mailchimp embedded form. The form URL lives once in `mkdocs.yml` as `extra.newsletter_action`, so changing it is a one-line edit.
- Show the partial in four places, all from the same file:
  1. Home page hero (one `id="hero-cta"`, not three)
  2. Bottom of **every blog post** (via `overrides/partials/content.html`)
  3. Bottom of every `/learn/` page
  4. The `/newsletter/` page
- Replace the announce bar ("Free Claude Code Course" is gone) with a one-line newsletter prompt.
- Delete every `YOUR-NEWSLETTER-URL` / `YOUR-MAILCHIMP-URL` placeholder.
- Home page: one sentence of positioning, one form, latest three posts, one line pointing to `/learn/`.
- **Gate:** `grep -r "YOUR-" website/` is empty, and a built page shows the form (I'll check with a real browser render).

### Step 5. Analytics and consent that work
- Restore Material's own Google Analytics partial and consent gating. Set `consent:` at the top level of `extra:`.
- Mailchimp listed as a cookie category in `cookie-policy.md`. Statsig removed from the policy.
- **Gate:** built HTML contains the GA tag and the consent banner. No script loads before consent.

### Step 6. Tests move over and run
- `git mv` already took every `tests/` folder with its tutorial. Update:
  - `tests/conftest.py`: `docs_src` fixture → `website/docs_src`.
  - `pyproject.toml`: `testpaths = ["website/docs_src", "tests"]`, plus `--import-mode=importlib`.
  - Rename `launch_cadence_with_skills/tests/test_launch_cadence.py` → `test_launch_cadence_with_skills.py` to fix the duplicate basename that breaks collection.
- Risk to check: several tutorial folders contain `app.py` and use `from app import app`. If a shared module name causes a clash, run each tutorial folder as its own pytest invocation (a small loop in CI) or rename the modules. I'll find out in this step.
- **Gate (hard requirement):** `uv run pytest` passes **all 30 existing tests plus every test in `launch_cadence_with_skills`**, from the repo root. The pass count is recorded in the commit message.

### Step 7. Simplify CI and dependencies
- `build.yml`: one job that installs with `uv sync --frozen`, runs `pytest`, runs `mkdocs build --strict`, then deploys the single site to the root of `gh-pages-uat` (on `develop`) or `gh-pages-prod` (on `master`). It also adds a `CNAME` file for the primary domain and a placeholder check (`grep -r "YOUR-"`).
- `pyproject.toml`: swap the Insiders git pin for public `mkdocs-material==9.7.0`. Delete `requirements.txt`.
- **Gate:** the PR check is green on GitHub.

### Step 8. Redirect, cleanup, docs
- Second domain redirects to the primary (Mailchimp and LinkedIn links stay valid). Mechanism depends on open question 3.
- Delete `projects/`, root scratch files (`claude_md_plan.md`, `claude_md_changes.md`, `suggested_changes*.md`), and gitignore `site/` and `_build/`.
- Rewrite `README.md` and `claude.md` to match the new layout and the "add a post" workflow.
- Delete or finish the lorem-ipsum post.
- **Gate:** fresh clone → `uv sync` → `uv run pytest` → `uv run mkdocs serve -f website/mkdocs.yml` works from the README alone.

## Definition of done

- [ ] One site, one `mkdocs.yml`, one build, one deploy.
- [ ] `/blog/` and `/learn/` both live, with all SpaceX tutorials under `/learn/`.
- [ ] Mailchimp form on home, every post, every tutorial page and `/newsletter/`.
- [ ] Statsig gone from the tree and recoverable from tag `archive/statsig-v1`.
- [ ] All existing tests plus the `_with_skills` tests pass with one `pytest` command locally and in CI.
- [ ] `mkdocs build --strict` passes. No `YOUR-` placeholders. GA and consent banner present in the built output.
- [ ] New post workflow = one markdown file in `website/docs/blog/posts/`.

## Not in this plan (deliberately)

- Writing actuarial content or settling the positioning sentence (next step, after the structure is clean).
- A/B testing, which returns once traffic justifies it.
- Moving off Material or MkDocs (revisit before mid-2027).

## Risks

| Risk | Mitigation |
|---|---|
| Old URLs break (`.dev/tutorial/...`) | Only a few pages exist and there's no traffic yet. Add MkDocs redirects for the five tutorial pages. |
| Snippet paths break after the move | `docs_src/` keeps its layout. The strict build catches missing files. Turn `check_paths` back on. |
| Test module-name clashes | Importlib mode, the renamed test file, and a per-folder run as the fallback (step 6). |
| Domain routing surprises | Open question 3, answered before step 7. |
