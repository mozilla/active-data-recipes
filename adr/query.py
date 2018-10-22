from __future__ import print_function, absolute_import

import datetime
import json
import logging
import os
import jsone
import requests
import yaml
from six import string_types
from adr.formatter import all_formatters
from adr.errors import MissingDataError

log = logging.getLogger('adr')
here = os.path.abspath(os.path.dirname(__file__))


QUERY_DIR = os.path.join(here, 'queries')
FAKE_CONTEXT = {
    'branch': 'mozilla-central',
    'branches': ['mozilla-central'],
    'from_date': 'today-week',
    'to_date': 'today',
    'rev': '5b33b070378a',
    'path': 'dom/indexedDB',
    'limit': 10,
    'format': 'table',
}


def format_date(timestamp, interval='day'):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')


def query_activedata(query, url):
    """Runs the provided query against the ActiveData endpoint.

    :param dict query: yaml-formatted query to be run.
    :param str url: url to run query
    :returns str: json-formatted string.
    """
    response = requests.post(url,
                             data=query,
                             stream=True)

    if response.status_code != 200:
        print(response.content)
        raise MissingDataError("ActiveData didn't return any data.")

    json_response = response.json()
    if not json_response.get('data'):
        raise MissingDataError("ActiveData didn't return any data.")
    return json_response


def load_query(name):
    """Loads the specified query from the disk.

    Given name of a query, the file is opened using a monad.

    No checks are necessary as adr.cli:query_handler filters
    requests for queries that do not exist.

    Generator is created to the calling method to handle cases
    where a single query file contains more than one query.

    :param str name: name of the query to be run.
    :yields dict query: dictionary representation of yaml query.
    """
    with open(os.path.join(QUERY_DIR, name+'.query')) as fh:
        for query in yaml.load_all(fh):
            yield query


def run_query(name, config, **context):
    """Loads and runs the specified query, yielding the result.

    Given name of a query, this method will first read the query
    from a .query file corresponding to the name.

    After queries are loaded, each query to be run is inspected
    and overridden if the provided context has values for limit.

    The actual call to the ActiveData endpoint is encapsulated
    inside the query_activedata method.

    :param str name: name of the query file to be loaded.
    :param Configuration config: config object.
    :param dict context: dictionary of ActiveData configs.
    :yields str: json-formatted string.
    """
    for query in load_query(name):
        # If limit is in the context, override the queries' value. We do this
        # to keep the results down to a sane level when testing queries.
        if 'limit' in context:
            query['limit'] = context['limit']
        if 'format' in context:
            query['format'] = context['format']
        if config.debug:
            query['meta'] = {"save": True}

        query = jsone.render(query, context)
        query_str = json.dumps(query, indent=2, separators=(',', ':'))
        log.debug("Running query {}:\n{}".format(name, query_str))
        yield query_activedata(query_str, config.url)


def format_query(query, config):
    """Takes the output of the ActiveData query and performs formatting.

    The result(s) from a query call to ActiveData is returned,
    which is then formatted as per the fmt argument.

    :param name query: name of the query file to be run.
    :param Configuration config: config object.
    """
    if isinstance(config.fmt, string_types):
        fmt = all_formatters[config.fmt]

    for result in run_query(query, config, **FAKE_CONTEXT):
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
