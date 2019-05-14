import ast
import collections
import inspect
from argparse import ArgumentParser, SUPPRESS
from copy import deepcopy

import yaml
from jsone.interpreter import ExpressionEvaluator
from jsone.prattparser import prefix
from orderedset import OrderedSet

from adr import sources
from adr.util import memoize


def validdatetime(string):
    return string


@memoize
def load_shared_context():
    if not sources.active_source:
        return {}

    context_path = sources.active_source.recipe_dir / 'context.yml'
    if not context_path.is_file():
        return {}

    with open(context_path, 'r') as fh:
        context = yaml.load(fh, Loader=yaml.SafeLoader)

    for key, value in context.items():
        # transform 'type' key
        if 'type' in value:
            if value['type'] in globals():
                value['type'] = globals()[value['type']]
            elif value['type'] in __builtins__:
                value['type'] = __builtins__[value['type']]
    return context


class RequestParser(ArgumentParser):

    def __init__(self, definitions):
        ArgumentParser.__init__(self)

        for name, definition in definitions.items():
            definition.setdefault('dest', name)
            flags = definition.pop('flags', [])

            if definition.pop('hidden', None):
                definition['help'] = SUPPRESS

            self.add_argument(*flags, **definition)


def override(name, **overrides):
    """Use a common context and override some of the argparse parameters.

    Args:
        name (str): Name of the common context to wrap.
        overrides (kwargs): Overrides the specified parameters to
                           argparse.add_argument().

    Returns:
        A context entry with the updated values.
    """
    shared_context = load_shared_context()
    if not shared_context:
        return

    context = deepcopy(shared_context[name])
    context.update(**overrides)
    return {name: context}


class ContextExtractor(ExpressionEvaluator):
    """
    Context extractor is used in conjunction with extract_context_names
    to extract argument context as a token value
    """

    def __init__(self):
        # Init evaluator with fake empty context
        super(ContextExtractor, self).__init__({})
        self.infix_rules = super(ContextExtractor, self).infix_rules
        for k, v in super(ContextExtractor, self).prefix_rules.items():
            self.prefix_rules.setdefault(k, v)
        # Init empty context set
        self.contexts = OrderedSet()

    @prefix("identifier")
    def identifier(self, token, pc):
        """
        Get corresponding value for token
        In this function, we return the same token value without using context
        Args:
            token: token object
            pc: parse context

        Returns: same token value

        """
        self.contexts.add(token.value)
        return token.value

    def parse(self, expression):
        """
        Parse current expression, return contexts inside this expression
        Args:
            expression (str): expression

        Returns:
            set of contexts

        """
        self.contexts.clear()
        super(ContextExtractor, self).parse(expression)
        return self.contexts


G_ZEROCONTEXT_EVALUATOR = ContextExtractor()


def extract_context_names(query):
    """
    Extract contexts list from query object
    This is to mimic json-e render() function
    Given using only $eval in query
    Args:
        query (dict): query object to extract context

    Returns:
        contexts (set): set of context names

    """
    contexts = OrderedSet()
    if isinstance(query, dict):
        for k, v in query.items():
            if k == "$eval":
                contexts.update(G_ZEROCONTEXT_EVALUATOR.parse(v))
            else:
                contexts.update(extract_context_names(v))
    elif isinstance(query, list):
        for v in query:
            contexts.update(extract_context_names(v))

    return contexts


def get_context_definitions(definitions, specific_defs=collections.OrderedDict()):
    """
    Build full context definitions from list of contexts with pre-defined definitions

    Args:
        definitions (list): mixed array of string and context definitions
        specific_defs (OrderedDict): specific definitions of contexts not in the shared context

    Returns:
        result (dict): a full dictionary of context definitions,
     each context definition has a name as key and attributes as value
    """
    shared_context = load_shared_context()
    result = collections.OrderedDict()

    for item in definitions:
        if isinstance(item, dict):
            result.update(item)
        elif isinstance(item, str):
            # if an item appears in both specific_defs and shared_context,
            # get from specific_defs
            if item in specific_defs:
                result.setdefault(item, specific_defs[item])
            elif item in shared_context:
                result.setdefault(item, shared_context[item])
            else:
                # Still not found! bad definition
                raise AttributeError("Cannot find definition for context {}".format(item))
        else:
            raise TypeError("Only accept str/list, but found {}".format(type(item)))
    return result


def extract_arguments(func, call, members=None):
    """
    Extract children calls and arguments attributes from a function object
    Args:
        func(function object): function object to extract
        call(str): name of child function being called inside func
        members(list): extractor function with the found ast.Call,
                    default to get first string argument

    Returns:
        calls (set): set of extracted values
        attrs (set): set of attributes

    """
    module = inspect.getmodule(func)
    if not members:
        members = inspect.getmembers(module, inspect.isfunction)

    # Get source from function
    source = inspect.getsource(func)
    # Get ast tree for this source code
    root_node = ast.parse(source)
    if not isinstance(root_node, ast.Module) or not isinstance(root_node.body[0], ast.FunctionDef):
        raise AttributeError("Expect function definition")

    root_func = root_node.body[0]
    # Get root args, only support second arg
    # TODO: support multiple args fetching
    root_arg = root_func.args.args[0].arg if len(root_func.args.args) > 0 else None
    calls = set()
    attrs = set()
    # Walk through all descendants recursively
    for node in ast.walk(root_node):
        # Check for Call and Attribute
        # Attribute first
        if isinstance(node, ast.Attribute):
            if hasattr(node.value, 'id') and node.value.id == root_arg:
                attrs.add(node.attr)
            continue

        # Early termination if not Call node with Name function
        elif not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue

        if node.func.id == call:
            calls.add(node.args[0].s)
    return calls, attrs
