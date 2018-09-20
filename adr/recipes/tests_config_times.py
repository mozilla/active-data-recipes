"""
Get runtimes for a specific test file broken across platforms.

.. code-block:: bash

    adr tests_config_time -t <path to test>
"""
from __future__ import print_function, absolute_import

from ..recipe import RecipeParser
from ..query import run_query


def run(args):
    parser = RecipeParser('date', 'branch', 'build', 'test')
    args = parser.parse_args(args)

    result = []
    query_args = vars(args)

    result = next(run_query('tests_config_times', **query_args))['data']
    result.insert(0, ['Config Name', '# of green runs', 'max runtime'])
    return result
