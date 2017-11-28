from __future__ import print_function, absolute_import

import importlib
import logging
import os
import sys
from argparse import ArgumentParser

from six import string_types

from adr.formatter import all_formatters

here = os.path.abspath(os.path.dirname(__file__))

log = logging.getLogger('adr')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

RECIPE_DIR = os.path.join(here, 'recipes')


def run_recipe(recipe, args, fmt='table'):
    modname = '.recipes.{}'.format(recipe)
    mod = importlib.import_module(modname, package='adr')
    output = mod.run(args)

    if isinstance(fmt, string_types):
        fmt = all_formatters[fmt]

    log.debug("Result:")
    return fmt(output)


def cli(args=sys.argv[1:]):
    parser = ArgumentParser()
    parser.add_argument('recipes', nargs='*', help="Recipe(s) to run.")
    parser.add_argument('-l', '--list', action='store_true', default=False,
                        help="List available recipes.")
    parser.add_argument('-f', '--format', dest='fmt', default='table',
                        choices=all_formatters.keys(),
                        help="Format to print data in, defaults to 'table'.")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Print the query and other debugging information.")
    args, remainder = parser.parse_known_args(args)

    if args.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    all_recipes = [os.path.splitext(p)[0] for p in os.listdir(RECIPE_DIR)
                   if p.endswith('.py') if p != '__init__.py']

    if args.list:
        log.info('\n'.join(sorted(all_recipes)))
        return

    for recipe in args.recipes:
        if recipe not in all_recipes:
            log.error("recipe '{}' not found!".format(recipe))
            continue
        print(run_recipe(recipe, remainder, fmt=args.fmt))


if __name__ == '__main__':
    sys.exit(cli())
