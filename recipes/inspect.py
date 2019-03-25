"""
Get information on the ActiveData schema. The above command returns the
available tables. To see the columns in a table, run:

.. code-block:: bash

    adr inspect
    adr inspect --table task
"""
from __future__ import absolute_import, print_function

from adr.context import override
from adr.query import run_query

RUN_CONTEXTS = [
    override('attribute', hidden=True),
]


def run(args):

    if not args.table:
        data = run_query('meta', args)['data']
        data = sorted([(d['name'],) for d in data])
        data.insert(0, ('Table',))
        return data

    if not args.attribute:
        data = run_query('meta_columns', args)['data']
        data = sorted([(d['name'],) for d in data])
        data.insert(0, ('Column',))
        return data

    data = run_query('meta_values', args)['data']
    data.insert(0, (args.attribute, 'count'))
    return data
