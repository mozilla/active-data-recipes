from __future__ import print_function, absolute_import

import json
import logging
import os
import sys
from argparse import ArgumentParser
from collections import defaultdict
from copy import deepcopy

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
    query_results = defaultdict(list)

    def new_run_query(name, **context):
        context['limit'] = 10
        qgen = orig_run_query(name, **context)

        for result in qgen:
            mock_result = deepcopy(result)
            mock_result.pop('meta')
            query_results[name].append(mock_result)
            yield result

    query.run_query = new_run_query

    result = run_recipe(args.recipe, remainder, fmt='json')
    test = {
        'recipe': args.recipe,
        'args': remainder,
        'queries': dict(query_results),
        'expected': json.loads(result),
    }

    path = os.path.join(test_dir, '{}.test'.format(args.recipe))
    with open(path, 'a') as fh:
        yaml.dump(test, fh)
