"""
Prints information on try effifiency. This is a measure of how effective try is
at preventing backouts. It is roughly:

    1000000 / (total_compute_hours_on_try * backout_rate)

.. code-block:: bash

    adr try_efficiency

`View Results <https://mozilla.github.io/active-data-recipes/#try-efficiency>`_
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

    query_args['branch'] = 'try'
    data = next(run_query('total_hours_spent_on_branch', **query_args))['data']

    try_hours = int(data['hours'])
    try_efficiency = round(10000000/(backout_rate * try_hours), 2)

    return (
        ['Backout Rate', 'Total Compute Hours on Try', 'Try Efficiency'],
        [backout_rate, try_hours, try_efficiency],
    )
