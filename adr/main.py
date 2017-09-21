from __future__ import print_function, absolute_import

import os
import sys
from argparse import ArgumentParser

here = os.path.abspath(os.path.dirname(__file__))
RECIPE_DIR = os.path.join(here, 'recipes')


def run_recipe(name, args):


class RecipeParser(ArgumentParser):

    def __init__(self, *args, **kwargs):
        ArgumentParser.__init__(*args, **kwargs)

        self.add_argument('recipe', nargs='?', help="Recipe to run.")
        self.add_argument('-l', '--list', action='store_true', default=False,
                          help="List available recipes.")


def cli(args=sys.argv[1:]):
    parser = RecipeParser()
    args, remainder = parser.parse_known_args(args)

    if args.list:
        recipes = os.listdir(RECIPE_DIR)
        return

    for path in sorted(os.listdir(RECIPE_DIR)):
        name = os.path.splitext(path)[0]
        if args.list:
            print(name)
            continue

        if args.recipe != name:
            continue

        mod = __import__('recipes.{}'.format(args.recipe))
        return mod.run(remainder)

    if not args.list:
        print("recipe '{}' not found!".format(args.recipe))


if __name__ == '__main__':
    sys.exit(cli())
