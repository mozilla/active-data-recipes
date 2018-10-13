from __future__ import print_function, absolute_import

import json
import sys
from imp import reload
from io import BytesIO, StringIO

import pytest
import yaml

from adr import formatter
from adr.query import format_query, run_query, query_activedata
from adr.util.config import Configuration

if sys.version_info > (3, 0):
    IO = StringIO
else:
    IO = BytesIO

@pytest.fixture
def config():
    congif = Configuration()
    config.debug = False
    config.fmt = 'json'
    config.url = "http://activedata.allizom.org/query"
    return config

def test_query(query_test, config):
    module = 'adr.queries.{}'.format(query_test['query'])
    if module in sys.modules:
        reload(sys.modules[module])

    result = json.loads(format_query(query_test['query'], config))
    #Line 33 - having trouble converting format to json as in terminal the 
    #following error appears:
    #TypeError: expected string or buffer
    #It could be because config is an object? Not sure how to resolve...
    
    buf = IO()
    yaml.dump(result, buf)
    print("Yaml formatted result for copy/paste:")
    print(buf.getvalue())

    buf = IO()
    yaml.dump(query_test['expected'], buf)
    print("\nYaml formatted expected:")
    print(buf.getvalue())
    assert result == query_test['expected']