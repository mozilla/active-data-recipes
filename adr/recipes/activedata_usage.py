"""
    Show ActiveData query usage, by day

    .. code-block:: bash

    adr activedata_usage [--from <date> [--to <date>]]
    """

from __future__ import print_function, absolute_import

from ..recipe import RecipeParser
from ..query import run_query


def run(args, config):
    response = next(run_query('activedata_usage', config, *args))
    return [response['header']] + response['data']
