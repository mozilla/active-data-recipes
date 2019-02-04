"""
Compare subtest performance across all suites for two revisions

.. code-block:: bash

    adr perf_tp6_compare -r <revision1> -r <revision2> [-t <subtest>]

<subtest> defaults to "-loadtime"

"""

from __future__ import absolute_import, print_function

import logging

from ..query import run_query

log = logging.getLogger("adr")

RUN_CONTEXTS = [
    {"rev1": [["--r1", "--rev1"], {"type": str, "help": "Revision to compare"}]},
    {"rev2": [["--r2", "--rev2"], {"type": str, "help": "Revision to compare"}]},
    {"subtest": [["-t", "--test", "--subtest"], {"type": str, "default": "-loadtime", "help": "the subtest name (or suffix)"}]},
]


def run(config, args):

    result = run_query("perf_tp6_compare", config, args)

    tests, revisions = result['edges']
    header = ["Subtest"] + [p['name'] for p in revisions['domain']['partitions']]

    data = list(
        [n] + v
        for n, v in zip(
            [p['name'] for p in tests['domain']['partitions']],
            result['data']['result.stats.median']
        )
    )

    data.insert(0, header)
    return data
