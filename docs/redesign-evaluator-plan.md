# Redesign evaluator plan

Date: 2026-11-07  
POC: Independent visual evaluator  
TL;DR: Preserve every existing page, content block, URL, and navigation branch. Evaluate the redesigned MkDocs site in both themes across phone, tablet, and desktop widths. Build and preservation checks are hard requirements; visual approval also requires a deliberate typography and spacing system across all page types.

## Scope and independence

This is a planning and baseline-capture task. No app code, tutorial source, existing assertion, or deployment setting is changed. No commits or reverts are permitted. The builder owns the preview server. Discover its port before connecting; do not start a competing server. The architecture graph is unavailable because graphify is not installed.

The contract is `/home/cooperm/.adal/engineer/contracts/2026-11-contract.md`. Baseline and final evaluation artifacts belong outside the repo at `/home/cooperm/.adal/engineer/tasks/analyticsbymark-redesign/`.

## Existing infrastructure

The baseline revision is `4a892b5423fe75b8b9067cdc9206317f9f60c98a` on `re-brand`; the working tree was clean at initial capture. MkDocs 1.6 uses Material 9.7.0, with the configuration in `website/mkdocs.yml`, shared styles in `website/docs/assets/extra.css`, and overrides in `website/overrides/`.

The current brand colors are `#384D48` in light mode and `#5C8076` in dark mode. Both schemes already exist. Navigation uses tabs, nested sections, breadcrumbs, instant navigation, tracking, and a following TOC. Search, table-reader, social cards, blog, metadata, tags, RSS, snippets, annotations, content tabs, and admonitions are configured. The newsletter partial is shared above the footer, except on the cookie policy and pages with `newsletter: false`.

There are 15 published Markdown sources, including two tag indexes and the unlisted agent index. No blog post Markdown exists in the published docs tree at capture time. Tutorial outlines under `docs_src` are not published posts. Do not invent a live post route to claim blog-post coverage.

Pytest discovers tutorial tests under `website/docs_src` and shared fixtures under `tests`. It tests data loading, tutorial subprocesses, generated charts, Dash layouts, and snippet ranges. It does not provide a visual, accessibility, navigation, or theme regression suite. Some tests regenerate chart files. Record any resulting changes; do not revert or silently exclude them.

CI installs with `uv sync --frozen`, runs `uv run pytest -v`, then performs a strict MkDocs build. Production deployment separately refuses the configured placeholder newsletter. Evaluation must not deploy or submit the form.

## Baseline artifacts and validation

`capture_baseline.py` lives outside the repo. It records source bytes, SHA-256 hashes, ordered navigation, generated HTML routes, article text, headings and anchors, links, images, and component counts. The source snapshot is taken before the tutorial tests run. Generated HTML is captured after validation.

Artifacts:

- `baseline/sources.json`: source text and hashes, initial revision and working-tree status.
- `baseline/navigation.json`: ordered labels, nesting, destinations, excluded navigation paths, canonical base, and directory-URL policy.
- `baseline/routes.json`: every generated HTML route, including pages omitted from nav and `404.html`.
- `baseline/site/`: built baseline for inspection and comparison.
- `baseline/pytest.log`, `baseline/build-strict.log`, and `baseline/validation.json`: full outcomes and final working-tree status. A failed strict build triggers a separately labeled non-strict diagnostic build, never a replacement pass.

Full local validation, from the repository root:

```bash
uv sync --frozen
uv run pytest -v
uv run mkdocs build --strict -f website/mkdocs.yml --site-dir /home/cooperm/.adal/engineer/tasks/analyticsbymark-redesign/final/site
```

For the captured baseline, the final command uses `baseline/site` instead of `final/site`. The existing environment is used for this initial run; dependency synchronization is not claimed unless separately executed. Record the suite count, build exit code, warnings, runtime, and source revision. Never weaken existing assertions or disable warnings to make the redesign pass.

