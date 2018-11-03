"""
Get skipped tests on the ActiveData schema. The above command returns the
test suites and their count which were skipped/disabled between specified period. Run:
.. code-block:: bash
    adr skipped_tests
"""
from __future__ import print_function, absolute_import

from ..query import run_query
from argparse import ArgumentParser


def run(args, config):
    parser = ArgumentParser()
    parser.add_argument('--from', default='today-day', dest='from_date',
                        help="Starting date to pull data from, defaults to a week ago")
    parser.add_argument('--to', default='eod', dest='to_date',
                        help="Ending date to pull data from, defaults to now")
    parser.add_argument('--limit', type=int, default=100,
                        help="Maximum number of tests to return")
    args = parser.parse_args(args)
    query_args = vars(args)
    result = next(run_query('skipped_tests', config, **query_args))['data']
    result.insert(0, ['Result test', 'run suite', 'count'])
    return result
