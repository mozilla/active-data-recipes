"""
Get the total tasks passed and failed for build platforms and types.

.. code-block:: bash

    adr config_intermittents [--branch <branch>]
"""
from __future__ import absolute_import, print_function

from adr.context import override
from adr.query import run_query


RUN_CONTEXTS = [
    override('limit', default=50, help="Maximum number of configs"),
    override('sort_key', default=0, help="Key to sort on (int, 0-based index)"),
]


def run(args):
    # process config data
    data = run_query('config_intermittents', args)["data"]
    result = []
    for record in data:
        if not record or not record[args.sort_key]:
            continue
        if isinstance(record[1], list):
            record[1] = record[1][-1]
        if record[2] is None:
            continue
        if record[3] is None:
            continue
        record.append(float(record[3] / (record[2] * 1.0)))
        result.append(record)

    result = sorted(result, key=lambda k: k[args.sort_key], reverse=True)[:args.limit]
    result.insert(0, ['Platform', 'Type', 'Num Jobs', 'Number failed', '%% failed'])
    return result
