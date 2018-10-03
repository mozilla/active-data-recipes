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
import sys
if sys.version_info >= (3, 0):
    from urllib.parse import urlparse
elif sys.version_info < (3, 0) and sys.version_info >= (2, 5):
    from urlparse import urlparse

log = logging.getLogger('adr')
here = os.path.abspath(os.path.dirname(__file__))

ACTIVE_DATA_URL = "http://activedata.allizom.org/query"
DEBUG_URL = "{}://{}/tools/query.html#query_id={}"
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


def set_active_data_url(url):
    global ACTIVE_DATA_URL
    ACTIVE_DATA_URL = url


def query_activedata(query):
    """Runs the provided query against the ActiveData endpoint.

    :param dict query: yaml-formatted query to be run.
    :returns str: json-formatted string.
    """
    response = requests.post(ACTIVE_DATA_URL,
                             data=query,
                             stream=True)
    response.raise_for_status()
    return response.json()


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


def run_query(name, debug=False, **context):
    """Loads and runs the specified query, yielding the result.

    Given name of a query, this method will first read the query
    from a .query file corresponding to the name.

    After queries are loaded, each query to be run is inspected
    and overridden if the provided context has values for limit.

    The actual call to the ActiveData endpoint is encapsulated
    inside the query_activedata method.

    :param str name: name of the query file to be loaded.
    :param debug: enable debug mode.
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
        if debug:
            query['meta'] = {"save": True}

        query = jsone.render(query, context)
        query_str = json.dumps(query, indent=2, separators=(',', ':'))
        log.debug("Running query {}:\n{}".format(name, query_str))
        yield query_activedata(query_str)


def format_query(query, args, fmt='table'):
    """Takes the output of the ActiveData query and performs formatting.

    The result(s) from a query call to ActiveData is returned,
    which is then formatted as per the fmt argument.

    :param name query: name of the query file to be run.
    :param Namespace args: object derived from parsing arguments.
    :param str fmt: specifies the formatting of the output.
    """
    if isinstance(fmt, string_types):
        fmt = all_formatters[fmt]

    for result in run_query(query, args.debug, **FAKE_CONTEXT):
        data = result['data']
        url = None
        if 'saved_as' in result['meta']:
            query_id = result['meta']['saved_as']
            domain = urlparse(ACTIVE_DATA_URL)
            url = DEBUG_URL.format(domain.scheme, domain.netloc, query_id)

        if args.fmt == 'json':
            return fmt(result)

        if 'edges' in result:
            for edge in result['edges']:
                if 'partitions' in edge['domain']:
                    data[edge['name']] = [p['name'] for p in edge['domain']['partitions']]

        if 'header' in result:
            data.insert(0, result['header'])

        return fmt(data), url
