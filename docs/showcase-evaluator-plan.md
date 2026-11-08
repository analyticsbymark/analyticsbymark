# Showcase page: evaluator plan

Date: 2026-11-08 | Role: independent evaluator (planning only, no implementation edits)

TL;DR: one additive, unlisted `/showcase/` page. Pass if it builds strict, nothing else changes, and it truthfully samples the existing redesign with real excerpts. Keep scope to one markdown file plus one `not_in_nav` line.

## Scope and assumptions
- Assumed implementation: `website/docs/showcase.md` (route `/showcase/`), plus `showcase.md` added to the existing `not_in_nav` block in `website/mkdocs.yml` (the same mechanism as `learn/agent_index.md`). The nav list itself stays untouched.
- "Unlisted" means absent from nav, the homepage and any new links. It does not mean hidden from search or the sitemap, and it is not private. Whether to add `search: exclude` or `noindex` is a product decision. Assumption: not required, so flag it rather than fail it.
- "Original content" means excerpts quoted or linked from existing pages (for example `learn/spacex/*`, the blog posts, `about.md`). Excerpts should be copied or transcluded, not paraphrased into new claims.
- Conflict to note: the user asked for a single page, and the redesign edits are still uncommitted in the working tree. The diff must be judged against the pre-showcase state, so record `git status` and the `extra.css` and `mkdocs.yml` hashes before the builder starts.
- Recommended minimal scope: no new CSS, JS, overrides, plugins or nav entries. If the page needs new CSS, that is a finding to justify, not a default.

## Checks (pass/fail)
1. **Strict build**: `mkdocs build --strict -f website/mkdocs.yml` exits 0 with no new warnings, such as broken links or anchors or an unlisted-page notice. `site/showcase/index.html` exists.
2. **Additive diff**: `git diff` against the baseline touches only the new page and the single `not_in_nav` line. `extra.css`, `overrides/`, `index.md`, nav and plugin config are byte-identical. Any other change fails.
3. **Old routes and nav unchanged**: compare the built route list (`find site -name index.html`) before and after, so the only addition is `/showcase/`. The nav HTML is identical on `/`, `/learn/` and `/about/`, with no Showcase link. The homepage has no link to it.
4. **Meaningful sampling**: the page exercises the existing styled components, each with a real excerpt and a link to its source page. The expected set is headings and prose, links, inline and block code (including the code-action buttons), a table, an admonition, tabs, a tag or blog-card, and the newsletter or CTA. Pass if at least five distinct component types are shown and every sample links back to its source. Fail if the samples are lorem ipsum or invented prose.
5. **No invented functionality**: no bespoke widgets, duplicated theme toggles, search, newsletter forms or custom scripts. Only standard Material and Markdown features are used, with existing classes. Check by grepping the page for `<script>`, `<form>`, inline `style=` and new class names.
6. **Theme and mobile (one low-cost check)**: if a browser is available, take one screenshot of `/showcase/` at 390px width in dark (`slate`) mode, and check that there is no horizontal overflow (`document.documentElement.scrollWidth <= innerWidth`). Optionally take one light screenshot. If no browser is available, mark this as unverified rather than inferring it from CSS.
7. **Contrast regression guard (cheap)**: confirm that the code-action buttons on the page still use the already-accepted tokens. Do no new contrast work unless the page adds new colours.

## Reporting
Give a verdict per check, the exact commands run, the diff stat, and the screenshot path or "unverified". Record any assumptions that proved wrong. No full browser matrix and no full route sweep. Checks 1–3 are blocking. Checks 4–5 are blocking for content truthfulness. Check 6 is advisory if there is no browser.
