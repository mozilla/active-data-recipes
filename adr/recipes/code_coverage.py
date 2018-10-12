"""
Get code coverage information for the given `path` at `rev`. Both arguments are required.

.. code-block:: bash

    adr code_coverage --path <path> --rev <rev>
"""
from __future__ import print_function, absolute_import

from ..recipe import RecipeParser
from ..query import run_query


def run(args, config):
    """
    THIS IS PRONE TO DOUBLE COUNTING, AS DIFFERENT TEST CHUNKS COVER COMMON LINES
    AT THE VERY LEAST YOU GET A ROUGH ESTIMATE OF COVERAGE
    """
    parser = RecipeParser('path', 'rev')
    args = parser.parse_args(args)
    query_args = vars(args)

    result = next(run_query('code_coverage', config, **query_args))
    output = [result['header']]+result['data']
    return output
