"""
Full definition of a context:
'key': [[--long-form, -short-form],
         {'type': int/str/bool/date/...,
          'default': default_value,
          'choices': range,
          'action': 'append',
          'required': True/False,
          'hidden': True/False,
          'help': help_text
         }]
]
The display order of contexts on webapp follows the order of contexts in COMMON_CONTEXTS
If action is append, this context on webapp will be multiple-choices
Define context in query/recipe:
1. If define a new context (not in COMMON_CONTEXTS), follow full definition template
2. If override some attribute of an existing context, use override function
Attribute "hidden": if a context of a recipe has "hidden=True",
                    it will not be listed on webapp and cli
"""
import ast
import collections
import inspect
from argparse import ArgumentParser, SUPPRESS
from copy import deepcopy

from jsone.interpreter import ExpressionEvaluator
from jsone.prattparser import prefix
from orderedset import OrderedSet


def validdatetime(string):
    return string


COMMON_CONTEXTS = collections.OrderedDict()
COMMON_CONTEXTS['attribute'] = [['--at'],
                                {'nargs': '?',
                                 'default': None,
                                 'help': "Display values of specified attribute within --table."}]
COMMON_CONTEXTS['branches'] = [['-B', '--branch'],
                               {'default': ["mozilla-central"],
                                'type': str,
                                'choices': ["mozilla-central", "mozilla-inbound", "autoland",
                                            "beta", "release"],
                                'action': 'append',
                                'help': "Branches to query results from",
                                }]
COMMON_CONTEXTS['build_type'] = [['-b', '--build-type'],
                                 {'default': 'opt',
                                  'help': "Build type (default: opt)",
                                  }]
COMMON_CONTEXTS['format'] = [['--format'],
                             {'type': str,
                              'default': 'table',
                              'choices': ['table', 'json'],
                              'help': "format of result"
                              }]
COMMON_CONTEXTS['groupby'] = [['--groupby'],
                              {'default': 'result.test'
                               }]
COMMON_CONTEXTS['path'] = [['--path'],
                           {'default': 'dom/indexedDB',
                            'help': "Path relative to repository root (file or directory)",
                            }]
COMMON_CONTEXTS['platform'] = [['-p', '--platform'],
                               {'default': 'windows10-64',
                                'help': "Platform to limit results to (default: windows10-64)",
                                }]
COMMON_CONTEXTS['platform_config'] = [['--platform-config'], {'default': 'test-'}]
COMMON_CONTEXTS['pushid'] = [['--push'],
                             {'type': int,
                              'required': True,
                              'help': "id of push to unittest"
                              }]
COMMON_CONTEXTS['limit'] = [['--limit'],
                            {'type': int,
                             'default': 10,
                             'help': "limit the number of rows in result"
                             }]

COMMON_CONTEXTS['rev'] = [['-r', '--revision', '--rev'],
                          {'default': '5b33b070378a',
                           'help': "Revision to limit results to",
                           }]
COMMON_CONTEXTS['result'] = [['--result'], {'default': "F"}]
COMMON_CONTEXTS['sort_key'] = [['--sort-key'],
                               {'type': int,
                                'default': 4,
                                'help': "Key to sort on (int, 0-based index)",
                                }]
COMMON_CONTEXTS['table'] = [['--table'],
                            {'default': None,
                             'help': "Table to inspect."}]
COMMON_CONTEXTS['test_name'] = [['-t', '--test'],
                                {'default': '',
                                 'help': "Path to a test file",
                                 }]
COMMON_CONTEXTS['from_date'] = [['--from'],
                                {'default': 'today-week',
                                 'type': validdatetime,
                                 'help': "Starting date to pull data from, defaults "
                                         "to a week ago",
                                 }]
COMMON_CONTEXTS['to_date'] = [['--to'],
                              {'default': 'eod',  # end of day
                               'type': validdatetime,
                               'help': "Ending date to pull data from, defaults "
                                       "to end of day",
                               }]
"""
COMMON_CONTEXTS are commonly used arguments which can be re-used. They are shared to
provide a consistent CLI across recipes/queries. Ordered by alphabet.
"""


class RequestParser(ArgumentParser):

    def __init__(self, definitions):
        ArgumentParser.__init__(self)

        for name, definition in definitions.items():
            # definition of a context: {name: [[],{}]}
            if isinstance(definition, dict):
                self.add_argument(name, **definition)
            elif len(definition) >= 2:
                # Set destination from name
                definition[1]['dest'] = name
                if definition[1].get('hidden'):
                    del definition[1]['hidden']
                    definition[1]['help'] = SUPPRESS
                elif not('default' in definition[1]):
                    # if a context is not hidden and has no default value
                    definition[1]['required'] = True
                self.add_argument(*definition[0], **definition[1])
            else:
                raise AttributeError("Definition of {} should be list of length 2".format(name))


def override(name, **overrides):
    """Use a common context and override some of the argparse parameters.

    Args:
        name (str): Name of the common context to wrap.
        overrides (kwargs): Overrides the specified parameters to
                           argparse.add_argument().

    Returns:
        A context entry with the updated values.
    """
    assert name in COMMON_CONTEXTS

    context = deepcopy(COMMON_CONTEXTS[name])
    context[1].update(**overrides)
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
        specific_defs (OrderedDict): specific definitions of contexts not in COMMON_CONTEXTS

    Returns:
        result (dict): a full dictionary of context definitions,
     each context definition has a name as key and attributes as value
    """

    result = collections.OrderedDict()

    for item in definitions:
        if isinstance(item, dict):
            result.update(item)
        elif isinstance(item, str):
            # if an item appears in both specific_defs and COMMON_CONTEXT,
            # get from specific_defs
            if item in specific_defs:
                result.setdefault(item, specific_defs[item])
            elif item in COMMON_CONTEXTS:
                result.setdefault(item, COMMON_CONTEXTS[item])
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
