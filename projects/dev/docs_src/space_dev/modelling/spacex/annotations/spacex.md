1. This is the API endpoint for the :rocket: [`launches`](https://ll.thespacedevs.com/2.3.0/launches/) data. We will make a call to this url with parameters to get data back.
2. This is the identifier of SpaceX in the dataset. Other space agencies have their own identifier
3. This is where the CSV file which is the initial output of this tutorial will be saved. It creates a spacex folder in the same folder as your python file and saves it there.
4. We create a class called `SpaceXLaunch` which inherits from `SQLModel` (which inherits `Pydantic`!). We pass data to this class from the API
5. This is a class variable conforming to a particular data type, `str` or `blank` in this instance. By default the value is `blank` unless we get data back from the API.
6. The only **_required_** variable (there is no default value of `None`). If there is no launch name the data is likely invalid and should cause a failure.
7. `def safe_get(obj, *keys, default=None):` This function takes 3 paramets:
    - `obj` - this is the nested dictionary we are diving into
    - `**keys` this is the path to follow, as many levels deep as you need
    - `default=None` - what to return if the path is missing

8. `if current is None:` 
    
    If you've ever had a script die halfway through a large import because of one null value.. this is the fix. Without this, 
    we would get `TypeError: 'NoneType' is not subscriptable`. Recognise that one? by retuning the `default` if at any point the API returns a `null` value 
    then the function stops and returns the `default`.

9. `if isinstance(key, int):` 

    This lets you handle two different data structures for the dictionary keys in one section. Example: `safe_get(launch, "rocket", "configuration", "families", 0, "name")`
    here we are rooting through the nested json using `strings` and `integers` for the keys. This bit of code takes the key, if it is a `integer` it treats the current value 
    as a list and does an index lookup. If it is a `string` it treats the current value as a dictionary and does a key lookup.

10. `len(current) > key` 
    
    We check that the next value is a list and then make sure that it has more values in it than the requested index. Without this we could get an `IndexError` when an empty list 
    is shorter than expected. This is set up to handle the case, e.g. `"families": []` where without this catch, `families[0]` would stop the script

11. `if isinstance(current, dict) and key in current:` 
    
    The equivalent safety check for dictionaries - verifies the key exists before trying to access it and prevents a `KeyError`

12. `return current` this is the line that gets executed if data is valid!

13. `User-Agent` the header helps the owners of the Launch API identify who is using it. They can identify your traffic if something 
    goes wrong.

14. `raise_for_status()` without this, a `404` or `500` response is still a valid Python response object. The code would then call `.json()`
    on a HTML error page and crash with a `JSONDecodeError` instead of a clear HTTP error message. With a `JSONDecodeError` error you might 
    spend a good hour trying to work out what's wrong with your code.. but in fact it's the `API` which is returned an error page.

15. `next_url = data.get('next')` this is where the next url to call is extracted. If there is no `'next'` key and the code returns `None` 
    then the while loop will stop

16. `while next_url:` with the request passing no `params` is a change to how we made the initial `resp` call above. This api includes 
    the `params` in the `'next'` url by default, including them again might cause pagination bugs

17. `.extend()` vs `.append()` we already have data in `all_results` from the initial call. Using `.extend()` means Python unpacks 
    each page's results into one flat list. A flat list is much easier to deal with downstream.

18. `list(safe_get(...) or []` the `"or []"` pattern is used in a few places in this section because `safe_get()` returns `None` when 
    the path is missing, and `list(None)` would throw a `TypeError`. The `or []` converts `None` to an empty list so the code 
    keeps running. 

19. Mission owners can appear in two places, `launch.mission.agencies` and `launch.program[].agencies`. Without looking at both sources 
    you might lose data if either one was empty. Here we create a list which extracts the data from program and then extends the data 
    from agencies

20. `dict.fromkeys(...)` removes any duplication in the mission owner extraction above. The same data can appear in both programs 
    and agencies. 

    ??? tip Tip

        `dict.fromkeys(...)` removes duplicates whilst preserving insertion order, unlike `set()` which loses order

21. `"; ".join(..)` programs like `"Starlink"` and `"Commercial Crew"` get joined into a single string `"Starlink; Commercial Crew"` 
    which is a deliberate data modelling choice for CSV output - it keeps one row per launch instead of exploding into a many-to-many 
    table 

22. `SpaceXLaunch(...)` is the constructor call - where Pydantic comes into play. The Pydantic model is a data contract, it ensures 
    your data conforms to a particular schema, otherwise it will throw an error. It turns a fragile script into a reliable pipeline. 
    If the data doesn't match the contract you find out here... not 3 steps down when someone else asks you why your format has changed. 
    Every field is checked against the schema from Section 2. If `launch_name` is missing it raises a `ValidationError`. 

23. `safe_get(..., "families", 0, "name")` an example of an integer key, `"families"` is a list, so 0 does an index lookup. Without `safe_get` 
    this would be `launch["rocket"]["configuration"]["families"][0]["name"]` wrapped in a try/except. 5 Levels of nesting could fail at any point.

24. `if not force_refresh and OUTPUT_CSV.exists()` skips calling the API if data already exists in CSV format and `force_refresh` is `False`. 
    Using `parse_dates` for `datetime` columns is important because otherwise they would be loaded as `string` and time-series operations 
    would not work properly.

25. Calls `fetch_all_pages` with params `"ordering": "-net"` which sorts newest-first ("Not Earlier Than"). `"lsp__id"` filters for SpaceX only.
    `"limit": 100` sets the page size. These are all API query parameters, not Python logic. 

26. list comprehension with `parse_launch` - Every raw dict extracted from the API passes through the Pydantic model. If any launch validation 
    fails this line will throw an exception and stop the whole pipeline. That's intentional - bad data should not slip into your extract.

27. `.model_dump()` converts each validated SQLModel instance back into a plain dict so Pandas can build a dataframe from it. Going from 
    API call (dict) -> SQLModel -> dict may seem counterintuitive but what we have done is validate it meets the correct data schema.

28. These explicit conversions ensures they're proper `datetime64[ns, UTC]` columns. The `utc=True` normalises mixed timezone offsets - without it 
    comparisons across launches in different timezones would give the wrong results.

29. Derived `year` & `month` columns make the data more analysis-friendly as they aren't returned by the API. They would be handy for downstream 
    `groupby` analysis (e.g. launches by year). We do this at this point and save ourselves hassle downstream.

30. This guards the code so that it runs when the script is executed directly (i.e. not part of any other imports). This is because `get_spacex_data()` 
    could be imported by any other script within the project.

31. `--refresh in sys.argv` This is a minimal CLI pattern - you can pass `--refresh` as part of your argument if using the CLI and it will
    call the API by default