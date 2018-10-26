.. ActiveData Recipes documentation master file, created by
   sphinx-quickstart on Thu Sep 13 10:32:04 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ActiveData Recipes
==================

ActiveData_ is a data warehouse operated by Mozilla. It ingests data from a large variety of sources
(including CI, Bugzilla, Mercurial + more) and contains many billions of records. The size and
variety of sources in ActiveData have created several issues; it is both difficult to create raw
ActiveData queries and interpret the results that get returned. Additionally, it was often difficult
(or impossible) to answer our desired questions using a single query. We'd often want to
cross-reference data from many queries at once, post-process the results and output them to a
variety of different formats. These are problems the built-in ActiveData `query tool`_ is not capable
of solving.

The ``active-data-recipes`` project (or ``adr`` for short) was created to help solve some of these
problems. It is a repository of ``queries`` and ``recipes`` that can be run on the command line and
shared with others.

A ``query`` represents a raw ActiveData query with some optional context interpolation (i.e we may
want to change which branch a query will use). Queries live in the ``adr/queries`` directory, have a
``.query`` extension and are typically written in YAML. They will be converted to JSON before being
sent to the ActiveData endpoint. Queries can be run directly with ``adr-query <query name>``.

A ``recipe`` is a Python script that does a few things:

    1. Creates a context (either from user input or default values)
    2. Runs one or more queries (first substituting in the context)
    3. Post process the results
    4. Print the results to the terminal

Recipes live in the ``adr/recipes`` directory. Individual recipes can have their own command line
argument parser with custom arguments. These arguments will typically be used to populate the
context, but can also be used in the post-processing step. Recipes can be run with ``adr <recipe
name> [arguments]``. You can see the help for a recipe by running ``adr <recipe name> -- --help``.


.. _ActiveData: https://github.com/mozilla/ActiveData/blob/dev/docs/GettingStarted.md
.. _query tool: https://activedata.allizom.org/tools/query.html

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   recipes



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
