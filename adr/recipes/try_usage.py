from __future__ import print_function, absolute_import

from argparse import ArgumentParser
from ..query import run_query


def run(args):
    parser = ArgumentParser()
    parser.add_argument('--from', dest='from_date', default='today-week',
                        help="Starting date to pull data from, defaults to a week ago")
    parser.add_argument('--to', dest='to_date', default='today',
                        help="Ending date to pull data from, defaults to today")
    args = parser.parse_args(args)

    query_args = vars(args)
    data = run_query('try_commit_messages', **query_args)

    unique_users = len(set(data['user']))
    data = zip(data['user'], data['message'])
    total_pushes = float(len(data))

    mach_syntax = {'count': 0, 'users': set()}
    mach_fuzzy = {'count': 0, 'users': set()}
    vanilla = {'count': 0, 'users': set()}
    other = {'count': 0, 'users': set()}

    for user, message in data:
        if "Pushed via `mach try syntax`" in message:
            mach_syntax['count'] += 1
            mach_syntax['users'].add(user)
        elif "Pushed via `mach try fuzzy`" in message:
            mach_fuzzy['count'] += 1
            mach_fuzzy['users'].add(user)
        elif "try:" in message:
            vanilla['count'] += 1
            vanilla['users'].add(user)
        else:
            other['count'] += 1
            other['users'].add(user)

    print("Total pushes to try: {} (with {} unique users)".format(int(total_pushes), unique_users))
    print("vanilla try syntax: {}% (with {} unique users)".format(int((vanilla['count'] / total_pushes) * 100), len(vanilla['users'])))
    print("mach try syntax: {}% (with {} unique users)".format(int((mach_syntax['count'] / total_pushes) * 100), len(mach_syntax['users'])))
    print("mach try fuzzy: {}% (with {} unique users)".format(int((mach_fuzzy['count'] / total_pushes) * 100), len(mach_fuzzy['users'])))
    print("other: {}% (with {} unique users)".format(int((other['count'] / total_pushes) * 100), len(other['users'])))

