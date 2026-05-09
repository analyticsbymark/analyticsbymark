# SpaceX

Let's say you've just received some data. You're about to get stuck into your analysis.
You start doing some sense checks on the data and _"Oh, no!"_ :exploding_head:

The data isn't in the same format as last time. The column names have changed, or the
format of a column is different.

Here is what that looks like in practice. A quick script — nothing fancy, just pull the
data and print a few fields:

```python
import requests

response = requests.get(
    "https://ll.thespacedevs.com/2.3.0/launches/",
    params={"lsp__id": 121, "limit": 100}
)

launches = response.json()["results"]

for launch in launches:
    name    = launch["name"]
    rocket  = launch["rocket"]["configuration"]["families"][0]["name"]  
    mission = launch["mission"]["name"]                                 
    net     = launch["net"]                                             
    print(f"{name} | {rocket} | {mission} | {net}")
```

For most records this works. Then it hits one launch where `mission` is `null` in the API
response, and everything stops:

```
Falcon 9 Block 5 | Starlink Group 6-14 | Falcon | Starlink | 2024-01-14T11:00:00Z
Falcon 9 Block 5 | Starlink Group 6-15 | Falcon | Starlink | 2024-01-18T06:00:00Z
Falcon 9 Block 5 | Starlink Group 6-16 | Falcon | Starlink | 2024-01-30T00:00:00Z

Traceback (most recent call last):
  File "fragile.py", line 13, in <module>
    mission = launch["mission"]["name"]
              ~~~~~~~~~~~~~~~~~^^^^^^^^
TypeError: 'NoneType' object is not subscriptable
```

It just takes that one bad one to ruin your script and your left with an empty output.

This is not an edge case — it is what happens when you work with data, particularly with a real API.

Missions get added late. Fields go missing. A date that was a proper timestamp last
month comes back as an empty string today.

!!! warning "Watch out for silent errors, they're the :material-emoticon-devil:{ .red-icon }"
    Sometimes the script does not crash — it just silently writes wrong data.
    `net` can come back as an empty string `""` instead of a datetime. If you convert
    it later in your BI tool, you get nulls in your time series and nobody notices
    until a chart breaks and another colleague comes running.

In this tutorial you will build a flow which validates every record, meets a data contract, gracefully handles missing values 
and outputs a table which is analytics ready (CSV or via a database).

You will become the one known in your company as the one who builds :fire: datasets :sunglasses:

!!! tip

    If you'd rather skip the API and go straight into using the data you can download a working CSV file
    [here](spacex_launches.csv){:download}. **_Note_** this is a static dataset and not updated for live 
    launches.

## Overview

In this dataset we extract launches for SpaceX :simple-spacex:. 

You will learn how to:

1. Build a repeatable pattern for data pipeline that doesn't break when the source changes
2. Validate incoming data against a defined schema so bad records don't appear in your data
3. Export a clean, analysis-ready CSV that anyone on your team can use immediately
4. **Bonus:** Create a queryable database from the same validated data


## Sample rows

<div class="data-table" markdown>
{{ read_csv("spacex_launches.csv", nrows=2) }}
</div>


The code is structured into **_5_** parts:

1. Imports + meta data (api url, spaceX id and save location)
2. Table schema, here we use `SQLModel` which wraps `Pydantic` to create the outline of our table
3. Helper functions which handle navigating API calls & data coming back
4. Mapping data returned by the API into our table schema and creating a data contract to ensure valid data
5. A `get_spacex_data()` function which orchestrates the extraction

!!! warning "What happens without validation"
    Without a schema and validation step, poor quality data can slip into your table silently. You only discover it weeks later 
    when a dashboard breaks, numbers don't add up or someone asks you why the format has changed. You're back to firefighting 
    instead of working on the fun stuff.

## Before you start

During the tutorial I highlight lines of interest and added them as annotations within code blocks. You can use them to learn what a 
particular line of code does.

!!! tip "How to use the annotations"                                                                                                                                                                               
      Click the **plus button** in the code blocks to toggle explanations on and off.                                                                                                                            
                                                                                                                                                                                                                     
      ```py                                                                                                                                                                                                          
      x = safe_get(data, "key") # (1)!                                                                                                                                                                               
      ```                                                                                                                                                                                                            

      1. Click here — this is an annotation!


## 1. Imports + Meta Data


??? info ":detective: which section is this creating?"
    
    ```py {.annotate hl_lines="22-35"}
    --8<-- "spacex_clean.py:18:212"
    ```


```py {.annotate}
--8<-- "docs_src/space_dev/modelling/spacex/spacex.py:22:35"

# Code omitted 👇

```

--8<-- "docs_src/space_dev/modelling/spacex/annotations/spacex.md"

