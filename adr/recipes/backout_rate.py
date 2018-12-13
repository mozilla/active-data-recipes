"""
Get information on the backout rate on autoland and mozilla-inbound over the given time period.

.. code-block:: bash

    adr backout_rate [--from <date> [--to <date>]]


`View Results <https://mozilla.github.io/active-data-recipes/#backout-rate>`__
"""
from __future__ import print_function, absolute_import

from ..recipe import execute_query


def run(args):

    pushes = len(set(execute_query('all_push_id')['data']['push.id']))
    backouts = len(set(execute_query('backout_rate')['data']['push.id']))
    backout_rate = round((float(backouts) / pushes) * 100, 2)

    return (
        ['Pushes', 'Backouts', 'Backout Rate'],
        [pushes, backouts, backout_rate],
    )
