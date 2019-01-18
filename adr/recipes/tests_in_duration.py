"""
This is currently broken.

.. code-block:: bash

    adr tests_in_duration
"""
from __future__ import absolute_import, print_function

from ..query import run_query


def run(config, args):

    result = run_query('tests_in_duration', config, args)['data']
    result.insert(0, ['Test Name', 'number of runs', 'average runtime'])
    return result
