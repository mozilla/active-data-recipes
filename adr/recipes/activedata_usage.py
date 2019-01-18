"""
Show ActiveData query usage, by day

.. code-block:: bash

    adr activedata_usage [--from <date> [--to <date>]]
"""

from __future__ import absolute_import, print_function

from ..query import run_query


def run(config, args):

    response = run_query('activedata_usage', config, args)
    return [response['header']] + response['data']
