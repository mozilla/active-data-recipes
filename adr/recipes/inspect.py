from __future__ import print_function, absolute_import

from argparse import ArgumentParser
from collections import defaultdict

from ..query import run_query


def run(args):
    parser = ArgumentParser()
    parser.add_argument('--table', default=None,
                        help="Table to inspect.")
    args = parser.parse_args(args)

    if not args.table:
        data = next(run_query('meta'))['data']
        data = sorted([(d['name'],) for d in data])
        data.insert(0, ('Table',))
        return data

    data = next(run_query('meta_columns', table=args.table))['data']
    data = sorted([(d['name'],) for d in data])
    data.insert(0, ('Column',))
    return data
