"""
Get information on the longest running tasks. Returns the total count, average
runtime and total runtime over a given date range and set of branches.

.. code-block:: bash

    adr task_durations

`View Results <https://mozilla.github.io/active-data-recipes/#task-durations>`__
"""
from __future__ import print_function, absolute_import

from ..recipe import RecipeParser
from ..query import run_query

DEFAULT_BRANCHES = [
    'autoland',
    'mozilla-inbound',
    'mozilla-central',
]


def run(args, config):
    parser = RecipeParser('build', 'date', 'platform')
    parser.add_argument('-B', '--branch', default=DEFAULT_BRANCHES, nargs='+',
                        help="Branches to gather backout rate on, can be specified "
                             "multiple times.")
    parser.add_argument('--limit', type=int, default=20,
                        help="Maximum number of jobs to return")
    parser.add_argument('--sort-key', type=int, default=2,
                        help="Key to sort on (int, 0-based index)")

    args = parser.parse_args(args)
    query_args = vars(args)
    limit = query_args.pop('limit')

    data = next(run_query('task_durations', config, **query_args))['data']
    result = []
    for record in data:
        if record[2] is None:
            continue
        record[2] = round(record[2]/60, 2)
        record.append(int(round(record[1] * record[2], 0)))
        result.append(record)

    result = sorted(result, key=lambda k: k[args.sort_key], reverse=True)[:limit]
    result.insert(0, ['Taskname', 'Num Jobs', 'Average Hours', 'Total Hours'])
    return result
