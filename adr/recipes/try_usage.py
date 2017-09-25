from __future__ import print_function, absolute_import

from argparse import ArgumentParser
from collections import defaultdict, OrderedDict

from ..query import run_query


def run(args):
    parser = ArgumentParser()
    parser.add_argument('--from', dest='from_date', default='now-week',
                        help="Starting date to pull data from, defaults "
                             "to a week ago")
    parser.add_argument('--to', dest='to_date', default='now',
                        help="Ending date to pull data from, defaults to "
                             "today")
    args = parser.parse_args(args)

    query_args = vars(args)
    data = run_query('try_commit_messages', **query_args)

    count = defaultdict(int)
    count['total'] = len(data['message'])
    users = defaultdict(set)
    users['total'] = set(data['user'])

    d = OrderedDict()
    d['syntax'] = {
        'test': 'Pushed via `mach try syntax`',
        'method': 'mach try syntax',
    }
    d['vanilla'] = {
        'test': 'try:',
        'method': 'vanilla try syntax',
    }
    d['fuzzy'] = {
        'test': 'Pushed via `mach try fuzzy`',
        'method': 'mach try fuzzy',
    }
    d['empty'] = {
        'test': '',
        'method': 'empty',
    }
    d['total'] = {
        'test': None,
        'method': 'total',
    }

    data = zip(data['user'], data['message'])
    for user, message in data:
        for k, v in d.items():
            if v['test'] in message:
                count[k] += 1
                users[k].add(user)
                break

    def fmt(key):
        percent = round(float(count[key]) / count['total'] * 100, 1)
        return [d[key]['method'], count[key], percent, len(users[key]), round(float(count[key])/len(users[key]), 2)]

    data = [['Method', 'Pushes', 'Percent', 'Users', 'Push / User']]
    for k, v in sorted(count.items(), key=lambda t: t[1], reverse=True):
        data.append(fmt(k))
    return data
