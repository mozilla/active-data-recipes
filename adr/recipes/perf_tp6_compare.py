"""
Compare subtest performance across all suites for two revisions

.. code-block:: bash

    adr perf_tp6_compare -r1 <revision1> -r2 <revision2> [-t <subtest>]

<subtest> defaults to "-loadtime"

"""

from __future__ import absolute_import, print_function

import logging

from ..query import run_query

log = logging.getLogger("adr")

RUN_CONTEXTS = [
    {"rev1": [["--r1", "--rev1"], {"type": str, "help": "Revision to compare"}]},
    {"rev2": [["--r2", "--rev2"], {"type": str, "help": "Revision to compare"}]},
    {
        "subtest": [
            ["-t", "--test", "--subtest"],
            {
                "type": str,
                "default": "-loadtime",
                "help": "the subtest name (or suffix)",
            },
        ]
    },
]


def run(config, args):

    result = run_query("perf_tp6_compare", config, args)

    tests, revisions = result["edges"]
    header = (
        ["Subtest"]
        + [p["name"] for p in revisions["domain"]["partitions"]]
        + ["Change"]
    )
    test_names = [p["name"] for p in tests["domain"]["partitions"]]
    values = result["data"]["result.stats.median"]

    data = list(
        [n] + [round(v) if v is not None else None for v in row] + [change(*row)]
        for n, row in zip(test_names, values)
    )

    data.insert(0, header)
    return data


def change(r1, r2):
    try:
        value = round((1 - r2 / r1) * 100)
        if value >= 0:
            return " " + str(value) + "%"
        else:
            return str(value) + "%"
    except Exception:
        return ""
