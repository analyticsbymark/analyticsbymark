[//]: # (Inspiration for hello world example taken from https://raw.githubusercontent.com/fastapi/sqlmodel/refs/heads/main/docs/tutorial/select.md)

# Creating Policies - SELECT

## Read Data with **SQLModel**

Now let's do the same query to read all the policies, but with **SQLModel**.

## Create a **Session**

The first step is to create a **Session**, the same way we did when creating the rows.

We will start with that in a new function `select_policies()`:


``` py title="" hl_lines="3 4"
# Code omitted ☝️

--8<-- "docs_src/space_dev/modelling/tutorial_001.py:38:39"

# Code omitted 👇
```

## Create a `select` Statement

Next, pretty much the same way you write a SQL `SELECT` statement above, now we'll create a **SQLModel** `select` statement.

First we have to import `select` from `sqlmodel` at the top of the file:

``` py title="" hl_lines="3"
# Code omitted ☝️

--8<-- "docs_src/space_dev/modelling/tutorial_001.py:3:3"

# Code omitted 👇
```

And then we will use it to create a `SELECT` statement in Python code:

``` py title="" hl_lines="3"
# Code omitted ☝️

--8<-- "docs_src/space_dev/modelling/tutorial_001.py:38:40"

# Code omitted 👇
```

It's a very simple line of code that conveys a lot of information:

```Python
statement = select(Policy)
```

This is equivalent to the equivalent SQL `SELECT` statement

```SQL
SELECT id, class_of_business, broker, premium_oc, curreny, is_cat_exposed
FROM policy
```

We pass the class model `Policy` to the `select()` function. And that tells it that we want to select all the columns necessary for the `Policy` class.

And notice that in the `select()` function we don't explicitly specify the `FROM` part. It is already obvious to **SQLModel** (actually to SQLAlchemy) that we want to select `FROM` the table `policy`, because that's the one associated with the `Hero` class model.

!!! tip

    The value of the `statement` returned by `select()` is a special object that allows us to do other things.
    
    I'll tell you about that in the next chapters.


## Execute the Statement

Now that we have the `select` statement, we can execute it with the **session**:

``` py title="" hl_lines="6"
# Code omitted ☝️

--8<-- "docs_src/space_dev/modelling/tutorial_001.py:38:41"

# Code omitted 👇
```

This will tell the **session** to go ahead and use the **engine** to execute that `SELECT` statement in the database and bring the results back.

Because we created the **engine** with `echo=True`, it will show the SQL it executes in the output.

This `session.exec(statement)` will generate this output:

```
INFO Engine BEGIN (implicit)
INFO SELECT policy.id, policy.class_of_business, policy.broker, policy.premium_oc, policy.currency, policy.is_cat_exposed 
FROM policy
INFO Engine [generated in 0.00015s] ()
```

The database returns the table with all the data, just like above when we wrote SQL directly:

## Iterate Through the Results

The `results` object is an <abbr title="Something that can be used in a for loop">iterable</abbr> that can be used to go through each one of the rows.

Now we can put it in a `for` loop and print each one of the heroes:

``` py title="" hl_lines="7 8"
# Code omitted ☝️

--8<-- "docs_src/space_dev/modelling/tutorial_001.py:38:43"

# Code omitted 👇
```

This will print the output:

```
id=1 class_of_business='Property' broker='London Brokers' currency='USD' premium_oc=50000 is_cat_exposed=True
id=2 class_of_business='Marine' broker='Singapore Brokers' currency='USD' premium_oc=25000 is_cat_exposed=False
id=3 class_of_business='Property' broker='Australia Brokers' currency='AUD' premium_oc=10000 is_cat_exposed=False'
```

## Add `select_policies()` to `main()`

Now include a call to `select_policies()` in the `main()` function so that it is executed when we run the program from the command line:

``` py title="" hl_lines="7 8"
# Code omitted ☝️

--8<-- "docs_src/space_dev/modelling/tutorial_001.py:38:43"

# Code omitted 👇
```

## Review The Code

Great, you're now being able to read the data from the database! 🎉

Let's review the code up to this point:

```py {.annotate}
--8<-- "docs_src/space_dev/modelling/tutorial_002.py"
```

--8<-- "docs_src/space_dev/modelling/annotations/tutorial_002.md"
   

/// tip

Check out the number bubbles to see what is done by each line of code.

///

Here it starts to become more evident why we should have a single **engine** for the whole application, but different **sessions** for each group of operations.

This new session we created uses the *same* **engine**, but it's a new and independent **session**.

The code above creating the models could, for example, live in a function handling web API requests and creating models.

And the second section reading data from the database could be in another function for other requests.

So, both sections could be in **different places** and would need their own sessions.

/// info

To be fair, in this example all that code could actually share the same **session**, there's actually no need to have two here.

But it allows me to show you how they could be separated and to reinforce the idea that you should have **one engine** per application, and **multiple sessions**, one per each group of operations.

///

