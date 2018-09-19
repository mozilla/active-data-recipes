"""
Get information on the backout rate on autoland and mozilla-inbound over the given time period.

.. code-block:: bash

    adr backout_rate [--from <date> [--to <date>]]


`View Results <https://mozilla.github.io/active-data-recipes/#backout-rate>`__
"""
from __future__ import print_function, absolute_import

from ..cli import RecipeParser
from ..query import run_query


def run(args):
    parser = RecipeParser('date')
    args = parser.parse_args(args)

    query_args = vars(args)
    query = run_query('backout_rate', **query_args)

    pushes = len(set(next(query)['data']['push.id']))
    backouts = len(set(next(query)['data']['push.id']))
    backout_rate = round((float(backouts) / pushes) * 100, 2)

    return (
        ['Pushes', 'Backouts', 'Backout Rate'],
        [pushes, backouts, backout_rate],
    )
