"""
The command returns the
list of failure tests of a push based on push id. To see the columns in a table, run:

.. code-block:: bash

    adr push_failure --pushid id
"""

from adr.query import run_query


def run(args):
    # TODO: extract revision and repo from treeherder link and return failure test
    push_failure = run_query('push_failure', args)['data']
    return push_failure
