from __future__ import print_function, absolute_import

import json
from argparse import ArgumentParser
from collections import defaultdict

from ..query import format_date, run_query


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
    query = run_query('backout_rate', **query_args)

    data = next(query)['data']
    pushes = len(set(data['push.id']))

    data = next(query)['data']
    backouts = len(set(data['push.id']))

    result = (
        ['Pushes', 'Backouts', 'Backout Rate'],
        [pushes, backouts, round((float(backouts) / pushes) * 100, 2)],
    )
    return result

