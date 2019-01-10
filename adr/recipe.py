from __future__ import print_function, absolute_import

import importlib
import logging
import os

from docutils.core import publish_parts
from .query import load_query_context
from argparse import ArgumentParser, Namespace
from adr.formatter import all_formatters
from .errors import MissingDataError
from adr import context
log = logging.getLogger('adr')
here = os.path.abspath(os.path.dirname(__file__))

RECIPE_DIR = os.path.join(here, 'recipes')


class RecipeParser(ArgumentParser):

    def __init__(self, definitions):
        ArgumentParser.__init__(self)

        for name, definition in definitions.items():
            # definition of a context: {name: [[],{}]}
            if isinstance(definition, dict):
                self.add_argument(name, **definition)
            elif len(definition) >= 2:
                # Set destination from name
                definition[1]['dest'] = name
                self.add_argument(*definition[0], **definition[1])
            else:
                raise AttributeError("Definition of {} should be list of length 2".format(name))


def get_recipe_contexts(recipe, mod=None):
    """
    Extract list of recipe context definition from the recipe file and related query files
    Args:
        recipe (str): name of recipe
        mod (module): module of recipe
    Returns:
        recipe_context_def (dict): definition of all contexts needed for recipe
    """
    if not mod:
        modname = '.recipes.{}'.format(recipe)
        mod = importlib.import_module(modname, package='adr')

    # try to extract name of query and run contexts automatically from run function
    queries, run_contexts = context.extract_arguments(mod.run, "run_query")

    # get name of queries and/or run contexts by function
    if hasattr(mod, 'QUERRY_LIST'):
        queries = mod.QUERRY_LIST
    if hasattr(mod, 'RUN_CONTEXTS'):
        run_contexts = mod.RUN_CONTEXTS

    # get full definition of all contexts needed for recipe
    recipe_context_def = {}
    for query_name in set(queries):
        query_context_def = load_query_context(query_name)
        recipe_context_def.update(query_context_def)

    run_context_def = context.get_context_definitions(run_contexts)
    recipe_context_def.update(run_context_def)

    return recipe_context_def


def run_recipe(recipe, args, config, from_cli=True):
    """Given a recipe, calls the appropriate query and returns the result.

    The provided recipe name is used to make a call to the modules.

    Args:
        recipe (str): name of the recipe to be run.
        args (list): remainder arguments that were unparsed.
        config (Configuration): config object.
        from_cli (bool): true if run recipe from cli
    Returns:
        output (str): output after formatted.

    """

    modname = '.recipes.{}'.format(recipe)
    mod = importlib.import_module(modname, package='adr')

    recipe_context_def = get_recipe_contexts(recipe, mod)

    if from_cli:
        parsed_args = vars(RecipeParser(recipe_context_def).parse_args(args))
    else:
        parsed_args = args

    try:
        # output = mod.run(Namespace(**run_args))
        output = mod.run(config, Namespace(**parsed_args))
    except MissingDataError:
        return "ActiveData didn\'t return any data."

    if isinstance(config.fmt, str):
        fmt = all_formatters[config.fmt]

    log.debug("Result:")
    return fmt(output)


def get_docstring(recipe):
    """
    Get docstring of a recipe
    Args:
        recipe(str): name of recipe
    Result:
        html (transformed from rst)
    """
    modname = '.recipes.{}'.format(recipe)
    mod = importlib.import_module(modname, package='adr')
    return publish_parts(mod.__doc__, writer_name='html')['html_body']


def is_fail(recipe):
    modname = '.recipes.{}'.format(recipe)
    mod = importlib.import_module(modname, package='adr')
    return hasattr(mod, "is_fail") and mod.is_fail()
