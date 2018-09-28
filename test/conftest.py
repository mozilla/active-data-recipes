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


def idfn(val):
    return '{} {}'.format(val['recipe'], ' '.join(val['args'])).strip()


def pytest_generate_tests(metafunc):
    if 'recipe_test' in metafunc.fixturenames:
        metafunc.parametrize('recipe_test', list(load_recipe_tests()), ids=idfn)
