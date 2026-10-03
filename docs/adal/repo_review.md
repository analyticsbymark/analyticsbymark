# Repo Review: Is `analyticsbymark` fit for building an audience?

**Date:** 2026-10-03 | **Branch:** `launch_cadence_with_skills` | **Reviewer:** AdaL

## TL;DR

The engineering is well ahead of the audience work. You have two MkDocs sites, CI with UAT and prod branches, a 20-skill content pipeline and a config-driven experimentation layer. The blog has one lorem-ipsum post, placeholder newsletter URLs, and no consent banner.

| Question | Verdict |
|---|---|
| Is MkDocs fit for purpose? | **Yes for the dev/tutorial site. Adequate but not ideal for the blog.** Material is now in maintenance mode, so plan an exit. |
| Is the `.dev` / `.blog` split a good idea? | **Mostly no, at this stage.** It doubles the maintenance and splits SEO authority before you have any. |
| Is the Statsig implementation good? | **Well built, wrong priority, and currently a compliance liability.** |
| Biggest risk to the goal | Positioning drift and zero published content, not tooling. |

Verified by running the repo:
- Both sites build with `mkdocs build --strict`.
- 30 of 30 tests pass, but only after excluding the untracked `launch_cadence_with_skills/` folder. Otherwise pytest fails at collection on duplicate test basenames.

---

## 1. Is MkDocs (Material) fit for purpose?

### What works
- **The dev site is a good fit.** Code snippets, tabs, annotations, copy buttons and search suit tutorials. `pymdownx.snippets` lets you embed the real tested `.py` files, which keeps the code shown and the code run in sync.
- **Build and deploy are simple.** The site is static, cheap to host and versioned in git. CI builds both sites and publishes to `gh-pages-uat` or `gh-pages-prod`.
- **The blog plugin covers the basics:** categories, tags, authors, archive, RSS (JSON and XML feeds generate) and a sitemap.

