from __future__ import absolute_import, print_function

import argparse
import logging
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

from adr import config, sources
from adr.formatter import all_formatters
from adr.query import format_query
from adr.recipe import run_recipe

here = Path(__file__).parent.resolve()

log = logging.getLogger('adr')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


class DefaultSubParser(argparse.ArgumentParser):
    __default_subparser = None

    def set_default_subparser(self, name):
        self.__default_subparser = name

    def _parse_known_args(self, arg_strings, *args, **kwargs):
        in_args = set(arg_strings)
        d_sp = self.__default_subparser
        if d_sp is not None and not {'-h', '--help'}.intersection(in_args):
            for x in self._subparsers._actions:
                subparser_found = (
                    isinstance(x, argparse._SubParsersAction) and
                    in_args.intersection(x._name_parser_map.keys())
                )
                if subparser_found:
                    break
            else:
                # insert default in first position, this implies no
                # global options without a sub_parsers specified
                arg_strings = [d_sp] + arg_strings

        return super(DefaultSubParser, self)._parse_known_args(
            arg_strings, *args, **kwargs
        )


def get_parser():
    parser = DefaultSubParser()
    subparsers = parser.add_subparsers()

    def add_common_args(parser):
        parser.add_argument('-f', '--format', dest='fmt', choices=all_formatters.keys(),
                            help="Format to print data in, defaults to 'table'.")
        parser.add_argument('-v', '--verbose', action='store_true',
                            help="Print the query and other debugging information.")
        parser.add_argument('-u', '--url',  help="ActiveData endpoint URL.")
        parser.add_argument('-o', '--output-file', type=str,
                            help="Full path of the output file")
        parser.set_defaults(**config.DEFAULTS)

    # recipe subcommand
    recipe = subparsers.add_parser('recipe')
    recipe.add_argument('recipe', help="Name of the recipe to run (or 'list' to "
                                       "view all available recipes).")
    add_common_args(recipe)
    recipe.set_defaults(func=handle_recipe)

    # query subcommand
    query = subparsers.add_parser('query')
    query.add_argument('query', help="Name of the query to run (or 'list' to "
                                     "view all available queries).")
    query.add_argument('-d', '--debug', action='store_true',
                       help="Open a query in ActiveData query tool.")
    add_common_args(query)
    query.set_defaults(func=handle_query)

    # list subcommand
    listcmd = subparsers.add_parser('list', help="List the available recipes (or queries).")
    listcmd.add_argument('subcommand', nargs='?', choices=['recipe', 'query'], default='recipe')
    add_common_args(listcmd)
    listcmd.set_defaults(func=handle_list)

    # config subcommand
    configcmd = subparsers.add_parser('config', help="Print active configuration.")
    configcmd.add_argument("-e", "--edit", action="store", nargs="?",
                           default=False, help="Open the config file in an editor.")
    configcmd.set_defaults(func=handle_config)

    parser.set_default_subparser('recipe')
    return parser


def handle_config(remainder):
    if config.edit is False:
        print(config.dump())
        return

    editor = None
    if config.edit is not None:
        editor = config.edit
    elif "VISUAL" in os.environ:
        editor = os.environ["VISUAL"]
    elif "EDITOR" in os.environ:
        editor = os.environ["EDITOR"]
    else:
        print('Unable to determine editor; please specify a binary')

    if editor:
        subprocess.Popen([editor, config.path]).wait()


def handle_list(remainder):
    key = 'queries' if config.subcommand == 'query' else 'recipes'
    lines = []
    for source in sources:
        if config.verbose:
            attr = getattr(source, f"{config.subcommand}_dir")
            lines.append(f"\n{key.capitalize()} from {attr}:")

        items = sorted(getattr(source, key))
        if config.verbose:
            items = ['  ' + i for i in items]
        lines.extend(items)

    log.info('\n'.join(lines).strip())


def handle_recipe(remainder):
    if config.recipe not in sources.recipes:
        log.error("recipe '{}' not found!".format(config.recipe))
        return

    data = run_recipe(config.recipe, remainder)

    if config.output_file:
        print(data, file=open(config.output_file, 'w'))
    return data


def handle_query(remainder):
    if config.query not in sources.queries:
        log.error("query '{}' not found!".format(config.query))
        return

    data, url = format_query(config.query, remainder)
    if config.output_file:
        print(data, file=open(config.output_file, 'w'))

    if url:
        time.sleep(2)
        webbrowser.open(url, new=2)
    return data


def main(args=sys.argv[1:]):
    """Entry point for the adr module.

    Supported usage:

    $ adr recipe <recipe_name>
    $ adr query <query_name>
    $ adr <recipe_name>
    """
    # Load config from file and override with command line.
    parser = get_parser()

    # Parse all arguments, then pass to appropriate handler.
    args, remainder = parser.parse_known_args()
    handler = args.func
    delattr(args, 'func')

    config.merge(vars(args))
    log.setLevel(logging.DEBUG) if config.verbose else log.setLevel(logging.INFO)

    result = handler(remainder)
    if result is not None:
        print(result)


if __name__ == '__main__':
    sys.exit(main())
