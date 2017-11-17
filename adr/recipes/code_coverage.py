from __future__ import print_function, absolute_import

from ..cli import RecipeParser
from ..query import run_query


def run(args):
    """
    THIS IS PRONE TO DOUBLE COUNTING, AS DIFFERENT TEST CHUNKS COVER COMMON LINES
    AT THE VERY LEAST YOU GET A ROUGH ESTIMATE OF COVERAGE
    """
    parser = RecipeParser()
    parser.add_argument('--path', required=True,
                        help="Source code path to show summary coverage stats for.")
    parser.add_argument('--rev', required=True,
                        help="Revision to collect coverage data at.")
    args = parser.parse_args(args)
    query_args = vars(args)

    result = next(run_query('code_coverage', **query_args))
    output = [result['header']]+result['data']
    return output
