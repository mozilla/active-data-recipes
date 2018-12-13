"""
Prints information on try effifiency. This is a measure of how effective try is
at preventing backouts. It is roughly:

    1000000 / (total_compute_hours_on_try * backout_rate)

.. code-block:: bash

    adr try_efficiency

`View Results <https://mozilla.github.io/active-data-recipes/#try-efficiency>`_
"""
from __future__ import print_function, absolute_import

from ..recipe import execute_query


def run(args):

    pushes = len(set(execute_query('all_push_id')['data']['push.id']))
    backouts = len(set(execute_query('backout_rate')['data']['push.id']))
    backout_rate = round((float(backouts) / pushes) * 100, 2)

    new_context = {'branch': 'try'}
    data = execute_query('total_hours_spent_on_branch', new_context)['data']

    try_hours = int(data['hours'])
    try_efficiency = round(10000000 / (backout_rate * try_hours), 2)

    return (
        ['Backout Rate', 'Total Compute Hours on Try', 'Try Efficiency'],
        [backout_rate, try_hours, try_efficiency],
    )
