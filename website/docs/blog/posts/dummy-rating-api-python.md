---
date: {created: 2025-08-14, updated: 2025-08-14}
categories: [APIs]
tags: [apis, python, validation, testing]
slug: rating-api-python
description: "Calling a rating API from Python requires clear timeouts, response validation and safe retry rules. Practise request handling with an offline response first."
keywords: [rating API from Python, response validation, API retries]
summary: "This sample outlines a Python rating API client boundary without contacting a real rating service. It covers offline response checks, timeout choices and the risks of retrying writes."
key_points:
  - Validate the response beyond its status code
  - Set explicit timeouts
  - Retry only when the operation's semantics allow it
prerequisites: [Basic Python, Familiarity with HTTP]
image: assets/images/blog/rating-api-python.webp
dummy: true
authors: [sample-rowan]
---
# Calling a rating API from Python
<!--
Primary: rating API from Python
Secondary: response validation; API retries
Intent: teach the client boundary without inventing a vendor integration.
-->

!!! warning "Sample post"
    This is a demo post by a fictional sample author. No real rating service is called and no insurance price is recommended.

Calling a rating API from Python is partly an HTTP task and partly a contract task. A successful status code tells you the server accepted the request at that level. It does not prove the returned currency, rating version or premium matches what the caller expected.

<!-- more -->

![Two geometric ledger blocks linked by fine routing lines](../../assets/images/blog/rating-api-python.webp){ width="1200" height="630" }

## Practise response validation offline

Begin with a local dictionary and a narrow response model. The currency restriction below belongs to the synthetic example, not to an external API specification. A real integration should follow the provider's documented schema and monetary precision rules.

=== "Response model"

    ```python
    from decimal import Decimal
    from typing import Literal
    from pydantic import BaseModel, ConfigDict, Field

    class QuoteResponse(BaseModel):
        model_config = ConfigDict(extra="forbid")
        quote_id: str = Field(min_length=1)
        currency: Literal["USD"]
        premium: Decimal = Field(ge=0)
        rating_version: str = Field(min_length=1)
    ```

=== "Offline fixture"

    ```python
    payload = {
        "quote_id": "SAMPLE-Q1",
        "currency": "USD",
        "premium": "420.00",
        "rating_version": "demo-1",
    }
    # Use with QuoteResponse from the other tab.
    result = QuoteResponse.model_validate(payload)
    assert str(result.premium) == "420.00"
    ```

The tabs are complementary snippets, not two independent programs. Add tests for a missing quote identifier, an unexpected currency and malformed JSON at the transport boundary.

The [SpaceX API tutorial](../../learn/data/spacex.md) is useful practice with real external payloads. Its nullable fields illustrate why a dictionary lookup can fail even after a valid JSON response.

## Set timeouts before API retries

For a `requests` client, pass an explicit connect/read timeout tuple such as `timeout=(3.05, 20)`. Those illustrative values are not a complete wall-clock deadline: retries and multiple reads can extend total execution time. Set the overall job budget separately.

| Result | Possible response | Required decision |
| --- | --- | --- |
| Authentication failure | Stop and report safely | Which credential owner responds? |
| Invalid request | Surface the validation error | Can the caller correct input? |
| Rate limit | Respect documented backoff | What is the retry budget? |
| Read timeout after POST | Check operation status | Could a quote already exist? |

!!! warning "An ambiguous write may have succeeded"
    Do not automatically resend a quote-creation request after a timeout. Use a provider-supported idempotency key or status lookup, with the provider's documented guarantees.

## Keep secrets outside the example

Load credentials from the approved secret store or runtime environment. Avoid printing authorization headers or entire request bodies in ordinary logs. Insurance requests may contain personal information, so choose diagnostic fields deliberately.

Record the request identifier, response identifier and rating version where permitted. These support later investigation without requiring unrestricted access to the full payload.

## Test the contract before the network

Mock the transport in unit tests and keep a small set of synthetic fixtures. Add a separate, explicitly enabled integration test only when a real sandbox is available. That separation keeps routine tests deterministic and avoids accidentally creating quotes during development.

Use the [Pydantic input-model sample](dummy-pydantic-actuaries.md) for the validation pattern, and the [pipeline finale](dummy-repeatable-pipeline.md) for replay handling when API requests become part of a larger delivery.
