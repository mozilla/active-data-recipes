"""
See the number of tests that have a duration in pre-selected buckets.

.. code-block:: bash

    adr test_durations
"""
from __future__ import print_function, absolute_import

from ..query import run_query


def run(config, args):

    result = []

    data = run_query('test_durations', config, args)['data']['result.test']

    duration = [1, 2, 5, 10, 20, 30, 45, 60, 90, 120, 150, 'max']
    for index in range(0, len(duration)):
        result.append([duration[index], data[index]])
    result.insert(0, ['Max Duration (seconds)', 'number of tests'])
    return result