Baseline result: `uv run pytest -v` passed all 45 tests in 115.04 seconds (exit 0). The strict build passed in 1.36 seconds (exit 0), with 16 generated HTML routes and 222 captured source/config files. No baseline test or strict-build failures occurred. Existing INFO diagnostics report three unrecognized relative links from `learn/agent_index.md`, a missing `#start` anchor in `learn/virtual_environments.md`, and an `index.md` link to `#newsletter` that MkDocs cannot see during Markdown validation. The shared footer template supplies the newsletter anchor in generated HTML, so that last diagnostic needs rendered confirmation rather than automatic classification as a broken link. Cookie policy and the root tag index are intentionally outside the explicit nav. Full logs are preserved; no warnings were suppressed.

Browser baseline limitation: the shared Chrome endpoint responds on port 9222, but the browser driver refuses the installed Node 18.20.2 because it requires Node 20 or newer. The builder-owned preview was subsequently discovered at `http://127.0.0.1:8010/` and returned HTTP 200. No competing site server was started. A second connection attempt still failed on the runtime requirement. Browser screenshots, rendered contrast, and interactive baseline checks remain unverified until a supported runtime is available. Do not report source inspection as visual verification.

## Preservation gates

1. Every baseline Markdown page retains its source content, metadata, snippets, code, tables, links, and image references. Prefer exact source hashes where presentation can live in CSS or templates. For any approved markup-only change, compare parsed text, heading order, link destinations, code bytes, table cells, image sources/alt text, and metadata explicitly. Content changes require separate approval.
2. The baseline route set must be a subset of the final route set with no path renames, missing files, or redirect substitutes. Explain any additions. Preserve non-nav pages, `404.html`, feeds, search assets, canonical URLs, and existing heading fragment identifiers. Compare all baseline files and anchors, not just sitemap entries.
3. Ordered navigation labels, nesting, and page targets must match `baseline/navigation.json` exactly. Top-level order remains Home, Blog, Learn, About, Newsletter; Learn retains Data, SpaceX, and Setup with their current children. Mobile rendering may change presentation, not information architecture.
4. Compare normalized generated article content for every route. Investigate any differences against the raw source snapshot. Also compare newsletter copy, announcement text, copyright, social links, cookie-policy access, and consent copy outside the article. CSS-hidden content is not preserved in practical terms: inspect visibility and accessibility.
5. All baseline local links and fragments must resolve after the build. Distinguish existing broken links from newly introduced ones and retain evidence of both. Existing defects do not authorize removing their content.

## Measurable visual and accessibility criteria

| Area | Proposed acceptance criterion |
| --- | --- |
| Viewports | Check 320, 375, 390, 768, 1024, 1280, and 1440 CSS-pixel widths at a consistent 900-pixel height. Check portrait and landscape behavior and 200% browser zoom. Use 320 CSS pixels to cover reflow equivalent to a 1280-pixel viewport at 400% zoom. |
| Theme matrix | Every generated HTML route at 390 and 1440 pixels in both light and dark. Representative component pages at all listed widths in both themes. Check immediately below and above any actual CSS breakpoint discovered in the implementation. |
| Overflow | `document.documentElement.scrollWidth <= window.innerWidth + 1`. No clipped body text, header controls, forms, nav, or footer. Wide tables and preformatted code may scroll inside a labeled, keyboard-operable container without widening the document. |
| Typography | Body text at least 16 CSS pixels, with line height approximately 1.5 to 1.8. Desktop prose measure approximately 55 to 85 characters; narrower screens use available width. Heading hierarchy and code hierarchy remain clear. Log measured sizes and line height, plus font fallback behavior. |
| Spacing | Use a consistent spacing scale. At 320 and 390 pixels, preserve at least 16 pixels of reading gutter unless a documented component needs less. No overlap at headings, sticky header, TOC anchors, consent dialog, or newsletter. |
| Contrast | WCAG AA: at least 4.5:1 for normal text, 3:1 for large text, and 3:1 for control boundaries and meaningful state indicators against adjacent colors. Check both themes, syntax tokens, muted text, footer links, inputs, hover, focus, active nav, and disabled-state clarity. Composite alpha backgrounds before calculating. |
| Brand | Keep dark green as the principal brand accent. Retain the existing green tokens or document accessible green variants. Neither theme may default to Material blue or borrow turbopuffer logos, copy, or product imagery. |
| Controls | Visible focus on every interactive element, not obscured by sticky UI. Targets meet WCAG 2.2 AA minimum 24 by 24 CSS pixels or its spacing exception; aim for 44 by 44 on principal touch controls. Color is not the only indicator for links or selected states. |
| Motion | With `prefers-reduced-motion: reduce`, remove decorative entrance effects, parallax, and smooth-scroll animation. No content stays hidden if animation or JavaScript is unavailable. |
| Visual quality | Side-by-side baseline and redesign review at identical viewport, theme, consent state, and scroll position. Typography, whitespace, hierarchy, and green brand treatment each score at least 4/5 using the rubric below. No page type may rely on an unstyled fallback. |

