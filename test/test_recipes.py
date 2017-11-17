from __future__ import print_function, absolute_import

import json
import os

import pytest
import yaml

from adr import query
from adr.main import run_recipe

here = os.path.abspath(os.path.dirname(__file__))

RECIPES = {
    'backout_rate': [],
    'code_coverage': ['--rev', '123456789abc', '--path', 'foo'],
    'code_coverage_by_suite': ['--rev', '123456789abc', '--path', 'foo'],
    'files_with_coverage': [],
    'hours_on_try': [],
    'inspect': [],
    'raw_coverage': ['--rev', '123456789abc', '--path', 'foo'],
    'task_durations': [],
    'try_usage': [],
    'try_users': [],
}


def test_recipe(monkeypatch, recipe_test):

    def _run_query(query, *args, **kwargs):
        if query not in recipe_test['queries']:
            pytest.fail("no test data found for query '{}' in '{}.test'".format(
                        query, recipe_test['recipe']))
        for result in recipe_test['queries'][query]:
            yield result

    monkeypatch.setattr(query, 'run_query', _run_query)

    result = json.loads(run_recipe(recipe_test['recipe'], recipe_test['args'], fmt='json'))
    print("Copy/paste result:")
    print(result)
    assert result == recipe_test['expected']
