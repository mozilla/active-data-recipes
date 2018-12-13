"""
Get runtimes for a specific test file broken across platforms.

.. code-block:: bash

    adr tests_config_time -t <path to test>
"""
from __future__ import print_function, absolute_import

from ..recipe import execute_query


def run(args):

    result = execute_query('tests_config_times')['data']
    result.insert(0, ['Config Name', '# of green runs', 'max runtime'])
    return result