The visual rubric uses 1 for broken or generic, 3 for consistent but ordinary, and 5 for distinctive and polished. Score typography by readability and intentional hierarchy; whitespace by rhythm and content measure; hierarchy by how quickly a reader can find title, section, and next action; brand treatment by whether the green identity feels coherent in both themes. Record concrete screenshot observations with each score. A numerical score alone cannot establish the requested wow factor. The final reviewer should identify the signature design move and confirm it improves the reading experience without obscuring content.

## Functional checks

- Toggle light to dark and back. Verify the displayed icon/name, palette attribute, and actual rendered colors agree. Selection persists through reload, direct navigation, instant navigation, and a new tab on the same origin. Test fresh storage separately; the initial choice must be usable and deterministic, and an explicit choice must override system preference if system detection is offered.
- Search for a known tutorial phrase, then an absent phrase. Check results, destination, highlighted text where supported, Escape dismissal, keyboard selection, focus restoration, and narrow-screen layout. Wait for the local index to load; do not classify initialization delay as empty search.
- Traverse desktop nav and nested Learn sections; repeat via the mobile drawer. Verify active states, labels, Home/logo target, Escape behavior, focus handling, and that every branch remains reachable.
- Follow a TOC anchor on a long page. The heading must be visible below sticky UI; active state and URL fragment must update appropriately. Check direct fragment entry, browser Back, and instant-navigation arrival.
- Inspect `/learn/data/spacex/` for tables, long values, syntax highlighting, admonitions, and data-reader output. Inspect `/learn/spacex/creating_policies/` for embedded source and line anchors. Inspect `/learn/spacex/sandbox/` for tabs and nested annotations; switch a tab and verify visible content. Test configured code select/copy behavior only where controls actually exist; do not require an unconfigured control.
- Check `/blog/`, `/blog/tags/`, and `/tags/` for empty-state presentation and intact links. Blog post, category, archive, and pagination routes are not present in the current published content. Validate template compatibility by inspection now. After approval, use an isolated disposable fixture build outside the repo if live component coverage is required; do not add demonstration posts to the published site.
- Check `/`, `/about/`, `/newsletter/`, `/learn/`, `/learn/data/`, `/learn/virtual_environments/`, `/learn/spacex/launch_cadence/`, `/learn/agent_index/`, and `/cookie-policy/`. This includes the profile image, newsletter input/label, footer, consent settings, unlisted content, and code-heavy pages.
- Open an unknown path and inspect the themed `404.html` with a working route home and search/navigation. Confirm HTTP 404 in the deployment context; a local preview may return a different status and must be labeled accordingly.
- Traverse all major controls using only Tab, Shift+Tab, Enter, Space, arrows, and Escape. Check skip link, visible focus, drawer/search/consent focus containment and restoration, no traps, form labels, headings, and accessible names. Do not submit Mailchimp or grant optional analytics consent merely to test styling.
- Inspect console and failed requests on representative pages and after instant transitions. No new first-party JavaScript errors, broken local assets, duplicate newsletter instances, or lost event handlers. Separate external network failures from app failures.

## Final evaluation sequence and evidence

