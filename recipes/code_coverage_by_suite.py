"""
Get code coverage information for the given `path` at `rev` aggregated by suite.
Both arguments are required.

.. code-block:: bash

    adr code_coverage_by_suite --path <path> --rev <rev>
"""
from __future__ import absolute_import, print_function

from adr.query import run_query


def run(args):
    """
    THIS IS PRONE TO DOUBLE COUNTING, AS DIFFERENT TEST CHUNKS COVER COMMON LINES
    AT THE VERY LEAST YOU GET A ROUGH ESTIMATE OF COVERAGE
    """

    all_suites = [
        'gtest',
        'marionette',
        'mochitest-plain',
        'mochitest-browser-chrome',
        'mochitest-devtools-chrome',
        'mochitest-chrome',
        'mochitest-a11y',
        'mochitest-gl',
        'mochitest-gpu',
        'mochitest-clipboard',
        'mochitest-media',
        'talos',
        'reftest',
        'reftest-no-accel',
        'reftest-crashtest',
        'reftest-jsreftest',
        'xpcshell',
        'web-platform-tests',
        'firefox-ui-functional local',
        'firefox-ui-functional remote',
        'awsy',
        'cppunittest',
        'jittest',
        'web-platform-tests-wdspec',
        'web-platform-tests-reftests',
    ]
    all_suites_name = ['gtest', 'Mn', 'm', 'bc', 'dt', 'c', 'a11y', 'gl', 'gpu', 'cl', 'mda',
                       'T', 'R', 'Ru', 'C', 'J', 'X', 'wpt', 'fx-l', 'fx-r', 'awsy', 'cpp',
                       'jit', 'Wd', 'Wr']

    retVal = {}
    result = run_query('code_coverage_by_suite', args)
    for line in result['data']:
        # line = [suite, filename, count]
        if line[1] not in retVal:
            retVal[line[1]] = {}
        retVal[line[1]][line[0]] = line[2]

    output = [['path']]
    output[0].extend(all_suites_name)
    counter = 1
    for path in retVal:
        if not path:
            continue

        output.append([])
        output[counter].append(path)
        for suite in all_suites:
            if suite not in retVal[path]:
                output[counter].append('')
            elif retVal[path][suite] is None:
                output[counter].append('')
            else:
                output[counter].append(retVal[path][suite])
        counter += 1

    return output
