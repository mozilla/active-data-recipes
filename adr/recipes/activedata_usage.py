"""
Show ActiveData query usage, by day

.. code-block:: bash

    adr activedata_usage [--from <date> [--to <date>]]
"""

from __future__ import print_function, absolute_import

from ..recipe import RecipeParser
from ..query import run_query


def run(args, config):
    parser = RecipeParser('date')
    args = parser.parse_args(args)

    query_args = vars(args)
    response = next(run_query('activedata_usage', config, **query_args))
    return [response['header']] + response['data']


def get_recipe_desc():
    return """
        Show ActiveData query usage, by day.
        Enter date in mm-dd-yyyy
    """


def get_recipe_args():
    return ['--from', '--to']
