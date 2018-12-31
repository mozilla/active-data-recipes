"""
Prints stats on how often individual users are pushing to try over the last
week. The date range can be modified the same as the `hours_on_try` recipe.

.. code-block:: bash

    adr try_users
"""

from __future__ import print_function, absolute_import

from collections import defaultdict

from ..query import run_query
from ..recipe import RecipeParser

RUN_CONTEXTS = ['from_date', 'to_date',
                {'limit': [['--limit'],
                           {'type': int,
                            'default': 25,
                            'help': "Maximum number of users in result"
                            }]},
                {'sort_key': [['--sort-key'],
                              {'type': int,
                               'default': 1,
                               'help': "Key to sort on (int, 0-based index)",
                               }]}

                ]


def run(config, args):

    header = ['User', 'Tasks', 'Pushes', 'Tasks / Push']
    if args.sort_key < 0 or len(header) - 1 < args.sort_key:
        RecipeParser.error("invalid value for 'sort_key'")

    args.branch = 'try'
    limit = args.limit
    delattr(args, 'limit')
    pushes = run_query('user_pushes', config, args)
    pushes = pushes['data']

    tasks = run_query('user_tasks', config, args)['data']

    users = defaultdict(list)
    for user, num in tasks:
        users[user].append(num)
    for user, num in pushes:
        users[user].append(num)

    data = []
    for user, value in users.items():
        if len(value) != 2:
            continue
        tasks, pushes = value
        data.append([user, tasks, pushes, round(float(tasks) / pushes, 2)])

    data = sorted(data, key=lambda k: k[args.sort_key], reverse=True)
    data = data[:limit]
    data.insert(0, header)
    return data
