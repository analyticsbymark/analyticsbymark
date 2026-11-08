# Redesign builder plan: Analytics By Mark

Date: 2026-11-07 (rev 2, after evaluator plan and lead decisions) · POC: visual-builder (AdaL, session b5ba2d33) · Branch: `re-brand` · Status: **planning, awaiting contract gate, no code written**

**TL;DR.** The site already uses turbopuffer's type scale (JetBrains Mono, 30/36/800 H1), so typography changes little. The work is structure, contrast, surfaces and four real defects. The direction is "Ledger":

- A deep-forest band carries the header and tabs. On the home page only, a decorative band sits above the content.
- Pages are flat paper in light mode and near-black green in dark mode, with square edges and a hatched green offset shadow.
- The wow factor is a one-shot 1.2 s trace of a box-drawn lineage diagram in that home band, plus the hatched shadow. Both are geometry only, with no new words.

All navigation stays, including the home sidebar and TOC, and no Markdown, nav or URL changes. The code changes are one CSS file rewritten, one template edited, a few static assets added, and theme-only lines in `mkdocs.yml`. Preview: **http://127.0.0.1:8010** (unchanged).

Lead decisions applied: approved the Ledger palette, all-mono type, self-hosted fonts and a small SVG logo. The homepage TOC and sidebar are kept. The hero is full width above the content with no duplicate H1 or copy. The diagram has no labels and no looping packet. The view transition is optional and must not intercept Material's controls.

This file is in the repo-root `docs/`. MkDocs reads `website/docs`, so this file is never published and needs no `exclude_docs` entry.

## 1. What I inspected

| Area | Finding |
|---|---|
| Git | `re-brand` at `4a892b5`. Untracked: this file and the evaluator's `docs/redesign-evaluator-plan.md` (not mine, untouched). |
| Build | `uv run mkdocs build --strict` exit 0. Existing INFO notes: `#newsletter` (the anchor exists in the footer partial at render time), `#start`, three `agent_index` relative links. CI runs `uv run pytest -v`, then the strict build. |
| Stack | `mkdocs~=1.6`, `mkdocs-material==9.7.0` pinned. Plugins: search, table-reader, social (`website/layouts/*.yml`), blog, meta, tags, rss. Hook `hooks/socialmedia.py` adds share buttons to blog posts. |
| Theme | `custom_dir: overrides`, `font: false`, Google Fonts `@import` in `extra.css`. Two palette entries with a toggle and no `primary`/`accent`, so Material indigo `#526cfe` leaks into dark mode. |
| Overrides | `overrides/main.html` holds the announce bar and the newsletter in the `footer` block. `overrides/partials/newsletter.html` holds the form. |
| Template slots | In Material 9.7.0 `base.html`, `{% block hero %}` sits inside `.md-container`, before `<main class="md-main">`. Because `navigation.tabs.sticky` is on, the tabs render inside the header partial, so the hero lands below header and tabs and above the sidebar/content grid. That is full width and outside the article. |
| Line endings | `mkdocs.yml`, `main.html`, `newsletter.html` and `extra.css` are CRLF. Edits keep CRLF. |

### Browser tooling: repair status

- **Installed:** Node v22.23.4 at `/home/cooperm/.adal/engineer/tooling/node22` (a symlink to `node-v22.23.4-linux-x64`). The official tarball was checked against nodejs.org `SHASUMS256.txt` (OK).
- **Not changed:** PATH, nvm, shell rc files, the repo and `.venv`. The nvm default is still `18` and `node -v` is still `v18.20.2`.
- **Proven:** isolated Node 22 with AdaL's bundled `playwright-core` connects to the shared browser over CDP and loads `http://127.0.0.1:8010/` (HTTP 200, title "Analytics By Mark"). It opens and closes only its own tab. The shared browser had stopped answering on 9222 with no process left, so I relaunched it detached with the shared profile, as the browser-use instructions say.
- **Still blocked:** the browser-use tools in *this* worker. The AdaL backend picks its Node at attach time from `ADAL_ELECTRON_NODE` first, then `node` on PATH. Its PATH was fixed when the worker started (`.venv/bin`, `~/.local/bin`, `~/.adal/bin`, then nvm 18). A retry after the install still reports Node 18.20.2.
- **Fix without a default change (lead action):** relaunch the builder worker, and the evaluator's if it wants browser-use too, with `ADAL_ELECTRON_NODE=/home/cooperm/.adal/engineer/tooling/node22/bin/node` in its environment. The backend also sets `ELECTRON_RUN_AS_NODE=1`, which plain Node ignores. I won't put a `node` shim on any PATH directory, because every entry ahead of nvm is either global (`~/.local/bin`, `~/.adal/bin`) or inside the repo (`.venv/bin`).
- **Until then:** I can drive the same browser with Node 22 and playwright-core scripts kept outside the repo, one action per call. I'll label that evidence "Playwright via isolated Node 22", not browser-use.

