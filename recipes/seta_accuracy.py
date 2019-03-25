"""
Show CI regressions found and SETA miss rate by week

.. code-block:: bash

    adr seta_accuracy [-B <branch>] [--from <date> [--to <date>]]
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
    fbc = {}
    if len(builddate) != len(fixedrev) != len(buildrev) != len(jobname) != len(jobdate):
        print("invalid length detected in the data found")

    counter = -1
    for item in fixedrev:
        counter += 1
        if counter > len(fixedrev):
            break
        if item is None:
            continue

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
            fbc[item] = {}

        if buildrev[counter] not in fbc[item]:
            fbc[item][buildrev[counter]] = False
        # 300 seconds is a magic number, represents lag between
        # build finished and test job scheduled
        if (jobdate[counter] - builddate[counter]) < 300:
            fbc[item][buildrev[counter]] = True

    results = []
    for item in fbc:
        failed = [x for x in fbc[item] if not fbc[item][x]]
        passfail = "pass"
        if len(failed):
            passfail = "fail"
        results.append([item, passfail])
    return results


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

    if not args.branches or args.branches == ['mozilla-central']:
        args.branches = BRANCH_WHITELIST

    start = date(int(from_date[0]), int(from_date[1]), int(from_date[2]))
    end = date(int(to_date[0]), int(to_date[1]), int(to_date[2]))
    day = start + timedelta(days=(6 - start.weekday()))
    day -= timedelta(days=7)
    results = []
    while day < end:
        args.from_date = str(day)
        day += timedelta(days=7)
        args.to_date = str(day)
        retVal = get_stats_for_week(args)
        results.append([args.from_date,
                        len(retVal),
                        len([x for x in retVal if x[1] == 'fail'])])

    header = ['week of', '# regressions', '# seta missed']
    results.insert(0, header)
    return results
