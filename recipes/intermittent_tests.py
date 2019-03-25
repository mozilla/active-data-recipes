"""
This is currently broken.

.. code-block:: bash

    adr intermittent_tests
"""
from __future__ import absolute_import, print_function

from adr.context import override
from adr.query import run_query

BROKEN = True
RUN_CONTEXTS = [override('platform_config', hidden=True)]


def run(args):
    # These 4 args are defined so that we can share the queries with the
    # 'intermittent_test_data' recipe.
    args.test_name = '(~(file.*|http.*))'
    args.groupby = 'result.test'
    args.result = ["F"]
    args.platform_config = "test-%s/%s" % (args.platform, args.build_type)

    jobs = run_query('intermittent_jobs', args)['data']
    result = run_query('intermittent_tests', args)['data']
    total_runs = run_query('intermittent_test_rate', args)['data']

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
