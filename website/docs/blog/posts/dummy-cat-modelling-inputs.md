---
date: {created: 2025-11-20, updated: 2026-02-12}
categories: [Actuarial]
tags: [catastrophe, insurance-data, data-quality, validation]
slug: cat-modelling-inputs
description: "Cat modelling inputs need clear location, value and financial-term definitions. Review exposure quality before interpreting modelled losses or comparisons."
keywords: [cat modelling inputs, exposure data quality, financial terms]
summary: "This sample introduces common exposure fields and distinguishes physical characteristics from financial terms. It provides a compact glossary and a review process without estimating catastrophe losses."
key_points:
  - Keep physical exposure and financial terms distinct
  - Preserve uncertainty in location and construction fields
  - Reconcile values before comparing model outputs
prerequisites: []
image: assets/images/blog/cat-modelling-inputs.webp
dummy: true
authors: [sample-ellis]
---
# Cat modelling inputs, explained simply
<!--
Primary: cat modelling inputs
Secondary: exposure data quality; financial terms
Intent: introduce an input-review vocabulary without making loss estimates.
-->

!!! warning "Sample post"
    This is a demo post by a fictional sample author. It is an introductory data example, not catastrophe-modelling or underwriting advice.

Cat modelling inputs describe what is exposed, where it is and how insurance terms apply. A model can produce a precise-looking output from uncertain input fields. Reviewing those fields first makes it easier to explain which parts of a comparison reflect exposure changes and which remain uncertain.

<!-- more -->

![Layered green geometric cells suggesting exposure information](../../assets/images/blog/cat-modelling-inputs.webp){ width="1200" height="630" }

## Review exposure data quality

Start with identifiers and the location hierarchy. A policy may cover several sites, and a site may contain several buildings. Decide which level each row represents before joining values or applying terms. Repeated policy limits on building rows can otherwise look like separate available limits.

| Field group | Example question | Preserve alongside the value |
| --- | --- | --- |
| Location | Which coordinate system is used? | Geocoding source and precision |
| Insured values | What property components are included? | Currency and valuation date |
| Construction | Which coding scheme applies? | Original code and mapping version |
| Financial terms | At which level does the limit apply? | Scope and currency |

An unknown construction code should remain distinguishable from a known code. Mapping every unknown to the most common category hides uncertainty and can change the interpretation of later comparisons.

<figure markdown>
![Abstract layers of input blocks with a separate exception path](../../assets/images/blog/exposure-layers.webp){ loading=lazy width="1200" height="630" }
<figcaption>Conceptual input layers, not a hazard map or model result. Each layer needs its own definitions and checks.</figcaption>
</figure>

## Separate financial terms from physical fields

=== "Physical exposure"

    Record location, occupancy, construction and the values attached to the defined row. Missing information should have an explicit status rather than an invented replacement presented as observed data.

=== "Financial structure"

    Record deductibles, limits and their application level. A policy-level limit and a location-level limit need different treatment even when the numeric values happen to match.

!!! warning "Check the model's documented conventions"
    Field names alone do not establish meaning. Confirm units, codes and term application against the documentation for the actual model and import format.

The [policy tutorial](../../learn/spacex/creating_policies.md) offers a small starting point for querying policy fields. It does not implement a catastrophe financial module, so keep any extension clearly separated from that teaching example.

## A compact input glossary

### Exposure

The assets or interests being described. An exposure table should state its row grain and the scope of the insured values it contains. See [exposure review](#review-exposure-data-quality) for the fields to check first.

### Geocoding precision

How specifically a location has been resolved. A postcode centroid and a building coordinate can both be numeric latitude and longitude while carrying different uncertainty.

### Deductible and limit

Contractual terms affecting the insured share of a loss. Their effect depends on wording, scope and application order; the [financial-terms section](#separate-financial-terms-from-physical-fields) explains why a flat amount is insufficient documentation.

## Reconcile before comparing results

Compare location counts and insured values within currency between deliveries. Explain additions, removals and mapping changes separately. Keep a report of unresolved fields so a reviewer can see whether an apparent change in output coincides with a change in input quality.

The [reserving-data pillar](dummy-reserving-data.md) uses the same grain-and-reconciliation discipline. For automated review, the [data-profiling agent sample](dummy-data-profiling-agent.md) proposes an evidence report while keeping decisions about uncertain exposure fields with a human owner.
