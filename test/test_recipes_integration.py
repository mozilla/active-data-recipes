import os
import subprocess
import json
from pytest import mark, param

TEST_CASES = [
    "activedata_usage",
    "backout_rate",
    param("code_coverage --path caps --rev 45715ece25fc", marks=mark.xfail),
    "code_coverage_by_suite --path caps --rev 45715ece25fc",
    "config_durations",
    "files_with_coverage",
    "intermittent_tests",
    "intermittent_test_data",
    param("raw_coverage --path caps --rev 45715ece25fc", marks=mark.xfail),
    "test_durations",
    param("tests_config_times -t test-windows10-64/opt-awsy-e10s", marks=mark.xfail),
    "tests_in_duration",
    "try_efficiency",
    "try_usage",
    param("try_users", marks=mark.xfail),
]


@mark.skipif(os.getenv("TRAVIS_EVENT_TYPE") != "cron", reason="Not run by cron job")
@mark.parametrize("recipe", TEST_CASES)
def test_recipe_integration(recipe):
    command = ['adr', '--format', 'json']
    command.extend(recipe.split(" "))
    data = subprocess.check_output(command, stderr=subprocess.STDOUT)
    result = json.loads(data)
    assert result
    assert len(result)
