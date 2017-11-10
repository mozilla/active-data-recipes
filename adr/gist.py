from __future__ import print_function, absolute_import

import logging
import os
import subprocess
import sys
from argparse import ArgumentParser
from distutils.spawn import find_executable

import yaml

from .main import run_recipe

log = logging.getLogger('adr')
DEFAULT_CONFIG = os.path.expanduser(os.path.join('~', '.adr-gist.yml'))


def cli(args=sys.argv[1:]):
    gist = find_executable('gist')
    if not gist:
        log.error("gist not installed!")
        return 1

    parser = ArgumentParser()
    parser.add_argument('gist_config', nargs='?', default=DEFAULT_CONFIG,
                        help='Path to yaml config file.')
    args = parser.parse_args(args)

    with open(args.gist_config, 'r') as fh:
        config = yaml.load(fh)

    for recipe in config['recipes']:
        args = config['recipes'][recipe]
        table = run_recipe(recipe, args, fmt='markdown', quiet=True)

        filename = '{}.md'.format(recipe.replace('_', '-'))
        cmd = [
            'gist',
            '-u', config['gist'],
            '-f', filename,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.stdin.write(table)
        output = proc.communicate()[0]


if __name__ == '__main__':
    sys.exit(cli())
