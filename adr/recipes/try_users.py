from __future__ import print_function, absolute_import

from collections import defaultdict

from ..cli import RecipeParser
from ..query import run_query


def run(args):
    parser = RecipeParser('date')
    parser.add_argument('--limit', type=int, default=25,
                        help="Maximum number of users to return")
    parser.add_argument('--sort-key', type=int, default=1,
                        help="Key to sort on (int, 0-based index)")
    args = parser.parse_args(args)

    header = ['User', 'Tasks', 'Pushes', 'Tasks / Push']
    if args.sort_key < 0 or len(header)-1 < args.sort_key:
        parser.error("invalid value for 'sort_key'")

    query_args = vars(args)
    query_args['branch'] = 'try'
    pushes = next(run_query('user_pushes', **query_args))
    pushes = pushes['data']

    query_args['from'] = 'task'
    tasks = next(run_query('user_tasks', **query_args))['data']

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
        data.append([user, tasks, pushes, round(float(tasks)/pushes, 2)])

    data = sorted(data, key=lambda k: k[args.sort_key], reverse=True)
    data = data[:args.limit]
    data.insert(0, header)
    return data
