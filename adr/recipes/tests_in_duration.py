"""
This is currently broken.

.. code-block:: bash

    adr tests_in_duration
"""
from __future__ import print_function, absolute_import

from ..query import run_query


def run(args, config):

    result = run_query('tests_in_duration', config, **vars(args))['data']
    result.insert(0, ['Test Name', 'number of runs', 'average runtime'])
    return result
