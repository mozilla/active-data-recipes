"""
Get information on the backout rate on autoland and mozilla-inbound over the given time period.

.. code-block:: bash

    adr backout_rate [--from <date> [--to <date>]]


`View Results <https://mozilla.github.io/active-data-recipes/#backout-rate>`__
"""
from __future__ import absolute_import, print_function

from adr.query import run_query


def run(args):

    pushes = len(set(run_query('all_push_id', args)['data']['push.id']))
    backouts = len(set(run_query('backout_rate', args)['data']['push.id']))
    backout_rate = round((float(backouts) / pushes) * 100, 2)

    return (
        ['Pushes', 'Backouts', 'Backout Rate'],
        [pushes, backouts, backout_rate],
    )
