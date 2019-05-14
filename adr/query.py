from __future__ import absolute_import, print_function

import datetime
import json
import logging
import os
import time
from argparse import Namespace

import jsone
import requests
import yaml

from adr import config, context, sources
from adr.context import RequestParser
from adr.errors import MissingDataError
from adr.formatter import all_formatters

log = logging.getLogger('adr')
here = os.path.abspath(os.path.dirname(__file__))


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
        log.debug("JSON Response:")
        log.debug(json.dumps(json_response, indent=2))
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
    with open(sources.get(name, query=True)) as fh:
        query = yaml.load(fh, Loader=yaml.SafeLoader)
        # Remove the context
        if "context" in query:
            query.pop("context")
        return query


def load_query_context(name, add_contexts=[]):
    """
    Get query context from yaml file.
    Args:
        name (str): name of query
        add_contexts (list): additional contexts if needed
    Returns:
        query_contexts (list): mixed array of strings (name of common contexts)
         and dictionaries (full definition of specific contexts)
    """

    with open(sources.get(name, query=True)) as fh:
        query = yaml.load(fh, Loader=yaml.SafeLoader)
        # Extract query and context
        specific_contexts = query.pop("context") if "context" in query else {}
        contexts = context.extract_context_names(query)
        contexts.update(add_contexts)
        query_contexts = context.get_context_definitions(contexts, specific_contexts)

        return query_contexts


def run_query(name, args):
    """Loads and runs the specified query, yielding the result.

    Given name of a query, this method will first read the query
    from a .query file corresponding to the name.

    After queries are loaded, each query to be run is inspected
    and overridden if the provided context has values for limit.

    The actual call to the ActiveData endpoint is encapsulated
    inside the query_activedata method.

    :param str name: name of the query file to be loaded.
    :param Namespace args: namespace of ActiveData configs.
    :return str: json-formatted string.
    """
    context = vars(args)
    query = load_query(name)

    if 'limit' not in query and 'limit' in context:
        query['limit'] = context['limit']
    if 'format' not in query and 'format' in context:
        query['format'] = context['format']
    if config.debug:
        query['meta'] = {"save": True}

    query = jsone.render(query, context)
    query_str = json.dumps(query, indent=2, separators=(',', ':'))

    # translate "all" to a null value (which ActiveData will treat as all)
    query_str = query_str.replace('"all"', 'null')
    query_hash = config.cache._hash(query_str)

    key = f"run_query.{name}.{query_hash}"
    if config.cache.has(key):
        log.debug(f"Loading query {name} from cache")
        return config.cache.get(key)

    log.debug(f"Running query {name}:\n{query_str}")
    result = query_activedata(query_str, config.url)

    config.cache.put(key, result, 60)
    return result


def format_query(query, remainder=[]):
    """Takes the output of the ActiveData query and performs formatting.

    The result(s) from a query call to ActiveData is returned,
    which is then formatted as per the fmt argument.

    :param name query: name of the query file to be run.
    :param remainder: user contexts
    """
    if isinstance(config.fmt, str):
        fmt = all_formatters[config.fmt]

    query_context = load_query_context(query, ["format"])
    args = vars(RequestParser(query_context).parse_args(remainder))

    for key, value in query_context.items():
        if 'default' in value:
            args.setdefault(key, value['default'])

    result = run_query(query, Namespace(**args))
    data = result['data']
    debug_url = None
    if 'saved_as' in result['meta']:
        query_id = result['meta']['saved_as']
        debug_url = config.debug_url.format(query_id)

    if config.fmt == 'json':
        return fmt(result), debug_url

    if 'edges' in result:
        for edge in result['edges']:
            if 'partitions' in edge['domain']:
                data[edge['name']] = [p['name'] for p in edge['domain']['partitions']]

    if 'header' in result:
        data.insert(0, result['header'])

    return fmt(data), debug_url
