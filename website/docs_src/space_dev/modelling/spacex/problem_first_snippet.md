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
    rocket  = launch["rocket"]["configuration"]["families"][0]["name"]  # (1)
    mission = launch["mission"]["name"]                                  # (2)
    net     = launch["net"]                                              # (3)
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

296 good records. One bad one. The whole run stops and your CSV is empty.

This is not an edge case — it is what happens every time you work with a real API.
Missions get added late. Fields go missing. A date that was a proper timestamp last
month comes back as an empty string today.

!!! warning "The silent version is worse"
    Sometimes the script does not crash — it just silently writes wrong data.
    `net` can come back as an empty string `""` instead of a datetime. If you convert
    it later in your BI tool, you get nulls in your time series and nobody notices
    until a chart breaks three weeks later.

The rest of this tutorial builds the version that handles all of this cleanly —
every field extracted safely, every record validated before it touches your CSV.
