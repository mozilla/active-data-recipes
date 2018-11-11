"""
Get the average and total runtime for build platforms and types.

.. code-block:: bash

    adr config_durations [--branch <branch>]
"""
from __future__ import print_function, absolute_import
from adr.util.modified_docopt import docopt
from ..query import run_query


argument_parser = """
    Argument parser for the config_durations recipe.

    Usage:
    config_durations [--limit LIMIT] [--sort-key SORTKEY]

    Options:
    --limit=LIMIT  Maximum number of jobs to return. [default: 50]
    --sort-key=SORTKEY  Key to sort on (int, 0-based index). [default: 4]
    """


def run(args, config):

    limit = int(docopt(argument_parser, args)['--limit'])
    sort_key = int(docopt(argument_parser, args)['--sort-key'])

    data = next(run_query('config_durations', config, *args))['data']

    result = []
    for record in data:
        if isinstance(record[1], list):
            record[1] = record[1][-1]
        if record[2] is None:
            continue
        if record[3] is None:
            continue
        record[3] = round(record[3] / 60, 2)
        record.append(int(round(record[2] * record[3], 0)))
        result.append(record)

    result = sorted(result, key=lambda k: k[sort_key], reverse=True)[:limit]
    result.insert(0, ['Platform', 'Type', 'Num Jobs', 'Average Hours', 'Total Hours'])
    return result
