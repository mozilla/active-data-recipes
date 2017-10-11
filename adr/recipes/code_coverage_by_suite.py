from __future__ import print_function, absolute_import

from argparse import ArgumentParser

from ..query import run_query


def run(args):
    """
    THIS IS PRONE TO DOUBLE COUNTING, AS DIFFERENT TEST CHUNKS COVER COMMON LINES
    AT THE VERY LEAST YOU GET A ROUGH ESTIMATE OF COVERAGE
    """
    parser = ArgumentParser()
    parser.add_argument('--path', required=True,
                        help="Source code path to show summary coverage stats for.")
    parser.add_argument('--rev', required=True,
                        help="Revision to collect coverage data at.")
    parser.add_argument('--suite', required=False, default="",
                        help="Revision to collect coverage data at.")
    args = parser.parse_args(args)
    query_args = vars(args)

    #TODO: cppunit, jittest
    all_suites = ['gtest', 'marionette', 'mochitest', 'talos', 'reftest', 'xpcshell', 'web-platform-tests', 'firefox-ui', 'awsy']
    suites = all_suites
    if args.suite:
        suites = [args.suite]

    retVal = {}
    for suite in suites:
        query_args['suite'] = suite
        result = run_query('code_coverage_by_suite', **query_args)
        output = [result['header']]+result['data']
        for line in result['data']:
            if line[0] not in retVal:
                retVal[line[0]] = []
            retVal[line[0]].append(str(line[1]))

    temp = ['path']
    temp.extend(suites)
    output = [temp]
    for item in retVal:
        temp = [item]
        temp.extend(retVal[item])
        output.append(temp)
    return output
