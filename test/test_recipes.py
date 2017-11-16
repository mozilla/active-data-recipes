from __future__ import print_function, absolute_import

import os

import pytest
import yaml

from adr import query
from adr.main import run_recipe
from adr.query import load_query

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


@pytest.fixture(autouse=True)
def mock_run_query(monkeypatch):

    def _run_query(query, *args, **kwargs):
        output = load_query(query)
        if len(output) < 2:
            pytest.skip('no sample data found')
        return output[1]

    monkeypatch.setattr(query, 'run_query', _run_query)


@pytest.mark.parametrize('recipe', RECIPES.keys())
def test_recipe(recipe):
    run_recipe(recipe, RECIPES[recipe])
