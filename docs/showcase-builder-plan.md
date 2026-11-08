# Showcase page builder plan

Date: 2026-11-08  
POC: AdaL  
TL;DR: Add a direct-only `/showcase/` page that assembles a few existing examples; keep the accepted homepage and navigation unchanged.

## Page outline and source material

Create `website/docs/showcase.md` as a short Markdown page. Use compact section labels and one-line links back to the source tutorials; preserve the original examples and wording wherever practical.

- **Code and data:** Reuse the sample-rows table from [`/learn/data/spacex/`](website/docs/learn/data/spacex.md#sample-rows), rendered from the existing `docs_src/space_dev/modelling/spacex/spacex_launches.csv` via `read_csv`. Add one representative Python snippet with its existing annotation from `docs_src/space_dev/modelling/spacex/spacex.py` and `docs_src/space_dev/modelling/spacex/annotations/spacex.md`; link to the original tutorial for context.
- **SQL and output:** Reuse a short `select(Policy)` example and its SQL/result output from [`/learn/spacex/creating_policies/`](website/docs/learn/spacex/creating_policies.md), sourcing code from `docs_src/space_dev/modelling/tutorial_001.py` or `tutorial_002.py` and annotations from `docs_src/space_dev/modelling/annotations/tutorial_002.md` where useful.
- **Chart treatment:** Show the existing initial and final chart images from [`/learn/spacex/launch_cadence/`](website/docs/learn/spacex/launch_cadence.md), linking back to the walkthrough. Reuse the current assets under `website/docs/assets/images/launch_cadence/` rather than making new images.

Avoid copying whole tutorial sections or adding new product copy. The sandbox page is currently generic placeholder material, so do not present it as a substantive example. The page should inherit the site’s existing theme, shared template, and footer; do not change or refine the homepage.

## Route, risks, and acceptance

- Add `showcase.md` to the existing `not_in_nav` configuration so MkDocs builds `/showcase/` without adding a navigation item. Confirm the generated route is directly reachable and that it remains absent from visible navigation. Check the generated sitemap and search index: being unlisted may not mean undiscoverable or excluded from indexing, so decide whether that is acceptable before release.
- Snippet paths are relative to the configured `website` / `.` bases. Keep includes narrowly scoped, confirm they resolve in the real site build, and avoid duplicating code that would drift from its source. Check image links and the CSV-rendered table in the built page.
- Acceptance: `uv run mkdocs build --strict` succeeds; `/showcase/` is emitted and renders all selected examples, links, chart images, shared footer, and both theme palettes; navigation and homepage output remain unchanged. No tests, app code, or source tutorials need modification.
