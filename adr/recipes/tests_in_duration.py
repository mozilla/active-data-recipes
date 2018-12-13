"""
This is currently broken.

.. code-block:: bash

    adr tests_in_duration
"""
from __future__ import print_function, absolute_import

from ..recipe import execute_query


def run(args):

    result = execute_query('tests_in_duration')['data']
    result.insert(0, ['Test Name', 'number of runs', 'average runtime'])
    return result
