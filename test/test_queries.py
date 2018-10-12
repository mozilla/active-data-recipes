from __future__ import print_function, absolute_import

import json
import sys
from imp import reload
from io import BytesIO, StringIO

import pytest
import yaml

from argparse import Namespace

from adr import formatter
from adr.query import format_query, run_query, query_activedata

if sys.version_info > (3, 0):
    IO = StringIO
else:
    IO = BytesIO

@pytest.fixture
def args():
	args = Namespace()
	args.debug = 'debug'
	args.fmt = 'fmt'
	return args

def test_query(query_test, args):

    module = 'adr.queries.{}'.format(query_test['query'])
    if module in sys.modules:
        reload(sys.modules[module])

    result = json.loads(format_query(query_test['query'], args, fmt='json'))
    #line 35 - having trouble converting format as JSON expects a string or buffer
    #and args is a namespace object
    
    buf = IO()
    yaml.dump(result, buf)
    print("Yaml formatted result for copy/paste:")
    print(buf.getvalue())

    buf = IO()
    yaml.dump(query_test['expected'], buf)
    print("\nYaml formatted expected:")
    print(buf.getvalue())
    assert result == query_test['expected']