1. Keep the baseline immutable. Record the final revision and working-tree diff; list changed files and explain changes beyond CSS/templates.
2. Run the full validation command and preserve uncapped logs outside the repo. Compare failures and warning messages to baseline. Build success is necessary for acceptance; pre-existing defects remain explicitly listed if not separately approved for repair.
3. Produce route, content, nav, anchor, and asset comparison reports for every baseline page. Record expected presentation differences explicitly, without broad text exclusions that could hide content loss.
4. Attach to the builder's confirmed preview origin. Resolve the runtime blocker before interactive claims. Use a dedicated browser window and known viewport. Perform one action, observe it, and capture a screenshot when target identity matters.
5. Save labeled desktop/mobile screenshots of every route in both themes, then the full representative-width matrix and interaction states. Use viewport screenshots for sticky layouts; use component captures for tables, code, and forms. Link measurements and any accessibility report to the route, theme, viewport, and state.
6. Write `final/evaluation.md` outside the repo with pass/fail/unverified per criterion, exact reproduction steps, severity, evidence paths, and baseline versus new failure classification. Missing evidence remains unverified. Do not approve solely from build success or homepage appearance.

Release blockers are lost or altered content, changed baseline URLs/nav, build failure, new test failures, inaccessible essential controls, unreadable contrast, page-level overflow, broken theme persistence, or a broken page family. Cosmetic issues receive explicit severity and screenshots. The user approves the visual direction; the evaluator provides the evidence and any remaining limitations.

## Response to builder

Date: 2026-11-07  
Status: Planning critique complete; awaiting implementation and build handoff. The lead decisions below supersede conflicting options in the builder plan and clarify the evaluation criteria above.

### Decisions and conflicts

| Builder proposal | Evaluation response and binding decision |
| --- | --- |
| Hide home sidebars and remove its desktop TOC, including the `body:has(.abm-home)` hiding rule | Conflicts with preservation. Keep the home TOC, sidebar, and navigation. Existing responsive collapse behavior may remain, but the redesign must not remove a branch or suppress the home TOC at widths where it was available. Verify headings, anchor destinations, and reachability alongside the hero layout. |
| SVG nodes labeled `raw data`, `model`, `insight`, and `agent` | Conflicts with the no-new-visible-words decision. Use geometry only, with no visible words, captions, tooltips, or generated text. Keep the decoration outside the meaningful content/accessibility tree with `aria-hidden="true"` and no focusable descendants. Existing page copy remains unchanged. |
| One connector draw followed by a looping mint packet | Conflicts with the motion decision. A one-shot trace is permitted; no looping packet, repeated animation, timer restart, or scroll-triggered replay. With reduced motion, render the complete static geometry immediately. |
| All-mono versus optional Plex Sans | Decision resolved: all-mono, self-hosted JetBrains Mono with license included. Remove third-party font loading. Verify real font requests, computed families, fallback behavior, and that no missing glyph or font failure hides content. |
| Exact green palette | Approved in principle, subject to rendered contrast checks. Token-table arithmetic is not final evidence: verify the actual text, alpha composition, background, and interaction state. See scope and contrast classification below. |
| Circular theme reveal | Accept only as progressive enhancement. Native Material palette controls remain the source of truth. Unsupported API, reduced motion, rejected transition, or enhancement failure must not cancel or double-fire the native toggle. Check mouse and keyboard activation, rapid toggles, persistence, and toggle → instant navigation → toggle. No duplicate subscription/listener effects. |
| Browser-use only if Node approval arrives; Selenium fallback acceptable | Superseded. The builder is repairing Node to version 20 or newer outside the repo without changing the default runtime. Final interactive checks must use the repaired browser tooling. Confirm attachment works; do not treat installation alone as a repair or report old fallback captures as final verification. |

### Scope and baseline classification

The external `baseline/sources.json`, `baseline/navigation.json`, `baseline/routes.json`, and `baseline/site/` remain the source of truth. The builder's `/tmp/abm-before` and screenshot set are useful supporting evidence but must not replace or overwrite these manifests. Do not reconstruct the baseline from a later HEAD or working tree. Keep final artifacts in the external task directory.

The proposed CSS, existing template/partial edits, decorative partial, enhancement script, self-hosted fonts, and logo/favicon assets fit the presentation scope subject to the decisions above. Preserve the PNG required by social cards. Nav, plugins, hooks, tutorial code, published Markdown, content metadata, and deployment behavior stay unchanged. The generic remark about Python call-site checking does not authorize a Python change.

Newsletter alignment, button styling, and an accessible label treatment are presentation/accessibility repairs, not permission to change form copy, fields, action, or subscription behavior. Preserve the label's text and programmatic association if it becomes visually hidden. Record that deliberate visibility change explicitly rather than excluding all labels from parity checks.

