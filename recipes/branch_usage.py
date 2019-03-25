"""
A summary of how many compute hours were spent on each branch.

.. code-block:: bash

    adr branch_usage [-B <branch>] [-B <branch>]

"""
from __future__ import absolute_import, print_function

from adr.context import override
from adr.query import run_query

DEFAULT_BRANCHES = [
    'autoland',
    'mozilla-central',
    'mozilla-inbound',
]

RUN_CONTEXTS = [
    override('branches', default=DEFAULT_BRANCHES),
]


def run(args):
    results = []
    branches = args.branches
    delattr(args, 'branches')

    total = 0
    for branch in branches:
        args.branches = [branch]
        data = run_query('total_hours_spent_on_branch', args)['data']
        hours = int(data['hours'])
        total += hours
        results.append([branch, hours])

    results.append(["total", total])

    for res in results:
        percentage = round(float(res[1]) / total * 100, 1)
        res.append(percentage)

    results.sort(key=lambda x: x[1], reverse=True)
    results.insert(0, ['Branch', 'Total Compute Hours', 'Percentage'])
    return results
