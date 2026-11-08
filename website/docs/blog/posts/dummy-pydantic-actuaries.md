---
date: {created: 2024-01-18, updated: 2024-03-04}
categories: [Data Engineering]
tags: [insurance-data, python, pydantic, validation]
slug: pydantic-actuaries
description: "Pydantic for actuaries starts with a small policy input model. Learn where validation helps, what coercion means and which business rules need more care."
keywords: [Pydantic for actuaries, policy input model, schema validation]
summary: "This sample introduces a Pydantic policy input model with a currency constraint and decimal premium. It distinguishes schema validation from business approval and describes rejection handling."
key_points:
  - Validate incoming rows before storage
  - Make conversion rules explicit
  - Keep rejected records for review
prerequisites: [Basic Python, Pydantic version 2]
image: assets/images/blog/pydantic-actuaries.webp
dummy: true
authors: [sample-rowan]
series: Insurance data models
series_part: 1
series_total: 4
---
# Pydantic for actuaries: first model
<!--
Primary: Pydantic for actuaries
Secondary: policy input model; schema validation
Intent: introduce a small executable contract.
-->

!!! warning "Sample post"
    This is a demo post by a fictional sample author. The policy records and rules are synthetic teaching examples.

A CSV reader gives you strings, even when a column is meant to contain a premium. Pydantic for actuaries is useful at that boundary: it can turn agreed field rules into a repeatable check, while leaving business decisions visible for someone to review.

<!-- more -->

![Hatched green cells arranged around a schema boundary](../../assets/images/blog/pydantic-actuaries.webp){ width="1200" height="630" }

## Define a policy input model

Start with a handful of fields and explain each restriction. This example accepts only two currencies and non-negative premiums because the teaching dataset has that scope. A production model may need return premiums, more currencies and separate transaction types.

```python
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class PolicyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy_id: str = Field(min_length=1)
    currency: Literal["USD", "AUD"]
    premium_oc: Decimal = Field(ge=0)

row = PolicyInput.model_validate({
    "policy_id": "DEMO-001",
    "currency": "USD",
    "premium_oc": "1250.50",
})
assert row.premium_oc == Decimal("1250.50")
```

`extra="forbid"` makes an unexpected field visible instead of ignoring it. That is helpful when a supplier changes a column name, although you still need an explicit mapping from source headers to model fields.

## Know what schema validation accepts

The premium string becomes a `Decimal`. This conversion is deliberate: CSV values normally arrive as text. Strict validation can be useful elsewhere, but applying it blindly to CSV input may reject every numeric field before you have defined how parsing should work.

Decimal arithmetic avoids binary floating-point representation for this amount. It does not decide when rounding occurs, which rounding mode applies or how many decimal places each output requires.

Keep the original currency with the amount. The [policy-query tutorial](../../learn/spacex/creating_policies.md) uses `premium_oc` and `currency` together, which is a useful convention to retain in your own teaching model.

An empty identifier also deserves more care than the first model provides. A string of spaces satisfies a minimum length. Add normalisation or a validator once the contract says whether trimming is allowed, and preserve the raw row so any change can be explained.

## Keep rejected rows available

Catch `ValidationError` at the batch boundary and record the source row number plus error location and reason. In a real claims feed, avoid copying personal information into an unrestricted error log. Keep detailed rejects in a controlled location and publish aggregate counts separately.

Test a valid row, a missing currency, an unsupported currency and a negative premium. Add a whitespace identifier case before calling the model complete. Each expected failure documents a decision someone can challenge.

## Continue into storage

The next part, [SQLModel: from CSV to policy table](dummy-sqlmodel-policy-table.md), adds persistence without dropping the input boundary. Return to [the reserving-data pillar](dummy-reserving-data.md) if the grain or valuation-date assumptions are still unclear; a typed field cannot repair an ambiguous row definition.

For another example of validating external records, follow the [SpaceX data tutorial](../../learn/data/spacex.md). Its nullable nested objects are a useful reminder that a missing object and an object with an empty field require different handling.
