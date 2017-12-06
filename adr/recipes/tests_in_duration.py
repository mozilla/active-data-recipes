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
    parser.add_argument('--min_seconds', default=120,
                        help="minimum seconds for runtime, default is: 120.")
    parser.add_argument('--max_seconds', default=1200,
                        help="maximum seconds for runtime, default is: 1200.")
    args = parser.parse_args(args)

    result = []
    query_args = vars(args)

    result = next(run_query('tests_in_duration', **query_args))['data']
    result.insert(0, ['Test Name', 'number of runs', 'average runtime'])
    return result
