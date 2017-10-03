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
    parser.add_argument('-b', '--branch', default=['autoland', 'mozilla-inbound', 'mozilla-central'],
                        help="Branches to gather backout rate on, can be specified "
                             "multiple times.")
    parser.add_argument('--limit', type=int, default=50,
                        help="Maximum number of jobs to return")
    parser.add_argument('--sort-key', type=int, default=2,
                        help="Key to sort on (int, 0-based index)")

    args = parser.parse_args(args)
    args.branch = json.dumps(args.branch)
    query_args = vars(args)

    data = run_query('task_durations', **query_args)['data']
    result = []
    for record in data:
        if record[2] is None:
            continue
        record[2] = round(record[2]/60, 2)
        record.append(int(round(record[1] * record[2], 0)))
        result.append(record)

    result = sorted(result, key=lambda k: k[args.sort_key], reverse=True)[:args.limit]
    result.insert(0, ['Task', 'Count', 'Average Hours', 'Total Hours'])
    return result
