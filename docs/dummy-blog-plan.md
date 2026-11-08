# Dummy blog posts plan: "a mature site, 3 years in"

Status: **proposed, awaiting approval.** Branch: `dummy_blog_posts`. Nothing below is built yet.

## Goal
Fill the blog with believable posts, as if the site had run for three years (roughly Nov 2023 to Nov 2026), so every blog feature is visible in one place and you can see how to use it. Posts are clearly fake and must never reach the live site by accident.

## 1. Safety: keeping dummy content off production
- All dummy posts live in `website/docs/blog/posts/` with the filename prefix `dummy-` and a front-matter flag `dummy: true`.
- Every dummy post shows a visible "Sample post" admonition at the top (not hidden).
- A tiny CI check fails the build if any `dummy: true` post is present when building the production branch. Nothing merges to `master` by accident.
- Removing them later is one command: delete `dummy-*.md`.
- Authors are fictional, in `.authors.yml`, with a "Sample" label. Your real name is not put on invented claims.

## 2. The content set (12 posts)
Spread over 3 years, 5 existing categories (Data Engineering, Analytics, APIs, Actuarial, AI Agents), about 15 tags.

| # | Working title (sample) | Category | Role in the demo |
|---|---|---|---|
| 1 | "Why your reserving data keeps breaking" | Data Engineering | Oldest post; pillar for a keyword cluster |
| 2 | "Pydantic for actuaries: first model" | Data Engineering | Series part 1 of 4 |
| 3 | "SQLModel: from CSV to policy table" | Data Engineering | Series part 2 of 4 |
| 4 | "Validating claims feeds before they hurt you" | Data Engineering | Series part 3 of 4 |
| 5 | "Shipping the model: a repeatable pipeline" | Data Engineering | Series part 4 of 4 |
| 6 | "Choosing a chart your CFO will read" | Analytics | Image-heavy; charts and before/after |
| 7 | "Loss ratio dashboards in Dash" | Analytics | Tabs, code, screenshot gallery |
| 8 | "Calling a rating API from Python" | APIs | Code-tab examples, tables |
| 9 | "Cat modelling inputs, explained simply" | Actuarial | Tables, admonitions, glossary links |
| 10 | "Building an AI agent that profiles your data" | AI Agents | Uses copy-as-prompt and copy-as-skill |
| 11 | "Prompts that earned their keep" | AI Agents | Several prompt blocks, `start_here` |
| 12 | "3 years of notes: what I'd tell myself" | Analytics | Retrospective; links to all pillars; `start_here` |

Bodies are short (400 to 900 words) and written to be useful placeholders, not filler. Where possible they reuse real material from the SpaceX and policy tutorials so the examples run.

## 3. Features each post will demonstrate
| Feature | Where it appears | Notes |
| --- | --- | --- |
| Categories, tags, tag index | all posts | Tag cluster pages and category pages get real content |
| Excerpts (`<!-- more -->`) | all posts | Controls card text on the blog index |
| Featured latest post card | blog index | Needs the newest dummy post to be dated last |
| Series banner | posts 2 to 5 | `series`, `series_part`, `series_total` |
| Related posts + prev/next | all posts | Driven by category and tags; I will check the results make sense |
| Start-here page | posts 11, 12, plus one more | `start_here: true` (capped at 3) |
| Archive timeline | archive pages | Posts across 2023 to 2026 by month |
| Footer stat strip | all pages | Shows post count, last updated, series count |
| Inline newsletter form | all posts | Existing component |
| Copy as prompt / skill | posts 10, 11 | `{ .copy-prompt }` and `{ .copy-skill }` blocks |
| Share buttons | all posts | Existing hook |
| Code tabs, admonitions, tables | posts 7, 8, 9 | Existing Material features |
| RSS | feed | Dates and updates populate `feed_rss_created.xml` |

