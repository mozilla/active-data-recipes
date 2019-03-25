"""
This is currently broken.

.. code-block:: bash

    adr tests_in_duration
"""
from __future__ import absolute_import, print_function

from adr.query import run_query


def run(args):

    result = run_query('tests_in_duration', args)['data']
    result.insert(0, ['Test Name', 'number of runs', 'average runtime'])
    return result
