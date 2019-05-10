from __future__ import absolute_import, print_function

import json
import logging
import os
import sys
from argparse import ArgumentParser
from collections import OrderedDict
from copy import deepcopy

import yaml

from adr import config, query
from adr.recipe import run_recipe

here = os.path.abspath(os.path.dirname(__file__))
test_dir = os.path.join(here, os.pardir, os.pardir, 'test', 'recipe_tests')

log = logging.getLogger('adr')


def cli(args=sys.argv[1:]):
    parser = ArgumentParser()
    parser.add_argument('recipe',
                        help='Recipe to generate test for')
    args, remainder = parser.parse_known_args(args)

    orig_run_query = query.run_query
    query_results = []

    def new_run_query(name, args):
        args.limit = 10
        result = orig_run_query(name, args)
        mock_result = deepcopy(result)
        mock_result.pop('meta')
        query_results.append(mock_result)
        return result

    query.run_query = new_run_query
    config.fmt = 'json'

    result = run_recipe(args.recipe, remainder)
    test = OrderedDict()
    test['recipe'] = args.recipe
    test['args'] = remainder
    test['queries'] = query_results
    test['expected'] = json.loads(result)

    # get pyyaml to preserve ordering of dict keys
    def represent_ordereddict(dumper, data):
        value = []
        for item_key, item_value in data.items():
            node_key = dumper.represent_data(item_key)
            node_value = dumper.represent_data(item_value)

            value.append((node_key, node_value))
        return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)
    yaml.add_representer(OrderedDict, represent_ordereddict)

    path = os.path.join(test_dir, '{}.test'.format(args.recipe))
    with open(path, 'a') as fh:
        yaml.dump(test, fh)
