from __future__ import print_function, absolute_import

import datetime
import json
import logging
import os
import sys
from argparse import ArgumentParser

import jsone
import requests
import yaml
from six import string_types

from .formatter import all_formatters
from .main import log

here = os.path.abspath(os.path.dirname(__file__))

ACTIVE_DATA_URL = 'http://activedata.allizom.org/query'
QUERY_DIR = os.path.join(here, 'queries')


def query_activedata(query):
    response = requests.post(ACTIVE_DATA_URL,
                             data=query,
                             stream=True)
    response.raise_for_status()
    return response.json()


def load_query(name):
    found = False
    for path in os.listdir(QUERY_DIR):
        query = os.path.splitext(path)[0]
        if name != query:
            continue

        found = True
        with open(os.path.join(QUERY_DIR, path)) as fh:
            for query in yaml.load_all(fh):
                yield query

    if not found:
        log.error("query '{}' not found".format(name))


def run_query(name, **context):
    for query in load_query(name):
        # If limit is in the context, override the queries' value. We do this
        # to keep the results down to a sane level when testing queries.
        if 'limit' in context:
            query['limit'] = context['limit']
        query = jsone.render(query, context)
        query_str = json.dumps(query, indent=2, separators=(',', ':'))
        log.debug("Running query {}:\n{}".format(name, query_str))
        yield query_activedata(query_str)


def format_date(timestamp, interval='day'):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')


def cli(args=sys.argv[1:]):
    parser = ArgumentParser()
    parser.add_argument('query', nargs='?', help="Query to run.")
    parser.add_argument('-l', '--list', action='store_true', default=False,
                        help="List available queries.")
    parser.add_argument('-f', '--format', dest='fmt', default='table',
                        choices=all_formatters.keys(),
                        help="Format to print data in, defaults to 'table'.")
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="Print the query and other debugging information.")

    args, remainder = parser.parse_known_args(args)
    if args.list:
        queries = [os.path.splitext(q)[0] for q in os.listdir(QUERY_DIR)]
        log.info('\n'.join(sorted(queries)))
        return

    if args.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    # Fake the context for convenience
    fake_context = {
        'branch': 'mozilla-central',
        'from_date': 'now-week',
        'to_date': 'now',
        'rev': '5b33b070378a',
        'path': 'dom/indexedDB',
        'limit': 10,
    }

    if isinstance(args.fmt, string_types):
        fmt = all_formatters[args.fmt]

    for result in run_query(args.query, **fake_context):
        data = result['data']

        if args.fmt == 'json':
            print(fmt(result))
            return

        if 'edges' in result:
            for edge in result['edges']:
                data[edge['name']] = [p['name'] for p in edge['domain']['partitions']]

        if 'header' in result:
            data.insert(0, result['header'])

        print(fmt(data))


if __name__ == '__main__':
    sys.exit(cli())
