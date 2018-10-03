from __future__ import print_function, absolute_import

import logging
import os
import sys
import webbrowser
import time

from argparse import ArgumentParser

from adr.formatter import all_formatters
from adr.query import format_query
from adr.query import set_active_data_url
from adr.recipe import run_recipe

here = os.path.abspath(os.path.dirname(__file__))

log = logging.getLogger('adr')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

RECIPE_DIR = os.path.join(here, 'recipes')
QUERY_DIR = os.path.join(here, 'queries')


def query_handler(args, remainder):
    """Runs, formats and prints queries.

    All functionality remains same as adr.query:cli.

    :param Namespace args: Namespace object produced by main().
    :param list remainder: List of unknown arguments.
    """
    queries = [os.path.splitext(item)[0] for item in os.listdir(
        QUERY_DIR) if item.endswith('.query')]

    _set_logging_verbosity(args.verbose)

    if args.list:
        _list(queries)
    else:
        _check_tasks_exist(args.task)

    for query in args.task:
        if query not in queries:
            log.error("query '{}' not found!".format(query))
            continue
        data, url = format_query(query, args, fmt=args.fmt)
        print(data)
        if url:
            time.sleep(2)
            webbrowser.open(url, new=2)


def recipe_handler(args, remainder):
    """Runs recipes.

    All functionality remains the same as the deprecated adr.cli:cli.

    :param Namespace args: Namespace object produced by main().
    :param list remainder: List of unknown arguments.
    """
    recipes = [os.path.splitext(item)[0] for item in os.listdir(
               RECIPE_DIR) if item != '__init__.py' and item.endswith('.py')]

    _set_logging_verbosity(args.verbose)

    if args.list:
        _list(recipes)
    else:
        _check_tasks_exist(args.task)

    for recipe in args.task:
        if recipe not in recipes:
            log.error("recipe '{}' not found!".format(recipe))
            continue
        print(run_recipe(recipe, remainder, fmt=args.fmt))


def _build_parser_arguments(parser):
    """Builds the parser argument list.

    Given a ArgumentParser object, this method will populate the standard
    list of arguments.

    :param ArgumentParser parser: instance of an ArgumentParser.
    :returns: ArgumentParser
    """
    # optional arguments
    parser.add_argument('-l', '--list', action='store_true', default=False,
                        help="List available recipes.")
    parser.add_argument('-f', '--format', dest='fmt', default='table',
                        choices=all_formatters.keys(),
                        help="Format to print data in, defaults to 'table'.")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Print the query and other debugging information.")
    parser.add_argument('-u', '--url', default='http://activedata.allizom.org/query',
                        help="Endpoint URL")
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help="Open a query in ActiveData query tool.")
    # positional arguments
    parser.add_argument('task', nargs='*')
    return parser


def _check_tasks_exist(task):
    """Checks whether the tasks argument is populated.

    If no tasks are found, the program is terminated.

    :param list task: list of tasks to be run.
    """
    if len(task) == 0:
        sys.stdout.write('Please provide at least one recipe or query to run.\n')
        sys.exit()


def _list(items):
    """Runs the -l/--list command line action.

    :param list items: list of items that are to be printed to the console.
    :returns None
    """
    log.info('\n'.join(sorted(items)))
    return


def _set_logging_verbosity(is_verbose):
    """Runs the -v/--verbose command line action.

    Default logging level is INFO.

    If the -v flag is provided to adr, the logging level is set to DEBUG.

    :param bool is_verbose: Speciies if -v flag has been supplied when adr was invoked.
    """
    log.setLevel(logging.DEBUG) if is_verbose else log.setLevel(logging.INFO)


def main(args=sys.argv[1:]):
    """Entry point for the adr module.

    When the adr module is called, this method is run.

    The argument list is parsed, and the appropriate parser or subparser is created.

    Using the argument list, arguments are parsed and grouped into a Namespace object
    representing known arguments, and a remainder list representing unknown arguments.

    The method then calls the appropriate method for the action specified.

    Supported use cases:

    $ adr recipe <recipe_name>
    $ adr query <query_name>
    $ adr <recipe_name>

    :param list args: command-line arguments.
    """
    # create parsers and subparsers.
    parser = ArgumentParser(description='Runs adr recipes and/or queries.')

    # check that adr is invoked with at least a recipe or subcommand.
    _check_tasks_exist(args)

    # determine if subparser are necessary.
    if 'query' in args or 'recipe' in args:
        subparser = parser.add_subparsers()

    if args[0] != 'query':
        # if subcommand query is not specified, default to recipe.
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
    set_active_data_url(parsed_args.url)
    parsed_args.func(parsed_args, remainder)


if __name__ == '__main__':
    sys.exit(main())
