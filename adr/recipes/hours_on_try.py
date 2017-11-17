from __future__ import print_function, absolute_import

from ..cli import RecipeParser
from ..query import run_query


def run(args):
    parser = RecipeParser('date')
    parser.add_argument('--max-duration', dest='max_task_duration', type=int, default=18000,
                        help="Maximum task duration to consider (in seconds. Defaults "
                             "to 18000 seconds.")
    args = parser.parse_args(args)

    query_args = vars(args)
    query_args['branch_name'] = 'try'

    data = next(run_query('total_hours_spent_on_branch', **query_args))['data']
    data['hours'] = int(data['hours'])
    return data
