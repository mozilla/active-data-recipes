from __future__ import print_function, absolute_import

import datetime
import json
import logging
import os

import jsone
import requests
import yaml

here = os.path.abspath(os.path.dirname(__file__))
log = logging.getLogger('adr')

ACTIVE_DATA_URL = 'http://activedata.allizom.org/query'
QUERY_DIR = os.path.join(here, 'queries')


def query_activedata(query):
    log.debug("Running query:\n{}".format(query))
    response = requests.post(ACTIVE_DATA_URL,
                             data=query,
                             stream=True)
    response.raise_for_status()
    return response.json()


def load_query(name):
    for path in os.listdir(QUERY_DIR):
        query = os.path.splitext(path)[0]
        if name != query:
            continue

        with open(os.path.join(QUERY_DIR, path)) as fh:
            return list(yaml.load_all(fh))

    log.error("query '{}' not found".format(query))


def run_query(name, **context):
    query = load_query(name)[0]
    query = jsone.render(query, context)
    query_str = json.dumps(query, indent=2, separators=(',', ':'))
    return query_activedata(query_str)


def format_date(timestamp, interval='day'):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
