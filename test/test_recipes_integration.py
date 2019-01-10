import os
import subprocess
import json
from pytest import mark, xfail
from adr.recipe import is_fail

TEST_CASES = [
    "activedata_usage",
    "backout_rate",
    "code_coverage --path caps --rev 45715ece25fc",
    "code_coverage_by_suite --path caps --rev 45715ece25fc",
    "config_durations",
    "files_with_coverage",
    "intermittent_tests",
    "intermittent_test_data",
    "raw_coverage --path caps --rev 45715ece25fc",
    "test_durations",
    "tests_config_times -t test-windows10-64/opt-awsy-e10s",
    "tests_in_duration",
    "try_efficiency",
    "try_usage",
    "try_users",
]


@mark.skipif(os.getenv("TRAVIS_EVENT_TYPE") != "cron", reason="Not run by cron job")
@mark.parametrize("recipe_name", TEST_CASES)
def test_recipe_integration(recipe_name):
    command = ['adr', '--format', 'json']
    command.extend(recipe_name.split(" "))
    try:
        data = subprocess.check_output(command, stderr=subprocess.STDOUT)
        result = json.loads(data)
        assert result
        assert len(result)
    except Exception as e:
        if is_fail(command[3]):
            xfail(str(e))
        else:
            raise e