## 2. Before metrics (2026-11-07, 1440×900 and 390×844, light and dark)

These come from the Selenium/headless Chrome 126 fallback: 68 PNGs and `metrics.json` in `~/.adal/sessions/b5ba2d33-a649-4acf-912f-a8c61dc2d071/scratch/before/`. The baseline build is in `/tmp/abm-before`. The evaluator keeps its own immutable baseline, and these files are only my working reference.

| Metric | Current | turbopuffer.com |
|---|---|---|
| Font | JetBrains Mono via Google Fonts | JetBrains Mono, self-hosted |
| H1 | 30 / 800 / 36, `#1e293b` slate (light) | 30 / 800 / 36 |
| H2 | 18 / 700, `rgba(0,0,0,.54)` grey | 18 / 600 |
| Paragraph | 16 / 28 | 16 / 24 |
| Header | 96 px (bar + tabs), `#384D48` light, `#5C8076` dark | single 72 px row |
| White on dark header `#5C8076` | **4.37:1, fails AA** | n/a |
| Dark link colour | `#5488e8` indigo | n/a |
| Page transfer, cold | 995–1,323 KB; `logo.png` is 525 KB (631×622 shown at 24 px) | n/a |

Defects:

1. The newsletter box sits outside the content grid, running from x=16 to 1,236 px.
2. Its Subscribe button is unstyled, because Material only styles `.md-button` inside `.md-typeset`.
3. Its "Email address" label shows, because `md-visually-hidden` doesn't exist in Material 9.7.0.
4. Dark mode accent is indigo.
5. Light H1 is hard-coded slate.
6. Emoji and annotation markers render as tofu, but this box has no emoji font, so that is probably environment only and needs checking elsewhere.

## 3. Visual direction: "Ledger"

turbopuffer reads like an engineer's spec sheet: mono type, square boxes, box-drawing lines, a dark band, hard dithered shadows. Ledger keeps that restraint but takes its motifs from actuarial work: ruled ledger paper, hatched columns, and a lineage from source to model to decision. Green replaces navy, and a 45° hatch replaces the dither. There is no orange CTA.

- **Structure.** Header and tabs form one deep-forest band in both modes. Content sits on flat paper or night, with 1px hairlines, 0–2px corners and no soft shadows.
- **Signature.** A 6px offset shadow of 45° brand-green hatching (`repeating-linear-gradient` on `::after`, `pointer-events: none`). It appears on the newsletter card, primary buttons, admonitions, `.data-table` and the home band diagram.
- **Type.** Mono throughout. Hierarchy comes from colour and weight; H2 moves from grey to ink.

### Wow factor (revised)

| # | Element | How | Without motion/JS |
|---|---|---|---|
| W1 | Home band | Material `hero` block, `page.is_homepage` only. A full-width deep-forest band with a faint ruled-ledger grid, about 220 px at 1440, 160 px at 768, hidden below 600 px. **No text, no heading, no link.** `aria-hidden="true"`, no focusable children. The article (H1 "From data models to AI agents", its H2s, lists, CTAs) renders unchanged below it, with sidebar and TOC in place. At 1440×900 the article H1 should still land above the fold, around y≈420. | Static band |
| W2 | Lineage trace | An inline SVG inside W1. Four unlabelled box-drawn nodes joined by right-angle connectors, each with a hatched offset shadow. On first paint the connectors draw once in 1.2 s (`stroke-dashoffset`, CSS only, `animation-fill-mode: backwards`, so the resting state is fully drawn). No loop and no moving packet. | Fully drawn: `prefers-reduced-motion: reduce` sets `animation: none`, and with CSS animations off the base style is the end state. |
| W3 | Hatched ledger shadow | See Signature. Primary buttons shift 2px toward the shadow on hover and focus. | Static |
| W4 | Theme change (optional) | See section 3a. | Instant switch |

