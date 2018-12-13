"""
Get information on the ActiveData schema. The above command returns the
available tables. To see the columns in a table, run:

.. code-block:: bash

    adr inspect
    adr inspect --table task
"""
from __future__ import print_function, absolute_import

from ..recipe import execute_query


def run(args):

    if not args.table:
        data = execute_query('meta')['data']
        data = sorted([(d['name'],) for d in data])
        data.insert(0, ('Table',))
        return data

    if not args.attribute:
        data = execute_query('meta_columns')['data']
        data = sorted([(d['name'],) for d in data])
        data.insert(0, ('Column',))
        return data

    data = execute_query('meta_values')['data']
    data.insert(0, (args.attribute, 'count'))
    return data
