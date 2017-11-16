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
    parser = ArgumentParser()
    parser.add_argument('gist_config', nargs='?', default=DEFAULT_CONFIG,
                        help='Path to yaml config file.')
    parser.add_argument('--gist', default='gist',
                        help='Path to the gist binary.')
    args = parser.parse_args(args)

    gist = find_executable('gist')
    if not gist:
        log.error("gist not installed!")
        return 1

    with open(args.gist_config, 'r') as fh:
        config = yaml.load(fh)

    output = None
    for recipe in config['recipes']:
        recipe_args = config['recipes'][recipe]
        table = run_recipe(recipe, recipe_args, fmt='markdown', quiet=True)

        filename = '{}.md'.format(recipe.replace('_', '-'))
        cmd = [
            'gist',
            '-f', filename,
        ]

        if 'gist' in config:
            cmd.extend(['-u', config['gist']])
        else:
            log.info("no 'gist' key defined, creating new gist")

        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.stdin.write(table)
        output = proc.communicate()[0].strip()
        log.info("updated {}".format(recipe))

        if 'gist' not in config:
            create_new = False
            config['gist'] = output.rsplit('/', 1)[1]
            with open(args.gist_config, 'w') as fh:
                fh.write(yaml.dump(config))

    if output:
        log.info(output)


if __name__ == '__main__':
    sys.exit(cli())