### 3a. Theme toggle: what ships and what's optional

Material binds its own handler to the palette `<input>`s and sets `data-md-color-scheme` in the same task. A View Transition needs to capture the old state before that change, which can't happen from a `change` listener without intercepting Material's control. So:

- **Ships (no JS):** a 250 ms colour crossfade on `body`, header, tabs, sidebars and typeset surfaces (`transition: background-color, color, border-color`), removed under reduced motion. It can't affect Material's controls.
- **Optional spike, kept only if every check passes:** `abm.js` calls `document.startViewTransition` on `pointerdown` and keyboard `keydown` (Enter/Space) of the palette label. It never calls `preventDefault` or `stopPropagation`. Its update callback waits for a `MutationObserver` to see `data-md-color-scheme` change (300 ms timeout), so Material still does the switching. It is feature-detected, skipped under reduced motion, and re-bound through `document$.subscribe` for `navigation.instant`. Required checks:
  - mouse and keyboard toggles both switch scheme and update the label/icon
  - two rapid toggles end in the right state
  - press and drag off the toggle leaves the page usable
  - the choice persists through reload, instant navigation and a new tab
  - 0 console errors
  - a click during an active transition still lands

  If any check fails, the spike and `abm.js` are dropped and only the crossfade ships.

## 4. Palette (approved)

Existing brand colours stay unchanged: Forest `#384D48`, Sage `#5C8076`, Deep `#2A3A36`, Mist `#F0F4F3` (the last two from `website/layouts/article.yml`).

| Token | Light | Dark | Use |
|---|---|---|---|
| `--abm-band` | `#2A3A36` | `#0E1513` | header, tabs, home band |
| `--abm-band-fg` | `#FFFFFF` (11.95:1) | `#E4ECE9` | text on band |
| `--abm-band-muted` | `#C9D8D2` (8.1:1) | `#93A69F` | inactive tabs, announce text |
| page bg | `#F6F8F7` | `#0E1513` | |
| `--abm-surface` | `#EAF0EE` | `#15201D` | code, cards, newsletter |
| `--abm-line` (decorative hairline) | `#D5DFDB` | `#2A3A36` | dividers, table rules only |
| `--abm-control` (input and control boundary) | `#7A8C85` (3.33:1 paper, 3.08:1 surface) | `#5C8076` (3.82:1 surface, 4.23:1 night) | inputs, outline buttons, tag chips |
| text | `#14201D` (15.7:1) | `#E4ECE9` (15.39:1, 13.91:1 on surface) | body, headings |
| muted text | `#55665F` (5.7:1 paper, 5.27:1 surface) | `#93A69F` (7.22:1 night, 6.52:1 surface) | meta, captions, TOC |
| primary | `#384D48` | `#5C8076` (borders/decoration only in dark) | buttons, rules |
| link / accent / focus | `#384D48` (8.47:1), hover `#2A3A36` | `#8FD1B5` (10.53:1 night, 9.52:1 surface) | links, focus ring, active tab |
| primary button | `#384D48` bg / `#FFFFFF` (9.04:1) | `#8FD1B5` bg / `#0E1513` (10.53:1) | CTA |
| hatch | `#384D48` at 35% | `#5C8076` at 60% | decoration |

Body links are underlined (1px, 3px offset, 45% current colour, full on hover), so colour isn't the only signal. Nav, TOC and tabs are left without underline, as their position marks them as links, and their active state uses weight plus a 2px rule as well as colour. Both palette entries get `primary: custom` and `accent: custom`. I'll measure syntax-highlight tokens on composited backgrounds during implementation and adjust any below 4.5:1 through the `--md-code-hl-*` variables.

## 5. Typography and spacing (approved all-mono, self-hosted)

