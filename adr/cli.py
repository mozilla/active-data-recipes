from __future__ import print_function, absolute_import

import importlib
import logging
import os
import sys
from argparse import ArgumentParser

from six import string_types

from adr.formatter import all_formatters
from adr.query import run_query

here = os.path.abspath(os.path.dirname(__file__))

log = logging.getLogger('adr')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

RECIPE_DIR = os.path.join(here, 'recipes')
QUERY_DIR = os.path.join(here, 'queries')

ARGUMENT_GROUPS = {
    'date': [
        [['--from'],
         {'dest': 'from_date',
          'default': 'now-week',
          'help': "Starting date to pull data from, defaults "
                  "to a week ago",
          }],
        [['--to'],
         {'dest': 'to_date',
          'default': 'now',
          'help': "Ending date to pull data from, defaults "
                  "to now",
          }],
    ],
}


class RecipeParser(ArgumentParser):
    arguments = []

    def __init__(self, *groups, **kwargs):
        ArgumentParser.__init__(self, **kwargs)

        for cli, kwargs in self.arguments:
            self.add_argument(*cli, **kwargs)

        for name in groups:
            group = self.add_argument_group("{} arguments".format(name))
            arguments = ARGUMENT_GROUPS[name]
            for cli, kwargs in arguments:
                group.add_argument(*cli, **kwargs)


def run_recipe(recipe, args, fmt='table'):
    modname = '.recipes.{}'.format(recipe)
    mod = importlib.import_module(modname, package='adr')
    output = mod.run(args)

    if isinstance(fmt, string_types):
        fmt = all_formatters[fmt]

    log.debug("Result:")
    return fmt(output)


def query_handler(args, remainder):
    queries = [os.path.splitext(item)[0] for item in os.listdir(
                 QUERY_DIR) if item.endswith('.query')]

    _set_logging_verbosity(args.verbose)

    if args.list:
        log.info('\n'.join(sorted(queries)))
        return

    _check_tasks_exist(args.task)

    fake_context = {
        'branch': 'mozilla-central',
        'branches': ['mozilla-central'],
        'from_date': 'now-week',
        'to_date': 'now',
        'rev': '5b33b070378a',
        'path': 'dom/indexedDB',
        'limit': 10,
        'format': 'table',
    }

    if isinstance(args.fmt, string_types):
        fmt = all_formatters[args.fmt]

    for task in args.task:
        for result in run_query(task, **fake_context):
            data = result['data']

            if args.fmt == 'json':
                print(fmt(result))
                return

            if 'edges' in result:
                for edge in result['edges']:
                    if 'partitions' in edge['domain']:
                        data[edge['name']] = [p['name'] for p in edge['domain']['partitions']]

            if 'header' in result:
                data.insert(0, result['header'])

            print(fmt(data))


def recipe_handler(args, remainder):
    recipes = [os.path.splitext(item)[0] for item in os.listdir(
               RECIPE_DIR) if item != '__init__.py' and item.endswith('.py')]

    _set_logging_verbosity(args.verbose)

    if args.list:
        log.info('\n'.join(sorted(recipes)))
        return

    _check_tasks_exist(args.task)

    for recipe in args.task:
        if recipe not in recipes:
            log.error("recipe '{}' not found!".format(recipe))
            continue
        print(run_recipe(recipe, remainder, fmt=args.fmt))


def _build_parser_arguments(parser):
    # optional arguments
    parser.add_argument('-l', '--list', action='store_true', default=False,
                        help="List available recipes.")
    parser.add_argument('-f', '--format', dest='fmt', default='table',
                        choices=all_formatters.keys(),
                        help="Format to print data in, defaults to 'table'.")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Print the query and other debugging information.")
    # positional arguments
    parser.add_argument('task', nargs='*', help='Task(s) to run.')
    return parser


def _set_logging_verbosity(is_verbose):
    log.setLevel(logging.DEBUG) if is_verbose else log.setLevel(logging.INFO)


def _check_tasks_exist(task):
    if len(task) == 0:
        sys.stdout.write('Please provide at least one recipe or query to run.\n')
        sys.exit()


def main(args=sys.argv[1:]):
    # create parsers and subparsers.
    parser = ArgumentParser(description='Runs adr recipes and/or queries.')

    if 'query' in args or 'recipe' in args:
        subparser = parser.add_subparsers()

    if args[0] != 'query':
        if args[0] == 'recipe':
            recipe_parser = subparser.add_parser('recipe', help='Recipe subcommand.')
            recipe_parser = _build_parser_arguments(recipe_parser)
        else:
            parser = _build_parser_arguments(parser)
        parser.set_defaults(func=recipe_handler)
    else:
        query_parser = subparser.add_parser('query', help='Query subcommand.')
        query_parser = _build_parser_arguments(query_parser)
        query_parser.set_defaults(func=query_handler)

    # parse all arguments, then pass to appropriate handler.
    parsed_args, remainder = parser.parse_known_args()
    parsed_args.func(parsed_args, remainder)


if __name__ == '__main__':
    sys.exit(main())