We start with our regular python imports and create variables for `API_URL`(1), `SPACEX_LSP_ID` and `OUTPUT_CSV`.
{ .annotate }

[Python coding conventions](https://peps.python.org/pep-0008/#constants){target="_blank"} suggest constants should be defined in `BLOCK_CAPS` 


## 2. How do you model data using Python :man_shrugging_tone2:

We are using [`SQLModel`](https://sqlmodel.tiangolo.com/) to define what our table looks like. 

??? tip "Using SQLModel"

    I highly rate using SQLModel as it interacts with APIs / databases seamlessly and has brilliant 
    out the box data validation as it wraps ['Pydantic'](https://docs.pydantic.dev/latest/).

    I would not do SQLModel training justice, so to learn from the pro who made it - take a tutorial [here](https://sqlmodel.tiangolo.com/tutorial/).
    Just as an FYI the same chap made FastAPI too :nerd:.

```py {.annotate}
# Code omitted ☝️

--8<-- "docs_src/space_dev/modelling/spacex/spacex.py:47:103"

# Code omitted 👇
```

--8<-- "docs_src/space_dev/modelling/spacex/annotations/spacex.md"

!!! tip "Tip" 

    Think of this as designing a bordereaux or claims extract template - you decide what columns exist what types they accept before
    any data arrives

??? Question "Why `str | None = None`?"
    Why do we include both the expected data type or None and default to None? Well - the API might 
    return both and we don't want our script to crash over missing data.


In this table, we define columns into the following groups:

### 2.1. **_Identity_**

These answer the questions _which launch is this?_ and _where can I find its full record?_

- `launch_uuid` the uuid is the unique identifier assigned by the launch api for that particular launch, and 
- `launch_url` -The url is what you can call to retrieve the full JSON dataset for that one launch. 

### 2.2 **_Timing_**

This captures when things happen, or rather when they were supposed to happen.

- `net` ("No Earlier Than") - _NET_ is often used in the space industry because launch dates frequently slip. 
- `window_start` and `window_end` - define the range in which conditions allow the rocket to launch. 
- `last_updated` - is useful for data quality, it details when the record was last changed.

### 2.3 **_Launch Info_**

This section captures _what happened_ with the launch itself:

 - `launch_name` - this is the only **required field**. Data is not correct if it comes back without a launch name. 
 - `launch_status` - is the full text _"Launch Successful"_ or _"Launch Failure"_
 - `launch_status_id` - is the numerical version of the above. Useful for filtering or sorting programatically
 - `launch_status_abbrev` - is the short code for e.g. _"Success"_ or "Failure". Easier to use in analytics than the full `launch_status`
 - `launch_status_description` - a longer description of what the `launch_status` means

### 2.4 **_Operator Info_** 

This section tells you _who_ launched the rocket

- `operator_id` is SpaceX's numeric ID in the Launch Library API (always **121** for this dataset).
- `operator_name` is the human readable equivalent (always **"SpaceX"** for this dataset). This is good for chart labels, titles and display

!!! Info "Why include these if they are always the same?"
     
    There are a few reasons why, even though the `operator_id` and `operator_name` are the same for each row 
    that they should be included in the dataset.

    1. This script can be adapted to pull & union data from different operators to do comparisons. If the operator 
    fields are already there, the data model does not need to change, just the `SPACEX_LSP_ID`. 
     
    2. If someone looks at this dataset without any context, they can immediately see who the operator is without
    needing to know which filter was applied.

### 2.5 **_Mission Info_**

This section tells you what the _launch_ was trying to accomplish

 - `mission_id` - is the API's numerical identifier for the mission with the same idea as `operator_id`
 - `mission_name` - is what the mission was called
 - `mission_type` - this is a grouping for types of mission, e.g. **"Communications"**, **"Resupply** or **"Navigation"**
 - `mission_description` - this is a free-text summary for the mission's purpose and valuable for context

??? tip "Missing Mission Data"

    Why are these fields Optional? Some launches in the API do not have a mission attached to them yet. This may be because it's a future launch and has not yet 
    been fully announced, or it is a historical record with incomplete data.

    Rather than losing the whole record over a few missing mission descriptions the data model accepts `None` as the default value 
    in these instances and moves on. 

    It is a good example of real world API's having gaps in the data that need to be handled gracefully.


### 2.5. _**Mission Owners**_ 

This section tells you _who is paying_ for the mission

- `mission_owner_primary_id` - is a numerical ID of the main organisation sponsoring the mission
- `mission_owner_primary_name` - is the readable name of the primary owner, e.g. `"NASA"` or `"European Space Agency"`
- `mission_owner_all_ids` - is a semicolon-delimited string like `"44;161"` containing every organisation 
   involved in the mission. Some missions have multiple sponsors, e.g. a NASA mission might also involve the US Space Force
- `mission_owner_all_names` - is the same as above but with names instead of IDs, e.g. `"NASA;USAF"`

??? Example "Where are the mission owners?"

    This data set does not provide a `mission_owner` field as default - we have to use a bit of API wizardry :material-wizard-hat:{ .purple-icon }
    (aka looking at the data returned) to extract it.

    The Launch API returns agency data in two places `mission.agencies` and `program.agencies`. We later see how we look at 
    both fields to return owners.

    When working with APIs it is good to assume that data can come from `multiple` places, it is worth `exploring` in detail 
    before building your data model and make sure to consider `deduplication` as, in this case, agencies can be the same
    in different parts of the API.

### 2.6. _**Programs**_ 

This section captures the high level _program_ a launch belongs to, e.g. `Starlink`, `Commercial Crew` or 
`International Space Station`.

- `program_names` - Think of this as the campaign a launch is part of. A launch can have multiple programs. 

### 2.7. _**Media**_ 

This section contains image urls for launches

- `image_thumbnail` - is a URL to a small preview of the launch - typically a photo of the rocked on the pad or during flight

### 2.8. _**Rocket**_ 

This section tells you what _flew_

- `rocket_full_name` is the complete identifier like `"Falcon 9 Block 5"`. This is the most descriptive - includes the rocket family, name, and variant all in one string. Good for display or labelling
- `rocket_variant` is the specific version, like `"Block 5"`. SpaceX iterates on their rockets - Block 5 is the current, most-reused version of the Falcon 9. Useful if you want to compare performance across variants.
- `rocket_name` is the base name without the variant - just `"Falcon 9"`. Handy for high level groupings such as how many Falcon 9 vs Falcon Heavy launches? 
- `rocket_family` is the broadest grouping - `"Falcon"`. This rolls up _Falcon 9_ and _Falcon Heavy_ into one category.

### 2.9. _**Launch Pad**_

This section tells you where the rocket launched _from_

- `launchpad_id` - this is the Launch API's numerical identifier for the pad. Useful for joins in additional pad data from the same API.
- `launchpad_name` - is the specific name for the pad, e.g. `"Space Launch Complex 40"` or `"Launch Complex 39A"`
- `launchpad_description` - is free-text background on the pad, its history and what it's used for
- `launchpad_map_url` - is a link to the pads location on a map. Handy if you're building something interactive and 
and you want a _view on map_ option.
- `launchpad_latitude` - these are raw co-ordinates, useful if you want to plot the pad yourself
- `launchpad_longitude` - these are raw co-ordinates, useful if you want to plot the pad yourself
- `launchpad_location_name` - this is the broader site name, e.g. `"Cape Canaveral, FL, USA"`
- `launchpad_country` - this is the 3 letter country code, e.g. `"USA"`

??? tip "Why so many location fields?"
    There are many ways to use location data, co-ordinates for maps, pad name for precision, location name 
    for regional grouping and country for the broades cut. Different analyses need different levels of geographic 
    detail.

Did your eagle eye spot it :eyes:? Every field has been initialised with a default value, e.g. `str | None = None` **_except_**
`launch_name`. This does not take a default value of `None`.

```py hl_lines="5"

class SpaceX:
    
    # Code omitted ☝️
    # --- Launch info ---
    launch_name: str   
    launch_status: str | None = None
    launch_status_id: int | None = None
    launch_status_abbrev: str | None = None
    launch_status_description: str | None = None
    # Code omitted 👇
```

This means that if no `launch_name` is returned by the API then the script will fail. This is a _good_ thing as 
`launch_name` should be populated and failing the script will stop bad data sneaking in.

!!! tip "When should my fields be optional?"
    When deciding whether each field should be optional required, think to yourself _"If this field is empty, would it 
    impact the quality of my dataset"_.

    If the answer is **_yes_** then you should remove the `None` default, if **_no_** then keep it.

    In this dataset, only `launch_name` is a non-negotiable. Everything else is best effort.

:partying_face: Congratulations - you have just built a data contract! The data you now extract from the API will always match
the definitions you just created. Future you just thanked current you for saving lots of questions down the road.

## 3. Is there anything that makes API calls easier? :fontawesome-solid-wand-magic-sparkles:{ .gold-icon }

In this section we create two helper functions that assist us with the messy parts of working with a paginated(1) REST API 
that returns deeply nested JSON data(2).
{ .annotate }

1. Data coming back from an API often has a limit on the number of items returned. This helps:
    - _Protect servers_, without limits a single client could flood the server with requests and degrade
    the experience for everyone else
    - _Cost_ every API call costs the provider compute, bandwith and database queries. Limits keep things sustainable,
    especially for the free tier
    - _Stability_ with large unbound queries often timing out, run out of memory or crash. Smaller bounded responses are 
    more reliable for both sides

2. The data that is returned from this dataset contains information within information, i.e. you need to go through different 
levels to extract what you are looking for. For example, to get `rocket_family` you need to traverse 
`results → [0] → rocket → configuration → families → [0] → name`.  That's an array inside an object inside an object inside an array

!!! tip 
    The two helper functions below are used across **_all_** datasets that I create. For the purpose of making a tutorial I include them 
    in every python file, but you can create a `utils` folder and have these within a `utils.py` file if you want to create these once.

### 3.1 Handle bad records with _safe_get()_ 

This helper function allows you to dig into nested JSON without your script crashing if something is missing

Normally you might do something like `launch["rocket"]["configuration"]["families"][0]["name"]`. 

That works great - until one launch is missing the `families` key, or it's an empty list, or `configuration` is `null`. 
If this happens you will get a `KeyError` or a `TypeError` and your entire script stops because of one bad record out of 
300+ good ones.

!!! tip "Tip"
    Ever been sent an excel file with missing data which broke your whole import? This solves a similar pattern - rather than crashing on one bad record,
    you handle gaps gracefully and keep the pipeline running

Notice that this function never raises an exception. It returns `None` allowing the data model to decide whether it is acceptable or not.

```py {.annotate}
# Code omitted ☝️
--8<-- "docs_src/space_dev/modelling/spacex/spacex.py:113:139"
# Code omitted 👇
```

--8<-- "docs_src/space_dev/modelling/spacex/annotations/spacex.md"


### 3.2 Return more records with _fetch_all_pages()_

We query Launch Library API, and by using `params={'limit': 100}` we request 100 items at a time. To be able to get more data you need to make another API call.
To help you with this, the Launch Library provides a `next` key as part of their results. 

This function is set up specifically for the Launch API to keep following the `next` result set until there is not one available.

```py {.annotate}
# Code omitted ☝️
--8<-- "docs_src/space_dev/modelling/spacex/spacex.py:142:171"
# Code omitted 👇
```

--8<-- "docs_src/space_dev/modelling/spacex/annotations/spacex.md"

**_BOSH!_** you've just created 2 patterns which will help you navigate any APIs you now call. The code might not be exactly
the same, but you can repeat the ideas.

## 4. I've got JSON data, but how do I actually use it?

In this section we take our API data and fit it to our Pydantic model. 

```py {.annotate}
# Code omitted ☝️
--8<-- "docs_src/space_dev/modelling/spacex/spacex.py:182:257"
# Code omitted 👇
```

--8<-- "docs_src/space_dev/modelling/spacex/annotations/spacex.md"


## 5. Ok, let's run it from start to finish

### 5.1 Extract your data with _get_spacex_data()_

In this section we either read the raw data from a CSV file if it exists, or call the Launch Library API if it doesn't. 

!!! tip "Tip"
    This cache-first pattern where it reads from an existing csv / downloaded file can help avoid running long queries on slow databases
    when the underlying data has not changed.


```py {.annotate}
# Code omitted ☝️
--8<-- "docs_src/space_dev/modelling/spacex/spacex.py:268:306"
# Code omitted 👇
```

--8<-- "docs_src/space_dev/modelling/spacex/annotations/spacex.md"

It's crazy how one line can do so much. All your data validation is done here.


```py hl_lines="2"
# Validate each record through the Pydantic model
launches = [parse_launch(raw) for raw in raw_launches] 
df = pd.DataFrame([launch.model_dump() for launch in launches])
```

This is where you find out whether the data you receive fits the contract you created, not downstream when a dashboard breaks.

### 5.2 Run it within _`__main__`_

We finally get to the part where we can run the script!

```py {.annotate}
# Code omitted ☝️
--8<-- "docs_src/space_dev/modelling/spacex/spacex.py:316:328"
# Code omitted 👇
```

--8<-- "docs_src/space_dev/modelling/spacex/annotations/spacex.md"

:rocket: You have just built a clean running pipeline that outputs an analytics ready csv. Love it. 

??? info ":detective: full code preview"
    
    ```py {.annotate}
    --8<-- "spacex_clean.py:18:212"
    ```

## What You've Built

You now have a repeatable data pipeline that validates its data. You've built a process which:

- Fetches data from a live API without manual intervention
- Validates every record against a defined schema, catching bad data in the process
- Creates a clean, analysis ready CSV file which can be used for dashboarding or sharing with colleagues

These are the same patterns that are used in production data engineering. The dataset used today is _Space X_ launches - but
the approach works just as well for claims data, pricing metrics, bordereaux files or other APIs used within your organisation.

> Want more patterns like this? [Subscribe to the newsletter](#) for weekly, practical data lessons — no fluff.