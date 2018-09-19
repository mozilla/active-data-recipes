"""
Show ActiveData query usage, by day

.. code-block:: bash

    adr backout_rate [--from <date> [--to <date>]]


`View Results <https://mozilla.github.io/active-data-recipes/#activedata-usage>`__
"""

from __future__ import print_function, absolute_import

from ..cli import RecipeParser
from ..query import run_query


def run(args):
    parser = RecipeParser('date')
    args = parser.parse_args(args)

    query_args = vars(args)
    response = next(run_query('activedata_usage', **query_args))
    return [response['header']] + response['data']
