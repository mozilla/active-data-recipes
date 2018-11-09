"""
This is currently broken.

.. code-block:: bash

    adr tests_in_duration
"""
from __future__ import print_function, absolute_import

from ..recipe import RecipeParser
from ..query import run_query


def run(args, config):
    parser = RecipeParser('branch', 'build', 'date', 'platform')
    parser.add_argument('--min_seconds', default=120,
                        help="minimum seconds for runtime, default is: 120.")
    parser.add_argument('--max_seconds', default=1200,
                        help="maximum seconds for runtime, default is: 1200.")
    args = parser.parse_args(args)

    query_args = vars(args)

    result = next(run_query('tests_in_duration', config, **query_args))['data']
    result.insert(0, ['Test Name', 'number of runs', 'average runtime'])
    return result


def get_recipe_desc():
    return """
    This is currently broken.
    """


def get_recipe_args():
    return []
