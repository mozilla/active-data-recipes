import json
import os
import sys
from imp import reload
from io import StringIO
from pathlib import Path

import pytest
import yaml
from requests import Response
from requests.exceptions import HTTPError

import adr

here = Path(__file__).parent.resolve()


def load_recipe_tests():
    recipe_dir = os.path.join(here, 'recipe_tests')
    recipes = [os.path.join(recipe_dir, r) for r in os.listdir(recipe_dir) if r.endswith('.test')]
    for recipe in recipes:
        with open(recipe, 'r') as fh:
            for test in yaml.load_all(fh, Loader=yaml.FullLoader):
                yield test


def load_query_tests():
    query_dir = os.path.join(here, 'query_tests')
    queries = [os.path.join(query_dir, q) for q in os.listdir(query_dir) if q.endswith('.test')]
    for query in queries:
        with open(query, 'r') as fh:
            for test in yaml.load_all(fh, Loader=yaml.FullLoader):
                yield test


def load_formatter_tests(format):
    formatter_dir = os.path.join(here, 'formatter_tests')
    json_formatter_tests = [os.path.join(formatter_dir, j) for j in os.listdir(
        formatter_dir) if j.endswith('.test') and j.startswith(format)]
    for json_formatter_test in json_formatter_tests:
        with open(json_formatter_test, 'r') as fh:
            for test in yaml.load_all(fh, Loader=yaml.FullLoader):
                yield test


def recipe_idfn(val):
    return '{} {}'.format(val['recipe'], ' '.join(val['args'])).strip()


def query_idfn(val):
    return '{} {}'.format(val['query'], ' '.join(val['args'])).strip()


def formatter_idfn(val):
    return '{} {}'.format(val['format'], ' '.join(val['args'])).strip()


def pytest_generate_tests(metafunc):
    if 'recipe_test' in metafunc.fixturenames:
        metafunc.parametrize('recipe_test', list(load_recipe_tests()), ids=recipe_idfn)
    if 'query_test' in metafunc.fixturenames:
        metafunc.parametrize('query_test', list(load_query_tests()), ids=query_idfn)
    if 'json_formatter_test' in metafunc.fixturenames:
        metafunc.parametrize(
            'json_formatter_test',
            list(
                load_formatter_tests('json_')),
            ids=formatter_idfn)
    if 'tab_formatter_test' in metafunc.fixturenames:
        metafunc.parametrize(
            'tab_formatter_test',
            list(
                load_formatter_tests('tab_')),
            ids=formatter_idfn)
    if 'table_formatter_test' in metafunc.fixturenames:
        metafunc.parametrize(
            'table_formatter_test',
            list(
                load_formatter_tests('table_')),
            ids=formatter_idfn)


@pytest.fixture
def set_config():
    config = adr.configuration.Configuration(path=here / 'config.toml')

    def inner(**other):
        config.merge(other)

        adr_modules = [mod for name, mod in sys.modules.items()
                       if name.startswith('adr') or name.startswith('app')
                       if name != 'adr.configuration']

        for source in adr.sources:
            adr_modules.extend([mod for name, mod in sys.modules.items()
                                if name.startswith(source.recipe_dir.name)])

        adr.configuration.config = config
        for mod in adr_modules:
            reload(mod)

    return inner


@pytest.fixture
def patch_active_data(monkeypatch):
    class MockQueryRunner(object):
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

    def patch(recipe_test):
        monkeypatch.setattr(adr.query, 'query_activedata',
                            MockQueryRunner(recipe_test))
        module = 'adr.recipes.{}'.format(recipe_test['recipe'])
        if module in sys.modules:
            reload(sys.modules[module])

    return patch


@pytest.fixture
def patch_active_data_exception(monkeypatch):
    class ExceptionQueryRunner(object):
        def __init__(self, exception):
            self.response = Response()
            self.response.status_code = 400
            content = json.dumps({
                'cause': {
                    'cause': {
                        'template': exception
                    }
                }
            })
            self.response._content = content

        def __call__(self, query, *args, **kwargs):
            raise HTTPError(response=self.response)

    def patch(recipe_test, exception):
        monkeypatch.setattr(adr.query, 'query_activedata',
                            ExceptionQueryRunner(exception))
        module = 'adr.recipes.{}'.format(recipe_test['recipe'])
        if module in sys.modules:
            reload(sys.modules[module])
            reload(sys.modules[module])

    return patch


@pytest.fixture
def validate():
    def do_validate(recipe_test, actual):
        buf = StringIO()
        yaml.dump(actual, buf)
        print("Yaml formatted result for copy/paste:")
        print(buf.getvalue())

        buf = StringIO()
        yaml.dump(recipe_test['expected'], buf)
        print("\nYaml formatted expected:")
        print(buf.getvalue())
        assert actual == recipe_test['expected']

    return do_validate
