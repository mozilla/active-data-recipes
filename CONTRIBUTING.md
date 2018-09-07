# How To Contribute

Changes should be submitted via pull request. Please make sure all tests pass before submitting by
running `tox`. If adding a new recipe, please also add a test for it (see the
[testing](#testing) section below).

# Concepts

There are two basic concepts in `adr`, queries and recipes.


## Queries

A query is a `yaml` (or `json`) file that has a `.query` extension and lives under `adr/queries`.
Queries are [json-e][0] templates that get rendered with whatever context a recipe passes it.
Consult the [json-e documentation][1] for more information. A rendered query file should result in
a valid ActiveData query.


### Writing Queries

The best way to learn how to write ActiveData queries is to look at the existing examples under
`adr/queries`. These queries can be run with:

    $ adr-query <query>

The `adr-query` command will create a dummy context and set a limit of 25 on all queries it runs.

Another way to test queries is via the ActiveData [web front-end][2]. You can use this tool to
quickly test and play around with queries. There is a lot of thorough documentation on writing
queries linked to from that portal. When running `adr-query`, you can use `-v/--verbose` to dump the
rendered json query to stdout before running. This is useful for copy/pasting into the web query
tool. If copy and pasting *from* the web query tool, be sure to convert all tabs to spaces,
otherwise `adr` will be unable to parse the query file.

In order to write a query, you need to understand the schema of the tables you are working with. The
`adr inspect` recipe can help with this. To see all the available tables in ActiveData, you can run:

    $ adr inspect

To see all of the columns available in a given table, you can run:

    $ adr inspect --table <table>


### Multiple Queries in a File

You can group several related queries in the same file using yaml's [document][3] feature. Simply
separate queries with a `---` delimiter:

    ---
    <query A>
    ---
    <query B>
    ---
    <query C>

This provides a way of grouping similar queries together. This should only be used when it never
makes sense to run `query B` without `query A`.


## Recipes

A recipe is a python script that typically:

1. Defines some command line arguments and formats the results into a context
2. Runs one or more queries, passing in the context
3. Post-processes the results and returns them in a format understood by the formatter functions

Recipes can be very simple, or arbitrarily complex. They live under `adr/recipes`.


## Writing Recipes

Recipe files must define a `run(args)` function. The `args` parameter is a list of command line
arguments that should be parsed by a recipe specific argument parser. For convenience, you can use
the `adr.cli.RecipeParser` class to accomplish this. It allows sharing certain common arguments
(like `--to/--from`) across recipes.

The only other requirement is that the data returned be in a format recognized by the formatter
functions. The easiest is a list of lists:

    [
        ['row1-col1', 'row1-col2', 'row1-col3'],
        ['row2-col1', 'row2-col2', 'row2-col3'],
        ['row3-col1', 'row3-col2', 'row3-col3'],
        ...
    ]

Each list represents a row in the table, whereas the items in the list represent the columns. Be
sure to put the header in the first row.

Another valid data format is a dict of lists:

    {
        'headerA': ['dataA-1', 'dataA-2', 'dataA-3', ...]
        'headerB': ['dataB-1', 'dataB-2', 'dataB-3', ...]
        'headerC': ['dataC-1', 'dataC-2', 'dataC-3', ...]
    }

This will create a table with the keys of the dict in the first row, and values zipped together. If
the values are not of equal length, an empty string will be used as a filler value. If the order of
the header is important, you can use a special `names` key to define the order:

    {
        'names': ['foo', 'bar', 'baz'],
        'foo': [...],
        'baz': [...],
        'bar': [...],
    }


### Running Queries

To run a query, use the `adr.query.run_query(query, **context)` function. The first argument is the
string name of the query to run, and the second is the context to pass into that query. This returns
a generator that will yield the result of the next query in the specified query file. Typically the
information you'll need is under the data key. For example:

    from adr.query import run_query
    query = run_query('backout_rate', **context)
    pushes = next(query)['data']['push.id']
    backouts = next(query)['data']['push.id']
    # post process results

In this example, we run the two queries defined in the `backout_rate.query` file one after the
other.


## Testing

The active-data-recipes module supports both python 2.7 and python 3.6. You can run the unittests
with:

    $ pip install tox
    $ tox

The tests themselves live in the `test` directory and are written with the [pytest][4] framework.


### Creating or Modifying Recipe Tests

There is a special test called `test_recipes.py` that uses something called `recipe_tests`. These
are files that live under `test/recipe_tests` and have a `.test` extension. Creating one of these
files automatically adds a new parametrized subtest for `test_recipes.py`. These files are also yaml
and have the following format:

    recipe: <recipe_name>
    args: [<list of arguments to pass in>]
    queries:  # the queries key defines mock data to return when calling the specified query
        <query A file name>:
            - {<mocked data from first query in file>}
            - {<mocked data from second query in file>}
        <query B file name>:
            - {<mocked data from first query in file>}
    expected: {<expected data to result from running recipe given the above mock data>}

You can have multiple tests in the same `.test` file using the `---` document delimiter.

Manually creating or modifying these files can be very time consuming. So instead, you can use the
`adr-test` command to automatically generate them. Just pass in the query as if you were using the
normal `adr` command:

    $ adr-test backout_rate --from now-2week

This will automatically generate a new `.test` file that can be added and checked in. No further
steps are required, you should see it passing when running `tox`. The generated data can be quite
large, so you may want to hand edit the `.test` file to trim some of the mocked data down a bit for
readability.

[0]: https://github.com/taskcluster/json-e
[1]: https://taskcluster.github.io/json-e/
[2]: https://activedata.allizom.org/tools/query.html
[3]: http://yaml.org/spec/1.1/#id897596
[4]: https://docs.pytest.org/en/latest/
