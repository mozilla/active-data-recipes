"""
Get skipped tests on the ActiveData schema. The above command returns the
test suites and their count which were skipped/disabled between specified period. Run:
.. code-block:: bash
    adr skipped_tests
"""
from __future__ import print_function, absolute_import

from ..query import run_query
from argparse import ArgumentParser

all_suites = ["mochitest-browser-chrome-instrumentation",
              "web-platform-tests-reftests",
              "mochitest-devtools-chrome",
              "mochitest-browser-chrome",
              "mochitest-valgrind-plain",
              "mochitest-webgl1-core",
              "mochitest-webgl2-core",
              "mochitest-webgl1-ext",
              "mochitest-webgl2-ext",
              "mochitest-clipboard",
              "web-platform-tests",
              "reftest-jsreftest",
              "reftest-crashtest",
              "reftest-no-accel",
              "mochitest-chrome",
              "mochitest-media",
              "mochitest-plain",
              "mochitest-a11y",
              "mochitest-gpu",
              "reftest-gpu",
              "test-verify",
              "marionette",
              "xpcshell",
              "reftest"]

all_platforms = ["linux64",
                 "linux32",
                 "maxosx64",
                 "android",
                 "win64",
                 "win32"]


def run(args, config):
    parser = ArgumentParser()
    parser.add_argument('--from', default='today', dest='from_date',
                        help="Starting date to pull data from,"
                        + " defaults to the beginning of today in GMT.")
    parser.add_argument('--to', default='eod', dest='to_date',
                        help="Ending date to pull data from, defaults to end of the day")
    parser.add_argument('--limit', type=int, default=100, dest='limit',
                        help="Maximum number of tests to return")
    parser.add_argument('--suite', default=all_suites, dest='suite',
                        help="Select suite to get skipped tests from." +
                        "By default, gets data from all suites.")
    parser.add_argument('--platform', default=all_platforms, dest='platform',
                        help="Select platform to get skipped tests from." +
                        "By default, gets information about tests across all platforms.")
    args = parser.parse_args(args)
    query_args = vars(args)
    result = next(run_query('skipped_tests', config, **query_args))['data']
    result.insert(0, ['Result test', 'run suite', 'count'])
    return result
