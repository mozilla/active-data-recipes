from __future__ import print_function, absolute_import

import json
from collections import defaultdict

from ..cli import RecipeParser
from ..query import format_date, run_query


def run(args):
    parser = RecipeParser('date')
    parser.add_argument('-b', '--branch', default=['mozilla-inbound'],
                        help="Branches to query results from.")
    parser.add_argument('-p', '--platform', default='windows10-64',
                        help="platform for results, default is windows10-64")
    parser.add_argument('-c', '--build_type', default='opt',
                        help="build configuration, default is 'opt'.")
    args = parser.parse_args(args)

    result = []
    query_args = vars(args)

    data = next(run_query('test_durations', **query_args))['data']['result.test']

    duration = [1,2,5,10,20,30,45,60,90,120,150,'max']
    for index in range(0, len(duration)):
        result.append([duration[index], data[index]])
    result.insert(0, ['Max Duration (seconds)', 'number of tests'])
    return result
