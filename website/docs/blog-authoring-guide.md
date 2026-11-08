---
title: Blog authoring guide
description: Front matter, keyword targeting, agent summaries, and checks for publishing a blog post.
---

# Blog authoring guide

Create a Markdown file in `website/docs/blog/posts/`. The build derives its public URL from the creation date and slug. Keep this guide outside navigation and search-engine indexes.

## Front matter template

```yaml
---
title: "A specific title"                      # Matches the single H1 below
date:
  created: 2026-11-08                         # First publication date
  updated: 2026-11-08                         # Last substantive revision
categories: [Data Engineering]               # One allowed category; see below
tags: [validation, insurance]                 # Existing topic labels where possible
slug: a-specific-title                        # Stable kebab-case public slug
description: >-                              # Aim for 140-160 characters; include primary keyword
  Insurance data validation checks for policy and claims feeds, with practical examples of schema rules, exception handling, and repeatable reporting.
keywords:                                    # First keyword is the primary target
  - insurance data validation
  - policy schema
  - claims feeds
summary: >-                                  # Two or three factual sentences for agents
  This post defines validation rules for policy and claims feeds.
  It explains which errors to reject and which to report for review.
key_points:                                  # Three to five concrete takeaways
  - Validate types before aggregating records.
  - Record rejected rows with a reason.
  - Separate schema checks from business rules.
prerequisites:                               # Zero to three; use [] when none
  - Basic Python and tabular data knowledge
image: assets/images/blog/a-specific-title.webp # Hero path relative to docs/
dummy: true                                  # Samples only; production rejects true
authors: [sample-author]                      # Must exist in blog/.authors.yml
series: Insurance data pipelines              # Optional shared series name
series_part: 1                               # Optional integer sequence
series_total: 4                              # Optional total number of parts
start_here: false                            # Optional curated starting-point flag
---

# A specific title

!!! note "Sample post"
    This is demonstration content, not a report of real project results.

Opening paragraph with the primary keyword.

<!-- more -->

## A useful subheading

Post body with descriptive links to related posts and relevant tutorials.
```

Allowed categories: Data Engineering, Analytics, APIs, Actuarial, AI Agents.

## Before publishing

- Give the post one primary keyword and at least one secondary keyword. Use the primary naturally in the title, description, and opening.
- Write a factual summary of two or three sentences, with three to five key points. Avoid invented results or claims.
- Include exactly one H1 in the Markdown body. Put secondary keywords in headings only where they describe the section.
- Link supporting posts back to their pillar and to relevant tutorials using relative Markdown paths. Check image paths and alt text.
- Add the hero image and an author entry before building. Keep `dummy: true` and the visible sample admonition on demo content.
- Run `uv run pytest -q` and `uv run mkdocs build --strict -f website/mkdocs.yml`.

The build publishes a collapsed agent summary, structured data, raw Markdown, `/llms.txt`, and `/blog/index.json`. Sample posts remain in these resources with explicit labels.

## Remove the demo content

Delete `website/docs/blog/posts/dummy-*.md`, then remove their unused hero images and sample author entries. Check for links from retained posts to deleted samples. Do not turn fictional posts into production content by changing only their flag.

Run `uv run python scripts/check_no_dummy_posts.py` before merging to `master`. The production workflow runs the same guard; local builds and develop/UAT allow samples.
