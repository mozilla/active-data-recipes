"""
Show ActiveData query usage, by day

.. code-block:: bash

    adr activedata_usage [--from <date> [--to <date>]]
"""

from __future__ import print_function, absolute_import

from ..recipe import execute_query


def run(args):

    response = execute_query('activedata_usage')
    return [response['header']] + response['data']
