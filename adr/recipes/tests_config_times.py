from __future__ import print_function, absolute_import

from ..cli import RecipeParser
from ..query import run_query


def run(args):
    parser = RecipeParser('date')
    parser.add_argument('-b', '--branch', default=['mozilla-inbound'],
                        help="Branches to query results from.")
    parser.add_argument('-c', '--build_type', default='opt',
                        help="build configuration, default is 'opt'.")
    parser.add_argument('-t', '--test_name', default=None, required=True,
                        help="full path of the test name "
                             "(ex. 'dom/xhr/tests/test_worker_xhr_timeout.html').")
    args = parser.parse_args(args)

    result = []
    query_args = vars(args)

    result = next(run_query('tests_config_times', **query_args))['data']
    result.insert(0, ['Config Name', '# of green runs', 'max runtime'])
    return result
