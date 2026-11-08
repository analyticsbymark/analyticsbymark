# What changed in the re-brand

A summary of what the AdaL engineer team changed to move the site to the new look and feel: typography-led, lots of whitespace, hairline detail, built on your existing dark-green branding. Everything below is uncommitted work on the `re-brand` branch, measured against the last merged commit.

MkDocs and Material are still the build system. No page content, URL or navigation entry was removed.

## Files touched

| File | Change |
| --- | --- |
| `website/docs/assets/extra.css` | Rewritten styling layer: about 1,070 lines added and 57 removed |
| `website/mkdocs.yml` | New SVG logo and favicon, custom palette for both themes, named dark-mode toggle, this page added to `not_in_nav` |
| `website/overrides/main.html` | Home page wrapper for the hero, and a restructured newsletter wrapper |
| `website/overrides/partials/abm-ledger.html` | New: decorative home hero graphic, geometry only, no text |
| `website/docs/assets/logo.svg`, `favicon.svg` | New compact SVG identity. The PNG logo is kept for social cards |
| `website/docs/assets/fonts/` | New: self-hosted JetBrains Mono (roman and italic) with its OFL licence |
| `website/docs/showcase.md` | This page |

## Look and feel

- **Typography.** JetBrains Mono everywhere, self-hosted, so there is no external font request. Body text is at least 16px with a deliberate prose width. Code, tables and media keep the full column.
- **Colour.** Your dark green is the identity in both light and dark modes, with a mint accent. Material's default indigo no longer shows through.
- **Header.** The announcement bar, header and tabs share one deep-forest band.
- **Home hero.** The existing headline sits in a card with a ledger-style graphic: source table, model grid, chart, decision. It has a one-shot trace animation that finishes in 1.2 seconds and never loops. On phones it shrinks to a compact version.
- **Detail language.** Hairline borders, ruler ticks, and diagonal hatched "ledger" shadows on buttons, cards and the profile photo.
- **Content elements.** Square admonitions, restyled tables, tabs, tags, inline code and code blocks, newsletter block and footer.
- **Links.** Links in prose are underlined as well as coloured.
- **Theme toggle.** The native Material toggle now crossfades without any custom JavaScript.

## Accessibility

- Focus rings are 2px, in mint on the dark band and forest green elsewhere.
- Code copy and select icons were low-contrast. A targeted rule now gives them over 10:1 calculated contrast in both themes, and in rest, hover, focus and selected states.
- The dark-mode toggle had no accessible name and now has one ("Switch to light mode").
- Reduced-motion users get no hero trace, no crossfade and no smooth scrolling.

## Deliberately unchanged

- Page content, URLs, sitemap and navigation.
- The home sidebar and table of contents.
- The home page was reviewed and left alone once accepted.

## Checks run

- Full test suite: 45 tests pass.
- Strict MkDocs build: passes, with the existing link notices still present.
- Contrast figures come from calculation. Live in-browser measurement was not available.

## Not yet done

- The full visual sweep (16 routes, both themes, mobile and desktop) and the written evaluation report are still open.
- The work is not committed.
- This page is reachable by direct URL only (`/showcase/`). It is not in the navigation and not private.