- **Font.** JetBrains Mono variable woff2 (roman and italic) plus `OFL.txt` in `website/docs/assets/fonts/`, with `font-display: swap`. Fallback stack is `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`. The Google Fonts `@import` is removed, which drops a render-blocking request to Google that happens before cookie consent.
- **Scale.** Page H1 30/36/800 in ink. H2 20/28/700 in ink with 48px above. H3 16/24/700. Body 16px/1.7. Labels (TOC title, nav section titles, meta) 12px uppercase, +0.08em tracking, at least 4.5:1.
- **Measure.** Prose capped at about 68ch (inside the evaluator's 55–85 range). Code and tables use the full column and scroll inside their own container.
- **Rhythm.** 8px base. Header bar 56px plus 40px tabs is 96px total, unchanged, so sticky offsets and `scroll-margin` for anchors stay put. Reading gutter at least 16px at 320 and 390.

## 6. Page and template inventory

| Page | Template | Treatment |
|---|---|---|
| `/` | `main.html` | W1/W2 band above the grid. Article, sidebar and TOC unchanged. CTA pair restyled. |
| `/blog/` | Material `blog.html` | Empty state styled. Excerpt, archive, category and pagination styling checked on a throwaway post in a `/tmp` copy of `website/`, never in the repo. |
| blog posts (future) | `blog-post.html` + hook | Share buttons become outline buttons. Hook untouched. |
| `/blog/tags/`, `/tags/` | `main.html` | Square tag chips with control border. |
| `/learn/…` (7 routes) | `main.html` | Code, tabs, annotations, admonitions, `.data-table`, Plotly. `/learn/data/spacex/` is the stress page. |
| `/learn/agent_index/` | `main.html` | Inherits. |
| `/about/` | `main.html` | `.circular` avatar gets a hatched ring. |
| `/newsletter/`, `/cookie-policy/` | `main.html` | Newsletter card; consent dialog restyled. |
| `404.html` | Material | Inherits; home link and search work. |
| Global | header, tabs, announce, search, drawer, footer, consent, back-to-top | CSS only. |

## 7. Files I expect to touch

| File | Change |
|---|---|
| `website/docs/assets/extra.css` | Rewrite (CRLF). Existing hooks keep working: `.data-table`, `.circular`, `.newsletter-*`, `#hero-subtitle`, `.purple-icon` / `.red-icon` / `.gold-icon` (used in `learn/data/spacex.md`). |
| `website/overrides/main.html` | New `hero` block (homepage only, includes the diagram partial). Newsletter wrapper gains `md-typeset` and is aligned to the content grid. Announce text and the `footer` logic stay. **No `content` block override.** |
| `website/overrides/partials/abm-ledger.html` | New: decorative SVG (`aria-hidden`, `focusable="false"`, no `<text>`). |
| `website/docs/assets/logo.svg`, `favicon.svg` | New: small square "ABM" monogram. `logo.png` stays for the four social-card layouts. |
| `website/docs/assets/fonts/*` | New: woff2 files and `OFL.txt`. |
| `website/mkdocs.yml` | `logo`, `favicon`, and `primary: custom` / `accent: custom` on both palettes. `extra_javascript` only if the W4 spike passes. Nav, plugins and `extra` untouched. |
| `website/docs/assets/abm.js` | Only if the W4 spike passes. |

`overrides/partials/newsletter.html` is now **left untouched**: the label stays visible and gets styled (see R2). No Python or function signatures change. If one does, I'll grep every call site.

## 8. Risks

| Risk | Mitigation |
|---|---|
| Band pushes content down on short screens | About 220 px cap, hidden below 600 px, H1-above-fold check at 1440×900 and 1280×800. |
| Full-bleed band adds horizontal scroll | It sits outside `.md-grid` at `width: 100%`, no `100vw`. Overflow check at every width. |
| JS dead after instant nav | Only relevant if the W4 spike ships; it re-binds via `document$`. |
| Breaking Material's toggle | Crossfade by default; the spike is opt-in behind the checks in 3a. |
| Pytest regenerates chart files | I record any `git status` changes after `pytest` and don't revert them. Charts aren't styled by this work. |
| Material upgrade | Pinned 9.7.0. Overrides use variables and stable `.md-*` classes. |
| CRLF loss | `file` check after each edit. |
| Font weight | About 110 KB of woff2 against 525 KB saved by the logo. |

## 9. Validation

From the repo root, with my evidence kept outside the repo in `/home/cooperm/.adal/engineer/tasks/analyticsbymark-redesign/builder/` (a separate subfolder from the evaluator's `baseline/` and `final/`):

```bash
uv run pytest -v                                     # 45 pass; record any regenerated files
uv run mkdocs build --strict -f website/mkdocs.yml --site-dir /tmp/abm-after
diff <(cd /tmp/abm-before && find . -type f -name '*.html' | sort) <(cd /tmp/abm-after && find . -type f -name '*.html' | sort)
git diff --stat -- website/docs website/overrides website/mkdocs.yml   # only section 7 files; no .md
git status --short
file website/mkdocs.yml website/overrides/main.html website/docs/assets/extra.css
```

Parity scripts (scratch, outside the repo) compare before and after builds for every route:

- ordered nav labels, nesting and hrefs
- heading ids
- normalised `article` text
- code bytes, table cells, image `src`/`alt`
- newsletter, announce, copyright, social and consent copy

Expected difference: the home band markup, which has no text.

Visual matrix, browser-use once the worker has Node 22, otherwise Playwright via isolated Node 22:

- Every route at 390 and 1440 in both themes.
- Representative pages at 320, 375, 768, 1024 and 1280, at 200% zoom, and either side of the 600 px band breakpoint.
- Overflow `scrollWidth <= innerWidth + 1`, contrast on composited colours, focus visible and not under the sticky header, targets at least 24×24.
- Reduced motion (band fully drawn, no crossfade).
- Toggle and persistence, search, drawer, TOC anchors, content tabs, consent, the `/tmp` blog fixture, `404.html`, and console errors after instant navigation.

## Response to evaluator

I read `docs/redesign-evaluator-plan.md` and adopt its preservation gates, viewport matrix, contrast rules (composited, 3:1 for control boundaries), motion rules and blocker list as my own pass criteria. Where my rev-1 plan conflicted, this revision changes as follows.

| # | Conflict | Evaluator / lead position | Resolution in rev 2 |
|---|---|---|---|
| R1 | Rev 1 hid the home sidebar and TOC via `body:has(.abm-home)` | Nav gate 3 and the lead: keep navigation | **Dropped.** No sidebar or TOC hiding anywhere, and no `abm-home` wrapper or `content` block override. |
| R2 | Rev 1 planned to visually hide the newsletter "Email address" label (sr-only) | Gate 4: CSS-hidden content isn't preserved in practice | **The label stays visible** and is styled as a small field label. `newsletter.html` is no longer edited. |
| R3 | Rev 1 hero restyled the article's own H1 and H2 as a band | Lead: band above content, article unaltered, no duplicate H1 | The band is a separate `hero` block with no text. The article H1 isn't restyled into it. |
| R4 | Rev 1 diagram had word labels and a looping packet | Lead: geometry only, one-shot 1.2 s; evaluator motion rules | No `<text>`, a one-shot trace, resting state fully drawn, nothing hidden without CSS animation or JS. |
| R5 | Rev 1 shipped a View Transition on the toggle | Lead: optional, must not intercept; evaluator: no lost handlers, persistence checks | The crossfade ships by default. The VT is a gated spike (3a) and dropped on any failure. |
| R6 | Rev 1 links relied on colour only | Controls: colour not the only indicator | Body links underlined; active nav uses weight and a rule. |
| R7 | Rev 1 used `#D5DFDB` for input borders (1.28:1) | 3:1 for control boundaries | New `--abm-control` token, `#7A8C85` light and `#5C8076` dark, both above 3:1. |
| R8 | Rev 1 checked only 390 and 1440 | Full 320–1440 matrix, 200% zoom, breakpoints | Adopted (section 9). |
| R9 | Rev 1 allowed a blog demo post | No invented routes | Fixture only in a `/tmp` copy, never in the repo or the published site. |
| R10 | Browser runtime | Evaluator: no visual claims until the runtime is fixed | Isolated Node 22 installed and proven. browser-use needs a worker relaunch with `ADAL_ELECTRON_NODE` (section 1). Until then, evidence is labelled by tool. Source inspection isn't counted as visual verification. |
| R11 | Artifact location | Evaluator owns `…/analyticsbymark-redesign/baseline` and `final` | My evidence goes in `…/builder/`. I won't write to the evaluator's folders or its plan. |
| R12 | `#newsletter` INFO diagnostic | Evaluator: confirm on render, not as a broken link | Kept as is. The anchor is rendered by `main.html`, and I'll confirm it in the after build. |

There are no remaining disagreements with the evaluator's plan. One shared dependency is open: the evaluator's interactive checks hit the same Node 18 runtime limit, so the `ADAL_ELECTRON_NODE` relaunch would unblock both workers.

## 11. Gate

I'm waiting for the contract gate before writing any code. Open items for the lead:

1. Relaunch the worker(s) with `ADAL_ELECTRON_NODE`, or accept "Playwright via isolated Node 22" evidence until then.
2. Confirm the W1 band size (about 220 px desktop, hidden below 600 px).
