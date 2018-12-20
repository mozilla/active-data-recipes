"""
Show ActiveData query usage, by day

.. code-block:: bash

    adr activedata_usage [--from <date> [--to <date>]]
"""

from __future__ import print_function, absolute_import

from ..query import run_query


def run(args, config):

    query_args = vars(args)
    response = run_query('activedata_usage', config, **query_args)
    return [response['header']] + response['data']
