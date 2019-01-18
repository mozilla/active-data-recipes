from adr import query
import pytest
import sys
from imp import reload
import yaml
from io import StringIO


@pytest.fixture
def patch_active_data(monkeypatch):
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

    def patch(recipe_test):
        monkeypatch.setattr(query, 'query_activedata',
                            new_run_query(recipe_test))
        module = 'adr.recipes.{}'.format(recipe_test['recipe'])
        if module in sys.modules:
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