Classify each finding as:

- New regression: absent in the baseline, introduced or worsened by the redesign. Block release for content/nav/route loss, essential interaction failure, new failing tests, unacceptable overflow, or contrast failure in changed styling.
- Baseline defect repaired: identify the before and after evidence. The reported dark-header white-text ratio of 4.37:1 is a builder baseline finding pending independent rendered confirmation; replacing that header styling must meet the contrast target.
- Baseline defect unchanged: keep it visible in the report with its original route/state. Existing agent-index links and the `#start` diagnostic are not new redesign failures and do not justify unrelated content edits. An unchanged baseline defect is not an automatic veto on this presentation task; severe remaining accessibility issues still need explicit lead disposition before claiming full accessibility compliance.
- Unverified: evidence or tooling is missing. Never relabel this as pass or baseline defect without comparison.

This classification qualifies the earlier broad release-blocker wording: new regressions and failures in redesigned components block acceptance; unchanged out-of-scope baseline defects are disclosed separately. A baseline defect that the redesign restyles or touches must be evaluated against the new component criteria, not grandfathered in.

### Contrast criteria

Use WCAG AA thresholds of 4.5:1 for normal text and 3:1 for large text (at least 24 CSS pixels regular, or approximately 18.67 CSS pixels bold). Meaningful control boundaries and state indicators need 3:1 against adjacent colors where required to identify the control or state. Decorative ledger grids, hatching, and nonessential geometry do not need 3:1 merely because they are visible. Do not apply the builder's blanket 4.5:1 requirement to every decorative border or large heading.

Measure actual rendered pairs in both themes, including code tokens, muted navigation, search, consent, links, forms, and hover/focus/selected states. Composite translucent colors over the effective background and inspect gradients/images manually where a single computed background is insufficient. Record baseline and final ratios for failing pairs. New or changed text styling must pass; unchanged failures must be listed as baseline defects. An automated computed-style scan supplements visual inspection and cannot establish complete WCAG compliance.

### Parity checks and exclusions

Visible article-text parity alone is insufficient. Compare source content, code bytes, table cells, metadata, headings and fragment IDs, image references, link targets, and ordered navigation, plus shared announcement, newsletter, footer, and consent text. Check that retained content is still available to readers and assistive technology. Do not exclude all `aria-hidden` elements or all hidden DOM text: such a filter can conceal content loss.

The existing opt-in honeypot may be excluded from visible-text parity only after confirming it is truly hidden from visual presentation and assistive technology, remains out of sequential keyboard focus, and cannot create document overflow at the tested widths. Preserve its field name and submission behavior. Keep its source/DOM record in the structural comparison. Geometry-only decoration contributes no text to exclude. Any other intentional visibility change, including the newsletter label, needs a specific recorded explanation and an accessibility check.

Keep the baseline HTML route set identical for this task, including all non-nav routes and `/404.html`; static asset additions are expected. Sitemap parity alone misses the 404 and does not prove content or nav preservation. The only expected repository planning changes are the two plans; evaluate implementation changes separately from those docs.

### Final matrix and practical checks

The required all-route matrix is 16 routes × 2 themes × 2 widths (390 and 1440 CSS pixels), for 64 route/theme/width states. Include empty blog/tag pages, the unlisted agent index, cookie policy, and 404. Record viewport height consistently for before/after comparisons; label any differing builder capture heights.

Additionally inspect complex representative pages in both themes at 320, 768, and 1024 pixels:

- `/`: retained home TOC/sidebar/nav, hero geometry, narrow layout, and native toggle.
- `/learn/data/spacex/`: long code, table-reader output, tables, and admonitions.
- `/learn/spacex/creating_policies/`: snippets and line anchors.
- `/learn/spacex/sandbox/`: tabs, annotations, and code.
- `/learn/agent_index/`: multiple tables and long navigation/link content.
- `/newsletter/`: input, accessible label, CTA, and shared footer alignment.

Exercise search and consent overlays at these representative widths as shared components. The earlier 375/1280 widths and breakpoint-adjacent checks are supplemental diagnostics; they do not replace the required matrix. Retain the zoom, keyboard, reduced-motion, theme-persistence, and no-JavaScript/API-fallback checks above.

