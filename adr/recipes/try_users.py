from __future__ import print_function, absolute_import

from argparse import ArgumentParser
from collections import defaultdict

from ..query import run_query


def run(args):
    parser = ArgumentParser()
    parser.add_argument('--from', dest='from_date', default='now-week',
                        help="Starting date to pull data from, defaults "
                             "to a week ago")
    parser.add_argument('--to', dest='to_date', default='now',
                        help="Ending date to pull data from, defaults to "
                             "today")
    parser.add_argument('--limit', type=int, default=25,
                        help="Maximum number of users to return")
    args = parser.parse_args(args)

    query_args = vars(args)
    query_args['branch'] = 'try'
    pushes = run_query('user_pushes', **query_args)

    query_args['from'] = 'task'
    tasks = run_query('user_tasks', **query_args)

    users = defaultdict(list)
    for user, num in tasks:
        users[user].append(num)
    for user, num in pushes:
        users[user].append(num)

    header = ['User', 'Tasks', 'Pushes', 'Tasks / Push']
    data = []
    for user, value in users.items():
        if len(value) != 2:
            continue
        tasks, pushes = value
        data.append([user, tasks, pushes, round(float(tasks)/pushes, 2)])

    data = sorted(data, key=lambda k: k[1], reverse=True)
    data = data[:args.limit]
    data.insert(0, header)
    return data
