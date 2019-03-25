"""
Show CI regressions per config per week

.. code-block:: bash

    adr unique_failures [-B <branch>] [--from <date> [--to <date>]]
"""

from __future__ import absolute_import, print_function

import logging
from datetime import date, timedelta

from adr.query import run_query

log = logging.getLogger('adr')
BRANCH_WHITELIST = [
    'mozilla-inbound',
    'autoland'
]


def get_stats_for_week(args):
    # query all jobs that are fixed by commit- build a map and determine for each regression:
    # <fixed_rev>: [{<broken_rev>: "time_from_build_to_job", "job_name">}, ...]
    backouts = run_query('fixed_by_commit_jobs', args)['data']
    if backouts == {}:
        return []
    builddate = backouts['build.date']
    jobname = backouts['job.type.name']
    jobdate = backouts['action.request_time']
    buildrev = backouts['build.revision12']
    fixedrev = backouts['failure.notes.text']
    branch = backouts['repo.branch.name']
    fbc = {}
    if len(builddate) != len(fixedrev) != len(buildrev) != len(jobname) != len(jobdate):
        print("invalid length detected in the data found")

    counter = -1
    configs = []
    for item in fixedrev:
        counter += 1
        if counter > len(fixedrev):
            break
        if item is None:
            continue

        if 'try' in branch[counter]:
            continue
        if 'mozilla-esr60' in branch[counter]:
            continue
        if 'mozilla-release' in branch[counter]:
            continue

        if not jobname[counter].startswith('test'):
            continue

        item = item[0:12]

        # TODO: this is hacky, it can get out of date and my shorthand is sloppy
        # parse: test-macosx64/opt-mochitest-browser-chrome-e10s-5
        config = '-'.join(jobname[counter].split('-')[1:])
        config = config.split('/')[0]
        other = jobname[counter].split('/')[1]
        config = "%s/%s" % (config, other.split('-')[0])
        config = config.replace('macosx64', 'OSX')
        config = config.replace('windows7-32', 'Win7')
        config = config.replace('windows10-64', 'Win10')
        config = config.replace('android-em-4.3-arm7-api-16', 'Android4.3')
        config = config.replace('android-hw-p2-8-0-arm7-api-16', 'Pixel2')
        config = config.replace('android-hw-p2-8-0-android-aarch64', 'Pixel2-64')
        config = config.replace('devedition', 'dev')
        config = config.replace('nightly', 'n')
        config = config.replace('android-em-4.2-x86', 'Android4.2')
        config = config.replace('android-em-7.0-x86', 'Android7.0')
        config = config.replace('android-hw-g5-7-0-arm7-api-16', 'G5')
        config = config.replace('linux', 'Lin')

        if config not in configs:
            configs.append(config)

        # sometimes we have a list and some items are None
        if isinstance(item, list):
            i = None
            iter = 0
            while i is None and iter < len(item):
                i = item[iter]
                iter += 1
            if i is None:
                continue
            item = i

        item = item[0:12]
        if item not in fbc:
            fbc[item] = {'revisions': [], 'branch': {}}

        fbc[item]['revisions'].append(buildrev[counter])

        b = branch[counter]
        if b not in fbc[item]['branch']:
            fbc[item]['branch'][b] = {}
        if config not in fbc[item]['branch'][b]:
            fbc[item]['branch'][b][config] = []
        fbc[item]['branch'][b][config].append(jobname[counter])

    configs.sort()

    results = []
    for item in fbc:
        branches = list(fbc[item]['branch'])
        configs = fbc[item]['branch'][branches[0]]
        for c in configs:
            total = 1 if len(configs[c]) > 0 else 0
            # assume same test fails, not multiple tests and we disable the one failing test
            unique = 1 if (sum([len(configs[x]) for x in configs]) - len(configs[c])) == 0 else 0
            results.append([c, total, unique])
    return results, configs


def run(args):
    # Between these dates on a particular branch
    to_date = args.to_date
    if to_date == 'eod':
        to_date = str(date.today())
    to_date = to_date.split('-')

    from_date = args.from_date
    if from_date == 'today-week':
        from_date = str(date.today())
    from_date = from_date.split('-')

    branch = args.branches

    if not branch or branch == ['mozilla-central']:
        branch = BRANCH_WHITELIST

    args.branches = branch

    start = date(int(from_date[0]), int(from_date[1]), int(from_date[2]))
    end = date(int(to_date[0]), int(to_date[1]), int(to_date[2]))
    day = start + timedelta(days=(6 - start.weekday()))
    day -= timedelta(days=7)
    results = []
    configs = []
    raw = {}
    while day < end:
        args.from_date = str(day)
        day += timedelta(days=7)
        args.to_date = str(day)
        retVal, c = get_stats_for_week(args)
        for x in c:
            if x not in configs:
                configs.append(x)
        raw[args.from_date] = retVal

    # this is a table of all regressions seen per config
    header = ['config']
    for d in raw.keys():
        header.append(d)
    configs.sort()
    for c in configs:
        res = []
        res.append(c)
        for d in raw.keys():
            res.append(sum([x[1] for x in raw[d] if x[0] == c]))
        results.append(res)

    # repeat now for just the unique regressions
    results.append(header)
    for c in configs:
        res = []
        res.append(c)
        for d in raw.keys():
            res.append(sum([x[2] for x in raw[d] if x[0] == c]))
        results.append(res)

    results.insert(0, header)
    return results
