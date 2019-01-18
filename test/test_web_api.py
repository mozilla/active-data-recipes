import pytest

import json
from app import app
from urllib.parse import urlencode
from adr.recipe import get_recipe_contexts


@pytest.fixture
def api_host():
    # Flask default localhost at port 5000
    return "http://127.0.0.1:5000"


@pytest.fixture
def api_url_func(api_host):
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
        url_string = "{}{}{}?{}".format(api_host, app.API_BASE_PATH,
                                        recipe_test["recipe"], urlencode(recipe_args))
        return url_string

    return build_api_url


@pytest.fixture
def client():
    return app.app.test_client()


def test_api(patch_active_data, api_url_func, client, recipe_test, validate):
    patch_active_data(recipe_test)

    url = api_url_func(recipe_test)
    response = client.get(url)

    assert response.status_code == 200
    assert response.is_json

    actual = json.loads(response.data)
    validate(recipe_test, actual)
