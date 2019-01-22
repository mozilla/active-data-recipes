from __future__ import absolute_import, print_function

import datetime
import json
import logging
import os
import time
from argparse import ArgumentParser, Namespace

import jsone
import requests
import yaml

from adr import context
from adr.errors import MissingDataError
from adr.formatter import all_formatters

log = logging.getLogger('adr')
here = os.path.abspath(os.path.dirname(__file__))


QUERY_DIR = os.path.join(here, 'queries')


class QueryParser(ArgumentParser):

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


def format_date(timestamp, interval='day'):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')


def query_activedata(query, url):
    """Runs the provided query against the ActiveData endpoint.

    :param dict query: yaml-formatted query to be run.
    :param str url: url to run query
    :returns str: json-formatted string.
    """
    start_time = time.time()
    response = requests.post(url,
                             data=query,
                             stream=True)
    log.debug("Query execution time: "
              + "{:.3f} ms".format((time.time() - start_time) * 1000.0))

    if response.status_code != 200:
        try:
            print(json.dumps(response.json(), indent=2))
        except ValueError:
            print(response.text)
        response.raise_for_status()

    json_response = response.json()
    if not json_response.get('data'):
        raise MissingDataError("ActiveData didn't return any data.")
    return json_response


def load_query(name):
    """Loads the specified query from the disk.

    No checks are necessary as adr.cli:query_handler filters
    requests for queries that do not exist.

    Args:
        name (str): name of the query to be run.

    Results:
        dict query: dictionary representation of yaml query
        (exclude the context).
    """
    with open(os.path.join(QUERY_DIR, name + '.query')) as fh:
        query = yaml.load(fh)
        # Remove the context
        if "context" in query:
            query.pop("context")
        return query


def load_query_context(name):
    """
    Get query context from yaml file.
    Args:
        name (str): name of query
    Returns:
        query_contexts (list): mixed array of strings (name of common contexts)
         and dictionaries (full definition of specific contexts)
    """

    with open(os.path.join(QUERY_DIR, name + '.query')) as fh:
        query = yaml.load(fh)
        # Extract query and context
        specific_contexts = query.pop("context") if "context" in query else {}
        contexts = context.extract_context_names(query)
        query_contexts = context.get_context_definitions(contexts, specific_contexts)
        return query_contexts


def run_query(name, config, args):
    """Loads and runs the specified query, yielding the result.

    Given name of a query, this method will first read the query
    from a .query file corresponding to the name.

    After queries are loaded, each query to be run is inspected
    and overridden if the provided context has values for limit.

    The actual call to the ActiveData endpoint is encapsulated
    inside the query_activedata method.

    :param str name: name of the query file to be loaded.
    :param Configuration config: config object.
    :param Namespace args: namespace of ActiveData configs.
    :return str: json-formatted string.
    """

    context = vars(args)
    query = load_query(name)

    if 'limit' in context:
        query['limit'] = context['limit']
    if 'format' in context:
        query['format'] = context['format']
    if config.debug:
        query['meta'] = {"save": True}

    query = jsone.render(query, context)
    query_str = json.dumps(query, indent=2, separators=(',', ':'))

    # translate "all" to a null value (which ActiveData will treat as all)
    query_str = query_str.replace('"all"', 'null')

    log.debug("Running query {}:\n{}".format(name, query_str))
    return query_activedata(query_str, config.url)


def format_query(query, config, remainder=[]):
    """Takes the output of the ActiveData query and performs formatting.

    The result(s) from a query call to ActiveData is returned,
    which is then formatted as per the fmt argument.

    :param name query: name of the query file to be run.
    :param remainder: user contexts
    :param Configuration config: config object.
    """
    if isinstance(config.fmt, str):
        fmt = all_formatters[config.fmt]

    query_context = load_query_context(query)
    args = vars(QueryParser(query_context).parse_args(remainder))

    # get contexts from cli, if not get default value
    real_contexts = {}

    for key, value in query_context.items():
        for name in value[0]:
            if name in args:
                real_contexts[key] = args[name]
                pass
            elif 'default' in value[1]:
                real_contexts[key] = value[1]['default']

    result = run_query(query, config, Namespace(**real_contexts))
    data = result['data']
    debug_url = None
    if 'saved_as' in result['meta']:
        query_id = result['meta']['saved_as']
        debug_url = config.build_debug_url(query_id)

    if config.fmt == 'json':
        return fmt(result), debug_url

    if 'edges' in result:
        for edge in result['edges']:
            if 'partitions' in edge['domain']:
                data[edge['name']] = [p['name'] for p in edge['domain']['partitions']]

    if 'header' in result:
        data.insert(0, result['header'])

    return fmt(data), debug_url
