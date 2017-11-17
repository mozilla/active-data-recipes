from __future__ import print_function, absolute_import

import logging
import os
import sys
from argparse import ArgumentParser

import yaml

from ..main import run_recipe
from .. import query

here = os.path.abspath(os.path.dirname(__file__))
test_dir = os.path.join(here, os.pardir, os.pardir, 'test', 'recipe_tests')

log = logging.getLogger('adr')


def cli(args=sys.argv[1:]):
    parser = ArgumentParser()
    parser.add_argument('recipe',
                        help='Recipe to generate test for')
    args, remainder = parser.parse_known_args(args)

    orig_run_query = query.run_query
    query_results = {}

    def new_run_query(name, **context):
        qgen = orig_run_query(name, **context)

        for result in qgen:
            query_results[name] = result
            yield result

    query.run_query = new_run_query

    result = run_recipe(args.recipe, remainder, fmt='json')
    test = {
        'recipe': args.recipe,
        'args': remainder,
        'queries': query_results,
        'expected': result,
    }

    path = os.path.join(test_dir, '{}.test'.format(args.recipe))
    with open(path, 'a') as fh:
        yaml.dump(test, fh)
