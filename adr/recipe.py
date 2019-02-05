from __future__ import absolute_import, print_function

import collections
import importlib
import logging
import os
from argparse import Namespace

from docutils.core import publish_parts

from adr import context
from adr.errors import MissingDataError
from adr.formatter import all_formatters
from adr.query import RequestParser, load_query_context

log = logging.getLogger('adr')
here = os.path.abspath(os.path.dirname(__file__))

RECIPE_DIR = os.path.join(here, 'recipes')


def get_recipe_contexts(recipe, mod=None):
    """
    Extract list of recipe context definition from the recipe file and related query files
    Args:
        recipe (str): name of recipe
        mod (module): module of recipe
    Returns:
        result (dict): definition of all contexts needed for recipe
    """
    if not mod:
        modname = '.recipes.{}'.format(recipe)
        mod = importlib.import_module(modname, package='adr')

    # try to extract name of query and run contexts automatically from run function
    queries, run_contexts = context.extract_arguments(mod.run, "run_query")

    specific_contexts = {}
    if hasattr(mod, 'RUN_CONTEXTS'):
        context_info = mod.RUN_CONTEXTS
        for item in context_info:
            specific_contexts.update(item)

    # get full definition of all contexts needed for recipe
    recipe_context_def = {}
    for query_name in set(queries):
        query_context_def = load_query_context(query_name)
        recipe_context_def.update(query_context_def)

    run_context_def = context.get_context_definitions(run_contexts, specific_contexts)
    recipe_context_def.update(run_context_def)

    result = collections.OrderedDict()
    result = context.sort_context_dict(recipe_context_def)
    return result


def get_module(name):
    """
    Get module of a recipe
    Args:
        name (str): name of recipe
    :return: module
    """
    modname = '.recipes.{}'.format(name)
    mod = importlib.import_module(modname, package='adr')
    return mod


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

    mod = get_module(recipe)

    recipe_context_def = get_recipe_contexts(recipe, mod)

    if from_cli:
        parsed_args = vars(RequestParser(recipe_context_def).parse_args(args))
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
    mod = get_module(recipe)
    return publish_parts(mod.__doc__, writer_name='html')['html_body']


def is_fail(recipe):
    mod = get_module(recipe)
    return getattr(mod, "BROKEN", False)
