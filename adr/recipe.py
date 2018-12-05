from __future__ import print_function, absolute_import

import importlib
import logging
import os

from .query import run_query, load_query_context
from argparse import ArgumentParser
from adr.formatter import all_formatters
from .errors import MissingDataError
from adr import context
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


def set_config(config):
    global G_CONFIG
    G_CONFIG = config


def set_query_context(query_args):
    global G_CONTEXT
    G_CONTEXT = vars(query_args)


def execute_query(query_name, override_context=None):
    """
    Run query
    Args:
        query_name (str): name of query
        override_context (list): updated context from previous query
    Returns: (str)

    """
    if not override_context:
        override_context = G_CONTEXT
    else:
        for key, value in G_CONTEXT:
            if not (key in override_context):
                override_context[key] = value
    return next(run_query(query_name, G_CONFIG, **override_context))["data"]


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


class StructureParser(ArgumentParser):
    def __init__(self, definitions):
        ArgumentParser.__init__(self)
        for name, definition in definitions.items():
            if len(definition) < 2:
                raise AttributeError("Definition of {} should be list of length 2".format(name))
            # Set destination from name
            definition[1]['dest'] = name
            self.add_argument(*definition[0], **definition[1])


def run_recipe(recipe, args, config):
    """Given a recipe, calls the appropriate query and returns the result.

    The provided recipe name is used to make a call to the modules.

    Args:
        recipe (str): name of the recipe to be run.
        args (list): remainder arguments that were unparsed.
        config (Configuration): config object.

    Returns:
        output (str): output after formatted.


    :param str recipe:
    :param list :
    :param Configuration config: .
    :returns: string
    """
    modname = '.recipes.{}'.format(recipe)
    mod = importlib.import_module(modname, package='adr')
    if recipe == 'config_durations':

        # Get queries and run_contexts by function
        if (hasattr(mod, 'get_queries')) and (hasattr(mod, 'get_run_args')):
            queries = mod.get_queries()
            run_contexts = mod.get_run_args()
        else:
            # try to extract automatically from run function
            queries, run_contexts = context.extract_arguments(mod.run, "execute_query")

        recipe_context_def = {}
        for query_name in set(queries):
            query_context_def = load_query_context(query_name)
            recipe_context_def.update(query_context_def)

        run_context_def = context.get_context_definitions(run_contexts)
        recipe_context_def.update(run_context_def)

        # get value of query parameters and post-processing parameters
        parsed_args = StructureParser(recipe_context_def).parse_args(args)
        set_config(config)
        # TODO: Split recipe_args into query_args and recipe_args while keep --help works correctly

        recipe_args = parsed_args
        set_query_context(recipe_args)

        try:
            output = mod.run(recipe_args)
        except MissingDataError:
            return "ActiveData didn\'t return any data."
    else:
        try:
            output = mod.run(args, config)
        except MissingDataError:
            return "ActiveData didn\'t return any data."

    if isinstance(config.fmt, str):
        fmt = all_formatters[config.fmt]

    log.debug("Result:")
    return fmt(output)
