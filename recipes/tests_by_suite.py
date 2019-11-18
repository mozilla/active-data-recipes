"""
See a breakdown of the number of tests for each suite.

.. code-block:: bash

    adr tests_by_suite
"""
from adr.query import run_query


def run(args):
    result = []
    data = run_query('tests_by_suite', args)['data']
    data = [row for row in data if row[0] is not None]

    for suite, _, num_tests in sorted(data):
        result.append([suite, num_tests])
    result.insert(0, ['Suite', 'Number of tests'])
    return result
