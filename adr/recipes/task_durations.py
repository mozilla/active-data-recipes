"""
Get information on the longest running tasks. Returns the total count, average
runtime and total runtime over a given date range and set of branches.

.. code-block:: bash

    adr task_durations

`View Results <https://mozilla.github.io/active-data-recipes/#task-durations>`__
"""
from __future__ import absolute_import, print_function

from ..query import run_query

DEFAULT_BRANCHES = [
    'autoland',
    'mozilla-inbound',
    'mozilla-central',
]

RUN_CONTEXTS = ['from_date', 'to_date', 'platform',
                {'limit': [['--limit'],
                           {'type': int,
                            'default': 20,
                            'help': "Maximum number of jobs in result"
                            }]},
                {'sort_key': [['--sort-key'],
                              {'type': int,
                               'default': 2,
                               'help': "Key to sort on (int, 0-based index)",
                               }]},
                {'branch': [['--branch'],
                            {'default': DEFAULT_BRANCHES,
                             'nargs': '+',
                             'help': "Branches to gather backout rate on, can be specified "
                                     "multiple times."
                             }]}
                ]


def run(config, args):

    limit = args.limit
    delattr(args, 'limit')

    data = run_query('task_durations', config, args)['data']
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
