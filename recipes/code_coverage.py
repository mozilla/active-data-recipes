"""
Get code coverage information for the given `path` at `rev`. Both arguments are required.

.. code-block:: bash

    adr code_coverage --path <path> --rev <rev>
"""
from __future__ import absolute_import, print_function

from adr.query import run_query

BROKEN = True


def run(args):
    """
    THIS IS PRONE TO DOUBLE COUNTING, AS DIFFERENT TEST CHUNKS COVER COMMON LINES
    AT THE VERY LEAST YOU GET A ROUGH ESTIMATE OF COVERAGE
    """

    result = run_query('code_coverage', args)
    output = [result['header']] + result['data']
    return output
