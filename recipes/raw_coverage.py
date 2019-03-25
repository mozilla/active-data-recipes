"""
This is currently broken.

.. code-block:: bash

    adr raw_coverage
"""
from __future__ import absolute_import, print_function

import copy
import json
import logging
import os

from adr.context import RequestParser
from adr.query import run_query

OUTPUTFILE_PREFIX = 'coverage_map'
log = logging.getLogger('adr')
BROKEN = True


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


def run(config, args):
    parser = RequestParser('path', 'rev')
    parser.add_argument('--use-chunks', default=False, action="store_true",
                        help="use chunks in aggregating and reporting jobs.")
    parser.add_argument('--no-perf', default=False, action="store_true",
                        help="Ignore performance tests in aggregating and reporting jobs.")
    args = parser.parse_args(args)

    def artifactCount(args):
        query_args = vars(args)
        result = run_query('raw_coverage_count', config, **query_args)
        for item in result['data']:
            return item[0]

    def buildDirList(dirs):
        dirs.sort()
        all_dirs = {}
        last_dir = ''
        for line in dirs:
            line = line.strip()
            if not line.endswith('/'):
                line = "%s/" % line
            if line == '/':
                continue

            args.path = line
            count = int(artifactCount(args))
            if count <= 0:
                continue

            if last_dir and line.startswith(last_dir) or line == last_dir:
                continue

            if line in all_dirs:
                continue

            # check if the parent is already in the dir list
            if '/'.join(line.split('/')[0:-1]) in all_dirs:
                continue

            if count < 50000:
                all_dirs[line] = count
                last_dir = line
            else:
                newdirs = []
                for d in dirs:
                    if d.startswith(line):
                        newdirs.append(d)

                if line in newdirs:
                    del newdirs[newdirs.index(line)]

                if newdirs:
                    sub_dirs = buildDirList(newdirs)
                    for sd in sub_dirs:
                        all_dirs[sd] = sub_dirs[sd]
                    last_dir = sd
                else:
                    all_dirs[line] = count
                    last_dir = line

        log.debug("original list of directories: %s" % len(dirs))
        log.debug("reduced set of directories: %s" % len(all_dirs.keys()))
        return all_dirs

    def minimumJobs(args, expected_count=0):
        query_args = vars(args)

        if expected_count >= 50000:
            result = run_query('raw_coverage_nosubdir', config, **query_args)
        else:
            result = run_query('raw_coverage', config, **query_args)

        # format is: {sourcename: {lines: {}, suites: []}, sourcename: ...}
        retVal = {}

        # this will be 1+ files, and 1+ suites, need to support that
        if expected_count and len(result['data']) != expected_count:
            log.debug("  Missing data for path: %s: %s != %s" %
                      (args.path, len(result['data']), expected_count))
        for suite in result['data']:
            sourcename = suite[0]['file']['name']
            if sourcename not in retVal:
                # data for SETA style unique coverage
                retVal[sourcename] = {'lines': {}, 'suites': []}

            fname = suite[1]['fullname']
            jobname = fname
            if args.use_chunks:
                chunk = suite[2].split('/')[-1]
                chunk = chunk.split('-')[-1]
                jobname = '%s-%s' % (fname, chunk)

            if args.no_perf:
                if fname in ['talos', 'awsy']:
                    continue

            lines = retVal[sourcename]['lines']
            suites = retVal[sourcename]['suites']
            # Prep data for reducing total jobs
            if isinstance(suite[0]['file']['covered'], int):
                suite[0]['file']['covered'] = [suite[0]['file']['covered']]

            for line in suite[0]['file']['covered']:
                if line not in lines:
                    lines[line] = []
                if jobname not in lines[line]:  # handle the case of !args.use_chunks
                    lines[line].append(jobname)
            suites.append(jobname)

        # SETA style discovery of important suites
        # NOTE: this will be biased based on the order we evaluate suites
        # (currently alpha_num sorted) jobs at the top of the list will be
        # removed first
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

        with open('%s_%s.json' % (OUTPUTFILE_PREFIX, args.path.replace('/', '_')), 'w') as f:
            json.dump(jsonOutput, f)

        return output, jsonOutput

    # Main code
    if os.path.isfile(args.path):
        merged_data = {}
        with open(args.path, 'r') as f:
            data = f.read()
        dirs = data.split('\n')
        all_dirs = buildDirList(dirs)

        for dir in all_dirs:
            args.path = dir
            log.debug("generating coverage for: %s" % args.path)

            output, jsonOutput = minimumJobs(args, all_dirs[dir])
            for filename in jsonOutput:
                merged_data[filename] = jsonOutput[filename]

        with open('%s.json' % (OUTPUTFILE_PREFIX), 'wb') as f:
            json.dump(merged_data, f)
        return []
    else:
        output, jsonOutput = minimumJobs(args)
        return output
