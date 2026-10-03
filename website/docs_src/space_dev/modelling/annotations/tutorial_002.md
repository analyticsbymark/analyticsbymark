1. Import from `sqlmodel` everything we will use, including the new `select()` function.

2. Create the `Policy` class model, representing the `policy` table.

3. Create the **engine**, we should use a single one shared by all the application code, and that's what we are doing here.

4. Create all the tables for the models registered in `SQLModel.metadata`.

    This also creates the database if it doesn't exist already.

5. Create each one of the `Policy` objects.

    You might not have this in your version if you had already created the data in the database.

6. Create a new **session** and use it to `add` the policies to the database, and then `commit` the changes.

7. Create a new **session** to query data.

    /// tip

    Notice that this is a new **session** independent from the one in the other function above.

    But it still uses the same **engine**. We still have one engine for the whole application.

    ///

8. Use the `select()` function to create a statement selecting all the `Policy` objects.

    This selects all the rows in the `policy` table.

9. Use `session.exec(statement)` to make the **session** use the **engine** to execute the internal SQL statement.

    This will go to the database, execute that SQL, and get the results back.

    It returns a special iterable object that we put in the variable `results`.

    This generates the output:

    ```
    INFO Engine BEGIN (implicit)
    INFO SELECT policy.id, policy.class_of_business, policy.broker, policy.premium_oc, policy.currency, policy.is_cat_exposed 
    FROM policy
    INFO Engine [generated in 0.00015s] ()
    ```

10. Iterate for each `Policy` object in the `results`.

11. Print each `policy`.

    The 3 iterations in the `for` loop will generate this output:

    ```
    id=1 class_of_business='Property' broker='London Brokers' currency='USD' premium_oc=50000 is_cat_exposed=True
    id=2 class_of_business='Marine' broker='Singapore Brokers' currency='USD' premium_oc=25000 is_cat_exposed=False
    id=3 class_of_business='Property' broker='Australia Brokers' currency='AUD' premium_oc=10000 is_cat_exposed=False'
    ```

12. At this point, after the `with` block, the **session** is closed.

    This generates the output:

    ```
    INFO Engine ROLLBACK
    ```

13. Add this function `select_heroes()` to the `main()` function so that it is called when we run this program from the command line.