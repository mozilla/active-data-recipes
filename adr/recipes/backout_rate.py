"""
Get information on the backout rate on autoland and mozilla-inbound over the given time period.

.. code-block:: bash

    adr backout_rate [--from <date> [--to <date>]]


`View Results <https://mozilla.github.io/active-data-recipes/#backout-rate>`__
"""
from __future__ import print_function, absolute_import

from ..query import run_query


def run(args, config):

    query_arg = vars(args)
    pushes = len(set(run_query('all_push_id', config, **query_arg)['data']['push.id']))
    backouts = len(set(run_query('backout_rate', config, **query_arg)['data']['push.id']))
    backout_rate = round((float(backouts) / pushes) * 100, 2)

    return (
        ['Pushes', 'Backouts', 'Backout Rate'],
        [pushes, backouts, backout_rate],
    )
