"""
Get runtimes for a specific test file broken across platforms.

.. code-block:: bash

    adr tests_config_time -t <path to test>
"""
from __future__ import absolute_import, print_function

from adr.query import run_query

BROKEN = True


def run(args):

    result = run_query('tests_config_times', args)['data']
    result.insert(0, ['Config Name', '# of green runs', 'max runtime'])
    return result
