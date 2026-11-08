---
date: {created: 2023-11-16, updated: 2024-02-08}
categories: [Data Engineering]
tags: [insurance-data, data-quality, validation, pipelines]
slug: reserving-data
description: "Reserving data breaks when row meaning, dates and currencies drift. Build a small insurance data contract and checks that make monthly changes visible."
keywords: [reserving data, insurance data contract, monthly reconciliation]
summary: "This sample explains how row grain, valuation dates and currency definitions affect reserving extracts. It outlines a data contract and a reconciliation process for monthly deliveries."
key_points:
  - Define the grain before joining tables
  - Preserve source values and valuation dates
  - Reconcile both counts and amounts
prerequisites: [Familiarity with a monthly insurance extract]
image: assets/images/blog/reserving-data.webp
dummy: true
authors: [sample-rowan]
start_here: true
---
# Why your reserving data keeps breaking
<!--
Primary: reserving data
Secondary: insurance data contract; monthly reconciliation
Intent: connect schema validation to repeatable delivery.
-->

!!! warning "Sample post"
    This is a demo post by a fictional sample author. Examples are illustrative, not reports of work for an insurer.

A monthly claims file can have the same columns as last month and still mean something different. Perhaps one row now represents a payment instead of a claim, or the outstanding amount includes expenses that were previously separate. Reserving data needs a written definition of those choices before a successful import tells you much.

<!-- more -->

![Mint ledger rows separating into consistent columns](../../assets/images/blog/reserving-data.webp){ width="1200" height="630" }

## Start with an insurance data contract

Write one sentence describing the row. For example: "One claim snapshot per claim identifier and valuation date, in original currency." That sentence rules out several unsafe joins. Joining payment transactions directly onto that snapshot can repeat the outstanding balance once for every payment.

Keep transaction and snapshot tables separate until you have aggregated them to a compatible grain. Record whether identifiers are unique globally or only within a source system. A policy number that looks unique in a small sample may repeat after a portfolio acquisition.

For each monetary field, record currency, sign convention and whether expenses are included. A blank outstanding balance is not automatically zero. It may mean the source could not supply the value, which needs a different response from a genuinely closed claim.

The [SpaceX data tutorial](../../learn/data/spacex.md) demonstrates a related problem with a nullable mission object. The subject differs, but the boundary is the same: external data must satisfy a documented shape before downstream analysis can rely on it.

## Make monthly reconciliation explicit

Compare counts at the agreed grain, then compare amounts within currency. A total across USD and AUD does not become meaningful because both columns contain numbers. If you convert currency, retain the original amount and identify the exchange-rate basis used for the converted view.

Save the source filename, extraction time and valuation date alongside each run. These dates answer different questions. An extract taken on Tuesday can describe a month-end position, and a late correction may change that position without changing the valuation date.

A useful reconciliation report shows source rows, accepted rows, rejected rows and duplicate keys. Explain each difference. Do not let the process discard invalid records and then compare only the surviving totals.

## Build the smallest useful model

The four-part series starts with [Pydantic for actuaries](dummy-pydantic-actuaries.md), which makes field rules executable. It then puts accepted rows into a [SQLModel policy table](dummy-sqlmodel-policy-table.md), adds [claims-feed validation](dummy-claims-feed-validation.md), and packages the steps into a [repeatable pipeline](dummy-repeatable-pipeline.md).

Keep the first version narrow. One source, one valuation date and a few named checks are enough to expose uncertain definitions. Ask the person who owns the extract to approve those definitions before generalising them across products.

## Leave evidence for the next month

Store a tiny, synthetic fixture with a duplicate identifier, a missing currency and a valid correction. Run it whenever the mapping changes. Include expected rejection reasons so a future maintainer can distinguish an intentional rule change from a regression.

The handover should say who can approve an exception and where that decision is recorded. A manual override without an owner can quietly become the rule for every later month. Keep the exception beside the run report, with an expiry or a review date.
