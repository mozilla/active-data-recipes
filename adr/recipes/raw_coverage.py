from __future__ import print_function, absolute_import

from argparse import ArgumentParser

from ..query import run_query

import copy
import json


def removeJob(lines, jobname):
    # TODO: do we need a deep copy here?
    temp_lines = copy.copy(lines)
    retVal = copy.copy(lines)
    for line in temp_lines:
        if jobname not in temp_lines[line]:
            continue

        temp_lines[line].remove(jobname)
        if len(temp_lines[line]) == 0:
            del retVal[line]

    return retVal
    
def taskclusterName(jobname):
    # output data to .json file, create format like: test-linux64/debug-<jobname>
    # todo, there are a lot of exceptions.
    return "test-linux64/debug-%s" % jobname

def run(args):
    parser = ArgumentParser()
    parser.add_argument('--path', required=True,
                        help="Source code path to show summary coverage stats for.")
    parser.add_argument('--rev', required=True,
                        help="Revision to collect coverage data at.")
    args = parser.parse_args(args)
    query_args = vars(args)

    result = run_query('raw_coverage', **query_args)

    # format is: {sourcename: {lines: {}, suites: [], jobdata: {}, sourcename: ...}
    retVal = {}

    # this will be 1+ files, and 1+ suites, need to support that
    for suite in result['data']:
        sourcename = suite[0]['file']['name']
        if sourcename not in retVal:
            # data for SETA style unique coverage
            retVal[sourcename] = {'lines': {}, 'suites': [], 'jobdata': {}}

        fname = suite[1]['fullname']
        chunk = suite[2].split('/')[-1]
        chunk = chunk.split('-')[-1]
        jobname = '%s-%s' % (fname, chunk)

        #TODO: we might not need 'jobdata', only used for printing covered filees
        retVal[sourcename]['jobdata'][jobname] = [suite[0]['file']['total_covered'], suite[0]['file']['total_uncovered']]

        lines = retVal[sourcename]['lines']
        suites = retVal[sourcename]['suites']
        # Prep data for reducing total jobs
        if type(suite[0]['file']['covered']) == type(1):
            suite[0]['file']['covered'] = [suite[0]['file']['covered']]

        for line in suite[0]['file']['covered']:
            if line not in lines:
                lines[line] = []
            lines[line].append(jobname)
        suites.append(jobname)


    # SETA style discovery of important suites
    # NOTE: this will be biased based on the order we evaluate suites (currently alpha_num sorted)
    #       jobs at the top of the list will be removed first
    jsonOutput = {}
    for sourcename in retVal:
        lines = retVal[sourcename]['lines']
        suites = retVal[sourcename]['suites']

        uniqueSuites = []
        suites.sort(reverse=True)
        for suite in suites:
            tlines = removeJob(lines, suite)
            if len(tlines.items()) != len(lines.items()):
                uniqueSuites.append(suite)
            else:
                lines = tlines

        retVal[sourcename]['uniqueSuites'] = uniqueSuites
        jsonOutput[sourcename] = [taskclusterName(x) for x in uniqueSuites]

    output = [[args.path, 'minimum jobs']]
    for sourcename in retVal:
        output.append([sourcename, retVal[sourcename]['uniqueSuites']])

    with open('coverage_map_%s.json' % args.path.replace('/', '_'), 'w') as f:
         json.dump(jsonOutput, f)

    return output