Do not accept `overflow-x: clip` as proof that the hero fits. Require document overflow within one pixel and verify that clipped descendants contain no lost text, focus ring, TOC, or control. Wide table/code containers may scroll locally.

The proposed 600 KB cold-home transfer is a builder performance target, not a content-removal allowance or independently established release gate. If measured, state cold-cache setup, compression, actual transferred bytes, and font/resource completion. Classify console failures by first-party regression, baseline issue, or external network failure instead of requiring an unexplained blanket zero.

No implementation or additional server is started by this critique. Await the builder's build handoff and confirmed repaired browser attachment before final evaluation.

## Approved-build evaluation addendum

Date: 2026-11-07  
POC: Independent visual evaluator  
TL;DR: The contract now says Approved to Build. Prepare checks only while implementation is in progress; begin final evaluation after a stable build handoff.

The approved contract supersedes the earlier transition proposal and tooling requirement in this plan. Use the native Material toggle with CSS crossfade only. No custom toggle JavaScript, click interception, or View Transition enhancement is approved. Verify the native control by mouse and keyboard, then inspect palette, rendered colors, persistence after reload, and instant-navigation behavior. Reduced motion must disable decorative animation and smooth transitions.

The geometry-only hero sits above the unchanged article, at most 220 CSS pixels tall on desktop and 160 on tablet, compact or omitted on phones. Keep the home sidebar and TOC. The trace runs once for at most 1.2 seconds with no loops. These are acceptance criteria, not optional suggestions.

### Approved independent browser setup

The worker-process browser connection still uses Node 18 and is blocked. The lead approved direct Playwright with the isolated executable `/home/cooperm/.adal/engineer/tooling/node22/bin/node` and AdaL's existing bundled Playwright. The builder's connection example resolves it at `/home/cooperm/.adal/versions/1.11.6/node_modules/playwright-core`.

Use a new isolated context and evaluator-owned tabs only. Never enumerate, inspect, navigate, or close other agents' or the user's tabs. Close only the evaluator context; never close the shared browser. Do not change runtime defaults, PATH configuration, repository dependencies, or lockfiles. Verify one interaction and observe its resulting state before the next action. Do not use an automated action loop as a substitute for inspecting results.

The external `evaluator/connection-smoke.cjs` checks runtime and browser connection with a new blank tab only. It does not visit the site or establish final visual acceptance. Final screenshots and measurements must be independently captured after handoff; builder captures remain supporting evidence.

### Stable-handoff gate and prepared checks

Before final evaluation, obtain the builder's stable preview URL, final build directory, changed-file list, validation results, fixture-build location, and confirmation that active implementation has paused. Do not rebuild into a builder-owned directory, restart its server, or take final acceptance measurements against a moving implementation.

After handoff:

1. Compare the unchanged 15 Markdown source bytes and ordered nav against the external manifests. Check all 16 route paths, existing headings/anchors, article content, shared copy, canonical/sitemap/feed/search outputs, and baseline local-link diagnostics. Preserve the narrowly verified honeypot exclusion described above.
2. Run the full 45-test suite and strict MkDocs build into the evaluator's external final directory. Check scope, pinned infrastructure, CRLF in edited existing files, font licensing/self-hosting, and retained social-card PNG.
3. Independently inspect all 64 route/theme/width states at 390/1440, plus complex families at 320/768/1024 and 200% zoom. Apply the existing overflow, role-based contrast, baseline-defect classification, keyboard, and component checks.
4. Inspect the external disposable blog fixture for post/archive/category compatibility without publishing demonstration content.
5. Measure the contract's home first-load target of at most 600 KB with a documented cold-cache setup and actual transferred bytes. Report the result even if the target is missed; do not delete content to meet it.
6. Write the final evidence-backed report at `/home/cooperm/.adal/engineer/tasks/analyticsbymark-redesign/final/evaluation.md`. Keep each criterion pass, fail, or unverified and separate baseline defects from regressions.

Current state: awaiting stable handoff. Preparing the connection and check sequence does not approve or evaluate the in-progress implementation.

