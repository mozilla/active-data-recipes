"""
Prints stats on how often individual users are pushing to try over the last
week. The date range can be modified the same as the `hours_on_try` recipe.

.. code-block:: bash

    adr try_users
"""

from __future__ import absolute_import, print_function

from collections import defaultdict

from adr.context import override
from adr.query import run_query
from adr.recipe import RequestParser

RUN_CONTEXTS = [
    override('limit', default=25, help="Maximum number of users in result"),
    override('sort_key', default=1, help="Key to sort on (int, 0-based index)"),
]

BROKEN = True


def run(args):

    header = ['User', 'Tasks', 'Pushes', 'Tasks / Push']
    if args.sort_key < 0 or len(header) - 1 < args.sort_key:
        RequestParser.error("invalid value for 'sort_key'")

    args.branches = 'try'
    limit = args.limit
    delattr(args, 'limit')
    pushes = run_query('user_pushes', args)
    pushes = pushes['data']

    tasks = run_query('user_tasks', args)['data']

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