## 4. SEO and keyword targeting (what I would add)
- **Per-post front matter:** `title`, `description` (140 to 160 characters, includes the target keyword), `keywords`-style tags, a clean slug, `date.created` and `date.updated`.
- **One primary keyword per post**, plus 2 or 3 secondary ones, recorded in a comment block so you can see the targeting method.
- **Keyword cluster map** (pillar + supporting posts), for example "insurance data model" with posts 1 to 5 linking to each other and back to the pillar.
- **Heading structure:** one H1, descriptive H2s that carry secondary keywords, no skipped levels.
- **Meta tags:** a small template addition that outputs `meta description`, canonical URL, `article:published_time`, `article:modified_time`, and `article:tag` for each post.
- **Structured data:** JSON-LD `BlogPosting` (headline, dates, author, keywords, image) plus a `BreadcrumbList`, generated in a template from front matter. No JavaScript.
- **Sitemap:** already generated. I will check the dummy posts appear and that `start-here` and `showcase` are handled as you want.

## 5. Making the site useful to AI agents that index it
- **`llms.txt`:** a short file at the site root listing what the site is, the key sections and the best posts, in the emerging llms.txt format. Generated at build time from post summaries.
- **Per-post "Summary for agents" block:** a short, factual front-matter `summary` (2 to 3 sentences) plus `key_points` (3 to 5 bullets) and `prerequisites`. Rendered as a collapsed block on the page and included in the JSON-LD `abstract`.
- **Machine-readable post index:** `/blog/index.json` with title, URL, date, category, tags, summary, series and related links for each post.
- **Markdown source link:** each post gets a "View as Markdown" link to a raw `.md` copy, which is cleaner for agents than HTML.
- **Your existing `AGENT_INDEX.md`:** extend it to point at the blog index, `llms.txt` and the JSON feed.
- **`robots.txt`:** explicit allow rules, and a note on how to block dummy content if you ever want to.
- I will not invent claims about which crawlers use these. They are cheap, standard and low risk.

## 6. Interlinking
- Hand-written contextual links between posts (not just the auto "related" tiles), using MkDocs relative links so the build checks them.
- Series navigation, pillar-to-supporting links, and "if you liked this" links to the tutorial pages under `/learn/`.
- A link-check step in the verification so no dummy post has a dead internal link.
- Optional: a small "Where this fits" breadcrumb under the title for series posts.

## 7. Social cards
- The ledger social card layout already exists. I will check it renders for all 12 posts with long and short titles and fix overflow if any.
- Add per-post `description` to the card (the layout supports it) and a category label.
- Verify `og:` and `twitter:` tags point at the generated card, with a screenshot of each unique card shape.
- Note: cards are only built when the social plugin can run (needs Cairo). I will confirm this works in CI as well as locally and report if not.

## 8. Images
- **Hero images:** 12 simple, on-brand header images generated with the image tool (dark-green, ledger style, no text, no fake logos). About 12 small WebP or PNG files.
- **In-body figures:** 6 to 8 real charts reusing your existing launch-cadence images and a few generated from the SpaceX dataset with the existing scripts, with captions and alt text.
- **Rules:** every image has alt text; width and height are set to avoid layout shift; large files are optimised; lazy loading is on below the fold.
- Total added weight is capped at about 2 MB.

## 9. Small supporting changes
- A short `docs/blog-authoring-guide.md` (or a not-in-nav page) that shows the front-matter template and the keyword, summary and interlinking checklist. This is how "you can see how to do it".
- A post template file (`docs/blog/_template.md.example`) with every field commented.
- New tests: front-matter validation (required fields, description length, summary present, one H1), internal link check, and "no dummy posts on production".

## 10. Out of scope
Comments, search-result previews, analytics changes, any change to real tutorials or to non-blog page design.

## 11. Delivery and cost
- **Builder 1:** posts, authors, tags, images, interlinks (content).
- **Builder 2 (after Builder 1):** templates for meta tags, JSON-LD, `llms.txt`, JSON index, markdown links, social card fixes, tests.
- **Evaluator (different model):** build and test results, link check, validation of JSON-LD and `llms.txt`, screenshots of the blog index, a post, an archive, a category page, the start-here page and 3 social cards, saved in `docs/visual-check/dummy-blog/`.
- Estimate: about $4 to $6 of your remaining credit. If you want it leaner, drop section 5's JSON index and markdown links first (saves about $1), and use 6 posts instead of 12 (saves about $1 to $2).

## 12. Decisions needed from you
1. Approve the 12 posts, or a smaller set (6)?
2. Should AI-generated hero images be used, or text-only cards and no images?
3. Keep `/start-here/` and `/showcase/` out of the sitemap, or include them?
4. OK to add the "no dummy posts on production" CI check?
5. OK for authors to be fictional?
