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
    parser.add_argument('attribute', nargs='?', default=None,
                        help="Display values of specified attribute within --table.")
    args = parser.parse_args(args)

    if not args.table:
        data = next(run_query('meta', config))['data']
        data = sorted([(d['name'],) for d in data])
        data.insert(0, ('Table',))
        return data

    if not args.attribute:
        data = next(run_query('meta_columns', config, table=args.table))['data']
        data = sorted([(d['name'],) for d in data])
        data.insert(0, ('Column',))
        return data

    data = next(run_query('meta_values', config, **vars(args)))['data']
    data.insert(0, (args.attribute, 'count'))
    return data
