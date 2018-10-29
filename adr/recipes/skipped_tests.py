"""
Get skipped tests on the ActiveData schema. The above command returns the
tests which were skipped/disabled. Run:

.. code-block:: bash

    adr skipped_tests
"""
from __future__ import print_function, absolute_import

from ..recipe import RecipeParser
from ..query import run_query


def run(args, config):
    parser = RecipeParser()
    parser.add_argument('--limit', type=int, default=100,
                        help="Maximum number of tests to return")
    args = parser.parse_args(args)
    query_args = vars(args)

    result = next(run_query('skipped_tests', config, **query_args))['data']
    result.insert(0, ['Test', 'run name', 'status'])
    return result
