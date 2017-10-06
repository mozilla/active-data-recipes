from __future__ import print_function, absolute_import

from argparse import ArgumentParser

from ..query import run_query




def run(args):
    """
    THIS IS PRONE TO DOUBLE COUNTING, AS DIFFERENT TEST CHUNKS COVER COMMON LINES
    AT THE VERY LEAST YOU GET A ROUGH ESTIMATE OF COVERAGE
    """
    parser = ArgumentParser()
    parser.add_argument(
            '--path',
            default="",
            help="source code path to so summary coverage stats for"
        )
    parser.add_argument(
        '--rev',
        default=None,
        help="revision"
    )
    args = parser.parse_args(args)

    query_args = vars(args)

    result = run_query('code_coverage', **query_args)
    output = [result['header']]+result['data']
    return output