### Concerns
1. **Material for MkDocs is in maintenance mode.** 9.7.0 (Nov 2025) was the last feature release. Security and critical fixes are promised to about May 2027 ([issue #8523](https://github.com/squidfunk/mkdocs-material/issues/8523)). The maintainers' successor is Zensical. Your `pyproject.toml` pins the Insiders git repo while `requirements.txt` pins public `9.7.0`, and the README says "Insiders". Reconcile these (see action 9).
2. **MkDocs itself is stagnant.** `mkdocs==1.6.1` is pinned. The 2.0 direction is contentious, so pin and don't upgrade blindly.
3. **MkDocs is weak for audience growth:**
   - No built-in newsletter embed or subscribe form. Every CTA is currently a dead placeholder.
   - No per-post social cards on the blog. The `social` plugin is only enabled on the dev site.
   - Blog ergonomics are thin: no related posts, no reading-progress or series feature, and limited analytics hooks.
   - Build-time performance will degrade as posts and images grow.
4. **Social cards need CairoSVG.** CI installs `libcairo2-dev` on every run, so builds are slower and more fragile than needed.

### Verdict
MkDocs is fine for launch, and the sunk cost is small. Don't migrate now. Do keep content portable: plain Markdown, no heavy Material-only syntax in posts, and front matter you could reuse elsewhere. If the blog starts to feel constraining, the blog is the half to move (to Ghost, Astro or Substack). The tutorials can stay on MkDocs.

---

## 2. Is the `.dev` / `.blog` split a good idea?

### For
- It is a clean separation between the opinion and narrative blog and the reference tutorials.
- Each site can carry its own theme, nav and cadence.
- The dev site's generated `site/` output and heavy assets stay out of the blog build.

### Against (stronger, in my view)
1. **SEO authority is split.** Two root domains means two sets of backlinks. For a new site with no authority, this is the most expensive mistake available. One domain with `/blog` and `/learn` gets all links counting toward one site.
2. **The audience journey is broken.** Your SB7 funnel is read a post, trust Mark, subscribe, then later buy. A reader of a `.blog` post who wants the code must cross to another domain, and the cookie banner, analytics, Statsig user ID and nav all reset.
3. **Everything is duplicated.** The `js/statsig/` tree, `extra.css`, theme config, analytics override and consent config are copy-pasted into both sites. They have already drifted: the blog has extra docs, a `utils/` folder and a different nav. CI has to build and ship both.
4. **The dev site is thin.** It has 5 tutorial pages, and `creating_policies.md` is 169 lines of the 359 total. That is a sub-section, not a site.
5. **The messaging already overlaps.** `dev/index.md` repeats the About, "Is this for you?" and the same subscribe pitch that the blog homepage has.
6. **The dev index points to a dead link.** Its subscribe button is `href="#"`.

### Recommendation
Merge into one site now:
- `analyticsbymark.blog` (or a single primary domain) with `/blog/` for posts and `/learn/` (or `/tutorials/`) for the code series.
- Point `.dev` at the new URLs (GitHub Pages can't do true 301s, so use a DNS or registrar redirect), or drop it.
- One `mkdocs.yml`, one `js/` tree, one consent setup, one build.
- Use the nav for the split: `Blog | Tutorials | About | Newsletter`.

If you want to keep two sites for brand reasons, extract the shared parts (`overrides/`, `assets/`, `js/statsig/`) into a single shared folder and symlink or copy them at build time. You already have `hooks/` and `ext/` at the root, so the pattern exists. Don't maintain two copies by hand.

---

## 3. Statsig implementation

### What's good
- **The architecture is tidy.** It is modular (`core/`, `experiments/`, `tracking/`) and config-driven, with selector-to-experiment bindings. There is a client singleton, and cache-first `initializeSync` avoids flicker.
- **It handles Material's instant navigation** by hooking `document$`.
- **Testing is easy** through `?exp_...=value` URL overrides.
- **Exposure logging exists**, which is needed for valid analysis.
- **Secrets handling is sensible.** The real `experiments.config.js` is gitignored and injected from GitHub Secrets in CI. The client key is designed to be public.

### Problems
1. **It is far more than a tiny blog needs.** About 1,300 lines of JS across 9 modules, plus `IMPLEMENTATION_PLAN.md`, `QUICK_START.md`, `HOW_TO_ADD_EXPERIMENTS.md` and `EXPERIMENT_MAPPING.md`, for a config containing **one** active experiment (hero CTA text). A/B testing needs traffic, and a new blog with hundreds of visitors a month cannot reach significance on a CTA-click test for months, if ever.
2. **Consent is not respected (compliance risk, UK/EU audience).**
   - `analytics.html` in `overrides/` loads the Statsig SDK unconditionally.
   - `user.js` writes a persistent UUID to `localStorage` on first load, and the SDK sends events, with no check of `__consent`.
   - Your own cookie policy lists only Google Analytics and Mailchimp. Statsig is undisclosed.
   - Under PECR/UK GDPR a persistent identifier for experimentation generally needs consent or an explicit disclosure.
3. **The consent banner and Google Analytics are broken in the built sites.** I built both sites and checked:
   - Your `overrides/partials/integrations/analytics.html` **replaces** Material's partial. Material's version loads Google Analytics and gates it on consent. Your override only loads Statsig. The `G-QGKGYMC3V5` tag is **absent** from both built pages.
   - On the blog, `consent:` sits under `extra.analytics.consent`. Material reads `extra.consent` at the top level. The built blog page has **no consent banner at all**, while `cookie-policy.md` says there is one and offers a "reset" button for a `__consent` value that is never set.
   - `eventLogger.js` and `exposureLogger.js` call `gtag`, which doesn't exist. They silently no-op.
   - So you currently have no working web analytics (no GA), while Statsig runs without consent.
4. **Hardcoded fallback client key.** `bootstrap.js` contains a `DEFAULT_CLIENT_KEY` that is also in the template. The key is public, so this is safe, but it means a missing config silently runs against a real project. Fail closed instead.
5. **The "obfuscation" is theatre.** Experiment names are obfuscated, but the shipped config exposes selectors, parameters and the project key. A visitor can still see the exact test. It's harmless, but the private mapping file doesn't protect anything of value.
6. **The build never fails on missing config.** If the GitHub secret is unset, CI writes no file, `mkdocs build` still passes, and the browser gets a 404 for the script. Validation is duplicated in two places (inline in `build.yml` and in `scripts/experiments/validate-config.mjs`), so they can drift.
7. **Feature-flag layer unused.** `featureFlags: {}` is reserved and there is a lot of defensive code for cases that don't exist yet.
8. **Scripts are not bundled or minified.** There are 11 separate script requests per page, 9 of them yours, and they run after the SDK.

### Recommendation
- **Short term:** gate Statsig behind consent (or switch it off), add it to the cookie policy, and fix the analytics override so GA loads.
- **Medium term:** park experimentation until you have about 1,000+ weekly visitors. Until then, the newsletter conversion rate is the only metric that matters, and you can read it directly from your email tool.
- **Simpler alternative for now:** keep one Statsig-free site, use GA or Plausible plus UTM links to compare CTAs, and ship a single config-free "hero CTA" variant.
- If you keep it, collapse `tracking/` into fewer files and build once into a single JS file.

---

## 4. Suitability for "a blog about actuarial data modelling"

### Positioning drift (the biggest issue)
There are **three different value propositions** in the repo:

| Where | What it promises |
|---|---|
| `claude.md` | Data **visualisation** tutorials (Kirk's framework) using neutral datasets like SpaceX |
| `dev/index.md` | Insurance **data foundations**: APIs, Pydantic, SQLModel, Plotly |
| `blog/index.md`, `about.md`, `newsletter.md` | **"The Agentic Layer"**: AI agents in insurance, data models for agents |

Your stated goal is actuarial data modelling. None of the content yet teaches **actuarial** data modelling: there is no triangle, exposure, claims or policy table. The SpaceX series teaches charting, and its link to an insurer's day-to-day problems is left for the reader to make. The one post (`actuaries-are-data-engineers`) is a 3-sentence intro plus lorem ipsum, and its front matter says `updated: 2025-08-29`, so it looks abandoned.

`claude.md` justifies neutral datasets ("removes methodology arguments"). That is reasonable for teaching the mechanics, but as the **only** content it means you're competing with every Plotly tutorial on the web and giving actuaries no reason to pick you. Your real edge (qualified actuary, 100+ classes, $5bn+ GWP, data model builder) only appears on the About page.

### Launch blockers (visible to any reader)
- Newsletter CTA URLs are all placeholders: `https://YOUR-NEWSLETTER-URL`, `YOUR-MAILCHIMP-URL`, `YOUR-NEWSLETTER-SIGNUP-URL-HERE`. Appears on home, about, newsletter, the announce bar and every post footer.
- The announce bar in `overrides/main.html` advertises a "Free Claude Code Course" that doesn't exist, and it conflicts with the rest of the positioning.
- The dev subscribe button is `href="#"`.
- The same `id="hero-cta"` is used three times on the blog (home, about, newsletter), which is invalid HTML and makes the Statsig selector `#hero-cta` ambiguous. It only ever targets the first match.
- `blog/posts/drafts/.meta.yml` is fine, but there's no evidence of a draft pipeline being used.
- The blog's `categories_allowed` are "Data Engineering, Analytics, APIs". None of these says "actuarial" or "insurance", so posts about reserving or pricing data models cannot be categorised.
- No SEO basics beyond defaults: no per-page descriptions, no OpenGraph image for the blog (the social plugin is dev-only), no `robots.txt`, and the `description` is first-person ("My journey...").

### Content positives
- The SB7 BrandScript is clear and the About story is credible.
- The code quality is high. Tutorials are independently runnable, tested with pytest, and have a consistent structure.
- The audience definition is sharp (people with messy inherited data and reporting pain).
- The weekly newsletter and "build in public" angle fits the brand.

---

## 5. Repo hygiene and workflow

| Finding | Impact | Note |
|---|---|---|
| **`claude.md` has drifted from reality** | Agents will create files in the wrong places | It describes `docs/`, `docs_src/weather_data/`, `sports_data/`, `mission_types/`, `success_rates/`, 5-file image standards and `.claude/skills/` with 20 skills. In the repo: there is no root `docs/`, the sites live in `projects/blog` and `projects/dev`, there is no weather or sports data, and `.claude/` is not tracked. The real series are `launch_cadence`, `launch_reliability` and `customer_concentration`. |
| **`.claude/` and skills are gitignored** | The content pipeline is not versioned, so you can't recover or share it | The commit "gitignore .claude skills (private IP)" is a valid choice, but back it up somewhere private. |
| **Duplicate test basenames** | `pytest projects/` fails at collection | `launch_cadence_with_skills/` is a copy of `launch_cadence/` with the same `test_launch_cadence.py` name. Fix by renaming, adding `__init__.py`, or using `--import-mode=importlib`. CI will fail on the next push if that folder is committed. |
| **Untracked build output** | Noise | `projects/dev/site/` is not gitignored. |
| **Scratch docs at root and in `projects/dev/`** | Clutter | `claude_md_plan.md`, `claude_md_changes.md`, `EXPERIMENT_MAPPING.md`, `suggested_changes*.md`. One of them says "add to `.gitignore` before open sourcing". |
| **Binary blobs committed** | Clone size (`.git` is 35 MB) | Two `database.db` files, two JSON captures and two CSV copies of the same SpaceX data. The repo is public under MIT. |
| **Generated images live in two places** | Drift | `docs_src/.../images/` and `docs/assets/images/`. A build step should copy them. |
| **Dependencies are declared twice** | Confusing, hard to reproduce | `pyproject.toml` (with uv) and a `uv export`ed `requirements.txt`. CI uses pip. Pick uv end to end (`uv sync --frozen`). |
| **CI** | OK but basic | Single job, apt install every run, no caching of built sites, a 60-line inline Node script. No link check. `--strict` isn't used in CI. Deploys via a force-push to an orphan branch, which works but drops history and is non-atomic for two sites. |
| **Tests only check that code runs** | Weak signal | They validate the tutorials, which is good. No content tests (links, placeholders, front matter). |

---

## 6. Strengths worth keeping

- The **progressive tutorial structure** (brief, then 001 to 004, then final, then a Dash app) is a strong teaching format.
- **Tests on tutorials** mean copy-paste code works.
- **AGENT_SUMMARY.md and AGENT_INDEX.md** for AI discoverability are forward-thinking.
- **UAT and prod branches** in the deploy pipeline are more rigorous than most solo blogs.
- **Separation of code from prose** keeps your voice yours.

---

## 7. Prioritised action list

**This week (unblocks launch)**
1. **Fix the newsletter URL** in all five places and remove or replace the "Free Claude Code Course" announce bar.
2. **Fix the analytics override** so Material's GA partial is kept (`{{ super() }}` in a block override, or include the original), and move `consent:` to the top level of `extra:`.
3. **Gate Statsig behind consent**, or disable it, and mention it in the cookie policy.
4. **Rename or merge `launch_cadence_with_skills`** so CI doesn't break. Gitignore `projects/dev/site/`.
5. **Publish one real post** and delete or finish the lorem-ipsum post.

**Next 2 to 4 weeks**
6. **Decide the positioning in one sentence** and rewrite `claude.md`, the home page and the nav to match. Suggested: "Build insurance data models your team can trust", with the Agentic Layer as the newsletter name only.
7. **Consolidate to one site** with `/blog` and `/learn`, 301-redirect the second domain, and share one `js/` tree.
8. **Add an actuarial tutorial series** (for example, a claims triangle or exposure table modelled in SQLModel, then analysed and charted). Keep SpaceX as the "mechanics" track.
9. **Choose one dependency path** (uv), and replace the `pyproject` Insiders pin with public `mkdocs-material==9.7.0`.
10. **Add blog social cards and page descriptions** so LinkedIn shares look good. LinkedIn is your main distribution channel.

**Later (after you have traffic)**
11. Revisit A/B testing once you have about 1,000+ weekly visitors, and start with a single hypothesis.
12. Evaluate Zensical or a different blog engine before mid-2027.
13. Add CI checks for placeholders (`grep YOUR-`), broken links and `mkdocs build --strict`.

---

## Bottom line

The tooling is credible and the code tutorials are good, but you have more infrastructure than content and more experiments than visitors. The most valuable change is to stop optimising the system and publish actuarial-specific posts on one domain, with a working subscribe link and a working consent banner.
