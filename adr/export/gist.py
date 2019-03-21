from __future__ import absolute_import, print_function

import logging
import os
import subprocess
import sys
from argparse import ArgumentParser
from distutils.spawn import find_executable

import yaml

from ..cli import log, run_recipe
from ..util.config import Configuration

DEFAULT_CONFIG = os.path.expanduser(os.path.join('~', '.adr-gist.yml'))


def cli(args=sys.argv[1:]):
    parser = ArgumentParser()
    parser.add_argument('gist_config', nargs='?', default=DEFAULT_CONFIG,
                        help='Path to yaml config file.')
    parser.add_argument('--gist', default='gist',
                        help='Path to the gist binary.')
    args = parser.parse_args(args)

    log.setLevel(logging.INFO)

    gist = find_executable(args.gist)
    if not gist:
        log.error("gist not installed!")
        return 1

    with open(args.gist_config, 'r') as fh:
        config = yaml.load(fh, Loader=yaml.SafeLoader)

    output = None
    cfg = Configuration()
    cfg.format = 'markdown'
    for recipe in config['recipes']:
        recipe_args = config['recipes'][recipe]
        table = bytes(run_recipe(recipe, recipe_args, cfg), 'utf8')

        filename = '{}.md'.format(recipe.replace('_', '-'))
        cmd = [
            gist,
            '-f', filename,
        ]

        if 'gist' in config:
            cmd.extend(['-u', config['gist']])
        else:
            log.info("no 'gist' key defined, creating new gist")

        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output = proc.communicate(input=table)[0].strip()
        log.info("updated {}".format(recipe))

        if 'gist' not in config:
            config['gist'] = output.rsplit('/', 1)[1]
            with open(args.gist_config, 'w') as fh:
                fh.write(yaml.dump(config))

    if output:
        log.info(output)


if __name__ == '__main__':
    sys.exit(cli())
