"""
Get information on the ActiveData schema. The above command returns the
available tables. To see the columns in a table, run:

.. code-block:: bash

    adr inspect
    adr inspect --table task
"""
from __future__ import print_function, absolute_import

from ..recipe import RecipeParser
from ..query import run_query


def run(args, config):
    parser = RecipeParser()
    parser.add_argument('--table', default=None,
                        help="Table to inspect.")
    args = parser.parse_args(args)

    if not args.table:
        data = next(run_query('meta', config))['data']
        data = sorted([(d['name'],) for d in data])
        data.insert(0, ('Table',))
        return data

    data = next(run_query('meta_columns', config, table=args.table))['data']
    data = sorted([(d['name'],) for d in data])
    data.insert(0, ('Column',))
    return data


def get_recipe_desc():
    return """
        Get information on the ActiveData schema. The above command returns the
        available tables. You can see the columns of each table by using
        --table <table_name>
    """


def get_recipe_args():
    return ['--table']
