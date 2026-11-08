---
date: {created: 2024-04-11, updated: 2024-04-11}
categories: [Data Engineering]
tags: [insurance-data, python, sqlmodel, validation]
slug: sqlmodel-policy-table
description: "Build a SQLModel policy table from CSV without losing validation or currency meaning. Separate input checks, database constraints and safe batch writes."
keywords: [SQLModel policy table, CSV import, database constraints]
summary: "This sample separates CSV input validation from a SQLModel storage table. It explains transaction boundaries, duplicate handling and reconciliation after persistence."
key_points:
  - Validate CSV rows before constructing table objects
  - Define duplicate handling before importing
  - Reconcile persisted amounts by currency
prerequisites: [Basic Python, SQLModel and Pydantic]
image: assets/images/blog/sqlmodel-policy-table.webp
dummy: true
authors: [sample-rowan]
series: Insurance data models
series_part: 2
series_total: 4
---
# SQLModel: from CSV to policy table
<!--
Primary: SQLModel policy table
Secondary: CSV import; database constraints
Intent: distinguish the input contract from persistence.
-->

!!! warning "Sample post"
    This is a demo post by a fictional sample author. Identifiers, amounts and import scenarios are synthetic.

A SQLModel policy table gives a validated CSV somewhere durable to live. The import still needs decisions about duplicate identifiers, transaction boundaries and currency. Putting a Python class next to a database does not settle those questions automatically.

<!-- more -->

![Aligned green ledger panels representing persisted records](../../assets/images/blog/sqlmodel-policy-table.webp){ width="1200" height="630" }

## Give CSV import a defined boundary

Begin with the input model from [part one](dummy-pydantic-actuaries.md). Read a source row, map its headers and validate it explicitly with `model_validate`. Keep the source row number outside the business model so a rejection can be traced back to the original file.

Use a separate table class for storage. This makes it easier to distinguish source restrictions from database requirements. A generated database identifier, for example, is not something a supplier should have to invent.

```python
from decimal import Decimal
from sqlmodel import Field, SQLModel

class PolicyRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    policy_id: str = Field(index=True, unique=True)
    currency: str
    premium_oc: Decimal = Field(
        max_digits=18, decimal_places=2
    )
```

This teaching table assumes one current row per policy. A historical table would need a different key, perhaps including a version or valuation date. Changing the grain later can be expensive, so write that assumption beside the model.

## Understand database constraints

The unique constraint prevents a second row with the same `policy_id`; it does not decide whether a corrected policy should replace an earlier version. Choose whether duplicate input is an error, a replay or a new version before implementing the import.

A database column type is also not a substitute for validating source values. Validate the incoming dictionary first and construct `PolicyRow` only from accepted fields. Check the database's behaviour for decimal precision, especially when using SQLite for teaching and another database in production.

The [existing policy tutorial](../../learn/spacex/creating_policies.md) shows `select(Policy)` and session-based queries. Use that pattern to read back the rows after writing them, rather than trusting a log message saying the import finished.

## Commit a batch deliberately

For a small file, an all-or-nothing transaction is straightforward: validate the complete batch, insert it inside a session and commit only if the checks pass. If a uniqueness error occurs, roll back the transaction and report the conflicting key safely.

A larger feed may require chunks. Record which chunks committed and how a retry avoids inserting them twice. A source checksum plus a batch identifier helps distinguish an identical replay from a corrected file delivered under the same name.

## Reconcile the stored result

Compare accepted row counts with persisted row counts, and compare premium totals within each currency. Query using a fresh session so the check observes committed data. Keep the reconciliation with the run record, including the schema version.

Continue to [claims-feed validation](dummy-claims-feed-validation.md) for checks that span several rows. The [reserving-data pillar](dummy-reserving-data.md) explains why matching counts alone cannot prove the grain or monetary basis is correct.
