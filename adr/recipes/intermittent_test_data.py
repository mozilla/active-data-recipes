"""
This is currently broken.

.. code-block:: bash

    adr intermittent_test_data
"""
from __future__ import print_function, absolute_import

from ..recipe import execute_query


def run(args):

    if args.test_name == '':
        platform_config = "test-%s/%s" % (args.platform, args.build_type)
        new_context = {'test_name': '(~(file.*|http.*))', 'platform_config': platform_config}
    else:
        test_name = '.*%s.*' % args.test_name
        new_context = {'test_name': test_name, 'platform_config': "test-",
                       'groupby': 'run.key', 'result': ["T", "F"]}

    result = execute_query('intermittent_tests', new_context)['data']
    total_runs = execute_query('intermittent_test_rate', new_context)['data']

    intermittent_tests = []
    for item in result['run.key']:
        parts = item.split('/')
        config = "%s/%s" % (parts[0], parts[1].split('-')[0])
        if config not in intermittent_tests:
            intermittent_tests.append(config)

    retVal = {}
    for test in total_runs:
        parts = test[0].split('/')
        config = "%s/%s" % (parts[0], parts[1].split('-')[0])
        if config in intermittent_tests:
            if config not in retVal:
                retVal[config] = [test[1], test[2]]
            else:
                retVal[config][0] += test[1]
                retVal[config][1] += test[2]

    result = []
    for item in retVal:
        val = [item]
        val.extend(retVal[item])
        result.append(val)
    result.insert(0, ['Config', 'Failures', 'Runs'])
    return result
