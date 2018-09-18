"""
This is currently broken.

.. code-block:: bash

    adr intermittent_tests
"""
from __future__ import print_function, absolute_import

from ..cli import RecipeParser
from ..query import run_query


def run(args):
    parser = RecipeParser('date')
    parser.add_argument('-b', '--branch', default=['mozilla-inbound'],
                        help="Branches to query results from.")
    parser.add_argument('-c', '--build_type', default='opt',
                        help="build configuration, default is 'opt'.")
    parser.add_argument('-p', '--platform', default='windows10-64',
                        help="build configuration, default is 'windows10-64'.")
    args = parser.parse_args(args)

    # These 4 args are defined so that we can share the queries with the
    # 'intermittent_test_data' recipe.
    args.test = '(~(file.*|http.*))'
    args.groupby = 'result.test'
    args.result = ["F"]
    args.platform_config = "test-%s/%s" % (args.platform, args.build_type)

    result = []
    query_args = vars(args)

    jobs = next(run_query('intermittent_jobs', **query_args))['data']
    result = next(run_query('intermittent_tests', **query_args))['data']
    total_runs = next(run_query('intermittent_test_rate', **query_args))['data']

    intermittent_tests = []
    # for each result, match up the revision/name with jobs, if a match, save testname
    index = -1
    for item in result['result.test']:
        index += 1
        rev = result['repo.changeset.id12'][index]
        jobname = result['run.key'][index]
        if rev not in jobs['repo.changeset.id12']:
            continue

        index = jobs['repo.changeset.id12'].index(rev)

        if jobname != jobs['job.type.name'][index]:
            continue

        intermittent_tests.append(item)

    result = []
    for test in total_runs:
        if test[1] == 0:
            continue

        if test[0] in intermittent_tests:
            result.append(test)

    result.insert(0, ['Testname', 'Failures', 'Runs'])
    return result
