from __future__ import print_function, absolute_import

import json
from collections import defaultdict

from ..cli import RecipeParser
from ..query import format_date, run_query


def run(args):
    parser = RecipeParser('date')
    parser.add_argument('-b', '--branch', default=['mozilla-central'],
                        help="Branches to gather backout rate on, can be specified "
                             "multiple times.")
    parser.add_argument('--limit', type=int, default=50,
                        help="Maximum number of jobs to return")
    parser.add_argument('--sort-key', type=int, default=4,
                        help="Key to sort on (int, 0-based index)")

    args = parser.parse_args(args)
    query_args = vars(args)
    limit = query_args.pop('limit')

    data = next(run_query('config_durations', **query_args))['data']
    result = []
    for record in data:
        if type(record[1]) == type([]):
            record[1] = record[1][-1]
        if record[2] is None:
            continue
        if record[3] is None:
            continue
        record[3] = round(record[3]/60, 2)
        record.append(int(round(record[2] * record[3], 0)))
        result.append(record)

    result = sorted(result, key=lambda k: k[args.sort_key], reverse=True)[:limit]
    result.insert(0, ['Platform', 'Type', 'Num Jobs', 'Average Hours', 'Total Hours'])
    return result
