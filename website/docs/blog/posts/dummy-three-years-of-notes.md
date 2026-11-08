---
date: {created: 2026-11-06, updated: 2026-11-07}
categories: [Analytics]
tags: [communication, insurance-data, data-quality, ai-agents]
slug: three-years-of-notes
description: "These insurance analytics notes connect data contracts, charts and bounded AI tasks. Use the sample reading map to choose a practical place to start next."
keywords: [insurance analytics notes, data contracts, bounded AI tasks]
summary: "This fictional retrospective links the sample site's data-model series, chart examples and agent prompts. It offers a reading map based on whether the reader needs definitions, presentation or review support."
key_points:
  - Start with row meaning and monetary definitions
  - Match chart design to a specific comparison
  - Bound agent tasks and verify their evidence
prerequisites: []
image: assets/images/blog/three-years-of-notes.webp
dummy: true
authors: [sample-tess]
start_here: true
---
# 3 years of notes: what I'd tell myself
<!--
Primary: insurance analytics notes
Secondary: data contracts; bounded AI tasks
Intent: make a newcomer-friendly reading map across the sample collection.
-->

!!! warning "Sample post"
    This is a demo post by a fictional sample author. The retrospective framing and publication history are invented to demonstrate the blog; no three-year work record is claimed.

These insurance analytics notes share a recurring practical question: what would another person need to check the result? The answer changes between a policy import, a chart and an agent review. This sample retrospective groups the posts by those needs so a new reader can choose a starting point without reading the entire archive.

<!-- more -->

![Interconnected mint ledger cells arranged like an archive](../../assets/images/blog/three-years-of-notes.webp){ width="1200" height="630" }

## Start with data contracts when meaning is uncertain

[Why your reserving data keeps breaking](dummy-reserving-data.md) begins with row grain, valuation dates and currency. Read it before deciding whether a missing field is a code problem or an unresolved definition. A database can preserve an ambiguous record perfectly well.

The four-part series turns those definitions into a small delivery. [Pydantic for actuaries](dummy-pydantic-actuaries.md) handles the input boundary. [SQLModel policy tables](dummy-sqlmodel-policy-table.md) add persistence, while [claims-feed validation](dummy-claims-feed-validation.md) checks relationships across rows. [Shipping the model](dummy-repeatable-pipeline.md) covers replay and publication.

Keep the examples' limits visible. A non-negative premium rule belongs to the narrow teaching dataset; it is not a universal rule for insurance transactions. The useful habit is to attach each restriction to its documented purpose and test it with an exception case.

## Choose a comparison before a display

[Choosing a chart your CFO will read](dummy-cfo-chart.md) uses existing launch-cadence figures to show a before-and-after composition. It asks the reader to separate a visible movement from an explanation of that movement. Styling cannot supply evidence for causation.

The [loss-ratio dashboard sample](dummy-loss-ratio-dash.md) moves the same discipline into an interface. Filters must select a consistent population for both numerator and denominator. A percentage without its supporting amounts is difficult to reconcile when a selection changes.

For a hands-on visual reference, visit the [launch-cadence tutorial](../../learn/spacex/launch_cadence.md). Its subject is launch counts, so avoid treating those figures as evidence about financial performance.

## Keep external boundaries explicit

The [rating-API sample](dummy-rating-api-python.md) starts offline and separates response validation from transport success. Read it when a successful HTTP request is being mistaken for a verified business result. A timed-out write also needs special care because the remote operation may already have completed.

[Cat modelling inputs](dummy-cat-modelling-inputs.md) covers a different boundary: physical exposure fields and financial terms. Location precision and mapping choices belong in the evidence report, even when an output table presents numbers to several decimal places.

The [SpaceX data tutorial](../../learn/data/spacex.md) gives a concrete external-data exercise. The [policy-query tutorial](../../learn/spacex/creating_policies.md) then offers a small database example using sessions and select statements.

## Use bounded AI tasks for review support

The [profiling-agent article](dummy-data-profiling-agent.md) asks for reproducible counts on synthetic data and keeps repairs outside the first task. [Prompts that earned their keep](dummy-useful-prompts.md) adds review prompts for schemas, charts and handovers. Both require the reader to verify the evidence and enforce permissions outside the prompt.

Choose one exercise and a tiny synthetic fixture. Write the expected result before running it, including one case that should fail. Save the input version and the observed result together. That gives the next person a concrete starting point when a field, chart or operating procedure changes.
