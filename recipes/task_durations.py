"""
Get information on the longest running tasks. Returns the total count, average
runtime and total runtime over a given date range and set of branches.

.. code-block:: bash

    adr task_durations

`View Results <https://mozilla.github.io/active-data-recipes/#task-durations>`__
"""
from __future__ import absolute_import, print_function

from adr.context import override
from adr.query import run_query

DEFAULT_BRANCHES = [
    'autoland',
    'mozilla-inbound',
    'mozilla-central',
]

RUN_CONTEXTS = [
    override('branches', default=DEFAULT_BRANCHES),
    override('limit', default=20, help="Maximum number of jobs in result"),
    override('sort_key', default=2, help="Key to sort on (int, 0-based index)"),
]


def run(args):

    limit = args.limit
    delattr(args, 'limit')

    data = run_query('task_durations', args)['data']
    result = []
    for record in data:
        if record[2] is None:
            continue
        record[2] = round(record[2] / 60, 2)
        record.append(int(round(record[1] * record[2], 0)))
        result.append(record)

    result = sorted(result, key=lambda k: k[args.sort_key], reverse=True)[:limit]
    result.insert(0, ['Taskname', 'Num Jobs', 'Average Hours', 'Total Hours'])
    return result
