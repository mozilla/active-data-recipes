from __future__ import print_function, absolute_import

import importlib
import logging
import os
from argparse import ArgumentParser

from six import string_types

from adr.formatter import all_formatters
from .errors import MissingDataError

log = logging.getLogger('adr')
here = os.path.abspath(os.path.dirname(__file__))

RECIPE_DIR = os.path.join(here, 'recipes')

ARGUMENT_GROUPS = {
    'branch': [
        [['-B', '--branch'],
         {'default': ['mozilla-central'],
          'action': 'append',
          'help': "Branches to query results from",
          }],
    ],
    'build': [
        [['-b', '--build-type'],
         {'default': 'opt',
          'help': "Build type (default: opt)",
          }],
    ],
    'date': [
        [['--from'],
         {'dest': 'from_date',
          'default': 'today-week',
          'help': "Starting date to pull data from, defaults "
                  "to a week ago",
          }],
        [['--to'],
         {'dest': 'to_date',
          'default': 'eod',  # end of day
          'help': "Ending date to pull data from, defaults "
                  "to now",
          }],
    ],
    'path': [
        [['--path'],
         {'required': True,
          'help': "Path relative to repository root (file or directory)",
          }],
    ],
    'platform': [
        [['-p', '--platform'],
         {'default': 'windows10-64',
          'help': "Platform to limit results to (default: windows10-64)",
          }],
    ],
    'rev': [
        [['-r', '--revision'],
         {'dest': 'rev',
          'required': True,
          'help': "Revision to limit results to",
          }],
    ],
    'test': [
        [['-t', '--test'],
         {'required': True,
          'dest': 'test_name',
          'help': "Path to a test file",
          }],
    ],
}
"""
These are commonly used arguments which can be re-used. They are shared to
provide a consistent CLI across recipes.
"""


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


def run_recipe(recipe, args, config):
    """Given a recipe, calls the appropriate query and returns the result.

    The provided recipe name is used to make a call to the modules.

    :param str recipe: name of the recipe to be run.
    :param list args: remainder arguments that were unparsed.
    :param Configuration config: config object.
    :returns: string
    """
    modname = '.recipes.{}'.format(recipe)
    mod = importlib.import_module(modname, package='adr')
    try:
        output = mod.run(args, config)
    except MissingDataError:
        return "ActiveData didn\'t return any data."

    if isinstance(config.fmt, string_types):
        fmt = all_formatters[config.fmt]

    log.debug("Result:")
    return fmt(output)
