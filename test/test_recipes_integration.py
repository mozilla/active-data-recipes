import pytest
import os
import subprocess
import json

# Each test with recipe and appropriate parameters in one line
# Using bracket annotation to set it optional (xfail)
TEST_CASES = [
    "activedata_usage",
    ["backout_rate"],
    ["code_coverage --path caps --rev 45715ece25fc"],
    "code_coverage_by_suite --path caps --rev 45715ece25fc",
    "config_durations",
    "files_with_coverage",
    ["intermittent_tests"],
    ["intermittent_test_data"],
    ["raw_coverage --path caps --rev 45715ece25fc"],
    "test_durations",
    ["tests_config_times -t test-windows10-64/opt-awsy-e10s"],
    ["tests_in_duration"],
    ["try_efficiency"],
    ["try_usage"],
    ["try_users"]
]


def load_tests(tests):
    return [pytest.param(test[0], marks=pytest.mark.xfail)
            if isinstance(test, list)
            else test
            for test in tests]


@pytest.mark.skipif(os.getenv("TRAVIS_EVENT_TYPE") != "cron", reason="Not run by cron job")
@pytest.mark.parametrize("recipe", load_tests(TEST_CASES))
def test_recipe_integration(recipe):
    command = ['adr', '--format', 'json']
    command.extend(recipe.split(" "))
    data = subprocess.check_output(command, stderr=subprocess.STDOUT)
    result = json.loads(data)
    assert result
    assert len(result)
