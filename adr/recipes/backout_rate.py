from __future__ import print_function, absolute_import

import json
from argparse import ArgumentParser
from collections import defaultdict

from ..cli import RecipeParser
from ..query import run_query


def run(args):
    parser = RecipeParser('date')
    args = parser.parse_args(args)

    query_args = vars(args)
    query = run_query('backout_rate', **query_args)

    pushes = len(set(next(query)['data']['push.id']))
    backouts = len(set(next(query)['data']['push.id']))

    return (
        ['Pushes', 'Backouts', 'Backout Rate'],
        [pushes, backouts, round((float(backouts) / pushes) * 100, 2)],
    )
