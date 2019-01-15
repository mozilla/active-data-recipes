import pytest
import sys
from imp import reload
import yaml
import json

from adr import query
from app.app import app
from urllib.parse import urlencode
from adr.recipe import get_recipe_contexts

from io import BytesIO, StringIO
if sys.version_info > (3, 0):
    IO = StringIO
else:
    IO = BytesIO


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


API_URL = "http://127.0.0.1:5000/api/v1/{}?{}"
client = app.test_client()


def build_api_url(recipe_test):
    """
    Build api url from test case and default value of context
    :param recipe_test:
    :return: url_string (str)
    """
    args = recipe_test["args"]
    # Get definition of all contexts
    recipe_context_def = get_recipe_contexts(recipe_test["recipe"])
    recipe_args = {}

    # convert cli form to context form
    for key, value in recipe_context_def.items():
        for name in value[0]:
            try:
                index = args.index(name)
                recipe_args.setdefault(key, args[index + 1])
            except ValueError:
                pass

    url_string = API_URL.format(recipe_test["recipe"], urlencode(recipe_args))
    return url_string


def test_api(monkeypatch, recipe_test):
    monkeypatch.setattr(query, 'query_activedata', new_run_query(recipe_test))
    module = 'adr.recipes.{}'.format(recipe_test['recipe'])
    if module in sys.modules:
        reload(sys.modules[module])

    response = client.get(build_api_url(recipe_test))

    assert response.status_code == 200
    assert response.is_json

    result = json.loads(response.data)
    buf = IO()
    yaml.dump(result, buf)
    print("Yaml formatted result for copy/paste:")
    print(buf.getvalue())

    buf = IO()
    yaml.dump(recipe_test['expected'], buf)
    print("\nYaml formatted expected:")
    print(buf.getvalue())
    assert result == recipe_test['expected']
