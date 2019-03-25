"""
Get the average and total runtime for build platforms and types.

.. code-block:: bash

    adr config_durations [--branch <branch>]
"""
from __future__ import absolute_import, print_function

from adr.query import run_query

BROKEN = True


def run(config, args):
    # process config data
    data = run_query('config_durations', config, args)["data"]
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
        record[3] = round(record[3] / 60, 2)
        record.append(int(round(record[2] * record[3], 0)))
        result.append(record)

    result = sorted(result, key=lambda k: k[args.sort_key], reverse=True)[:args.limit]
    result.insert(0, ['Platform', 'Type', 'Num Jobs', 'Average Hours', 'Total Hours'])
    return result
