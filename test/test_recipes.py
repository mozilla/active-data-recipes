from __future__ import absolute_import, print_function

import json
import os

from adr.cli import run_recipe
from adr.util.config import Configuration

here = os.path.abspath(os.path.dirname(__file__))


def test_recipe(patch_active_data, recipe_test, validate):
    patch_active_data(recipe_test)

    config = Configuration()
    config.fmt = "json"
    result = json.loads(run_recipe(recipe_test['recipe'], recipe_test['args'], config))

    validate(recipe_test, result)
