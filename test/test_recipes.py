from __future__ import print_function, absolute_import

import json
import sys
from imp import reload
from io import BytesIO, StringIO

import pytest
import yaml

from adr import query
from adr.cli import run_recipe
from adr.util.config import Configuration
import os

if sys.version_info > (3, 0):
    IO = StringIO
else:
    IO = BytesIO

here = os.path.abspath(os.path.dirname(__file__))


class new_run_query(object):
    def __init__(self, test):
        self.test = test
        self.index = 0

    def __call__(self, query, *args, **kwargs):
        if len(self.test['queries']) <= self.index:
            pytest.fail("not enough mocked query data found in '{}.test'".format(
                        self.test['recipe']))

        result = self.test['queries'][self.index]
        self.index += 1
        return result


def test_recipe(monkeypatch, recipe_test):
    monkeypatch.setattr(query, 'query_activedata', new_run_query(recipe_test))
    config = Configuration()
    config.fmt = "json"
    module = 'adr.recipes.{}'.format(recipe_test['recipe'])
    if module in sys.modules:
        reload(sys.modules[module])

    result = json.loads(run_recipe(recipe_test['recipe'], recipe_test['args'], config))

    buf = IO()
    yaml.dump(result, buf)
    print("Yaml formatted result for copy/paste:")
    print(buf.getvalue())

    buf = IO()
    yaml.dump(recipe_test['expected'], buf)
    print("\nYaml formatted expected:")
    print(buf.getvalue())
    assert result == recipe_test['expected']
