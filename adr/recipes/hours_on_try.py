from __future__ import print_function, absolute_import

from argparse import ArgumentParser
from ..query import run_query


def run(args):
    parser = ArgumentParser()
    parser.add_argument('--from-date', default='today-week',
                        help="Starting date to pull data from, defaults to a week ago")
    parser.add_argument('--to-date', default='today',
                        help="Ending date to pull data from, defaults to today")
    parser.add_argument('--max-duration', dest='max_task_duration', default='18000',
                        help="Maximum task duration to consider (in seconds. Defaults "
                             "to 18000 seconds.")
    args = parser.parse_args(args)

    query_args = vars(args)
    query_args['branch_name'] = 'try'

    return run_query('total_hours_spent_on_branch', **kwargs)
