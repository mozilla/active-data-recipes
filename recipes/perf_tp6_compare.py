"""
Compare subtest performance across all suites for two revisions

.. code-block:: bash

    adr perf_tp6_compare -r1 <revision1> -r2 <revision2> [-t <subtest>]

<subtest> defaults to "-loadtime"

"""

from __future__ import absolute_import, print_function

from adr.query import run_query


def run(args):

    result = run_query("perf_tp6_compare", args)

    tests, revisions = result["edges"]
    header = (
        ["Test", "Subtest"]
        + [p["name"] for p in revisions["domain"]["partitions"]]
        + ["Change"]
    )
    suites, tests = zip(*(p["value"] for p in tests["domain"]["partitions"]))
    values = result["data"]["result.stats.median"]

    data = list(
        [s, scrub_suite(s, t)] + [round(v) if v is not None else None for v in row] + [change(*row)]
        for s, t, row in zip(suites, tests, values)
    )

    data.insert(0, header)
    return data


def scrub_suite(s, t):
    if t.startswith(s):
        return t[len(s):].lstrip("-")
    else:
        return t


def change(r1, r2):
    try:
        value = round((1 - r2 / r1) * 100)
        if value >= 0:
            return " " + str(value) + "%"
        else:
            return str(value) + "%"
    except Exception:
        return ""
