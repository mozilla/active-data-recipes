from __future__ import print_function, absolute_import

import os

import yaml

here = os.path.abspath(os.path.dirname(__file__))


def load_recipe_tests():
    recipe_dir = os.path.join(here, 'recipe_tests')
    recipes = [os.path.join(recipe_dir, r) for r in os.listdir(recipe_dir) if r.endswith('.test')]
    for recipe in recipes:
        with open(recipe, 'r') as fh:
            for test in yaml.load_all(fh):
                yield test


def load_query_tests():
    query_dir = os.path.join(here, 'query_tests')
    queries = [os.path.join(query_dir, q) for q in os.listdir(query_dir) if q.endswith('.test')]
    for query in queries:
        with open(query, 'r') as fh:
            for test in yaml.load_all(fh):
                yield test


def load_formatter_tests(format):
    formatter_dir = os.path.join(here, 'formatter_tests')
    json_formatter_tests = [os.path.join(formatter_dir, j) for j in os.listdir(
        formatter_dir) if j.endswith('.test') and j.startswith(format)]
    for json_formatter_test in json_formatter_tests:
        with open(json_formatter_test, 'r') as fh:
            for test in yaml.load_all(fh):
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
