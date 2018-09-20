from __future__ import print_function, absolute_import

import importlib
import logging
import os
from argparse import ArgumentParser

from six import string_types

from adr.formatter import all_formatters

log = logging.getLogger('adr')
here = os.path.abspath(os.path.dirname(__file__))

RECIPE_DIR = os.path.join(here, 'recipes')

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
    """Given a recipe, calls the appropriate query and returns the result.

    The provided recipe name is used to make a call to the modules.

    :param str recipe: name of the recipe to be run.
    :param list args: remainder arguments that were unparsed.
    :param str fmt: output format.
    :returns: string
    """
    modname = '.recipes.{}'.format(recipe)
    mod = importlib.import_module(modname, package='adr')
    output = mod.run(args)

    if isinstance(fmt, string_types):
        fmt = all_formatters[fmt]

    log.debug("Result:")
    return fmt(output)
