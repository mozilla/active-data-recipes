from __future__ import print_function, absolute_import

import logging
import os

import requests

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
    data = response.json()["data"]
    return data


def run_query(query, **kwargs):
    for path in os.listdir(QUERY_DIR):
        name = os.path.splitext(path)[0]
        if query != name:
            continue

        with open(os.path.join(QUERY_DIR, path)) as fh:
            query = fh.read()

        query = query % kwargs
        return query_activedata(query)

    log.error("query '{}' not found".format(query))
